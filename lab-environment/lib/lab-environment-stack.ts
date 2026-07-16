import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';

/**
 * Owner account for the official Debian AMIs. Debian publishes AMIs under this
 * AWS account; filtering by owner (rather than a hardcoded AMI ID) is what keeps
 * the app portable across regions and accounts.
 */
const DEBIAN_AMI_OWNER = '136693071363';

/**
 * SSM public parameter that always resolves to the latest Windows Server 2025
 * (English, Full/Desktop) base AMI in the deploying region. Resolved at deploy
 * time by CloudFormation, so it is region-correct for whoever deploys.
 */
const WINDOWS_2025_SSM_PARAM =
  '/aws/service/ami-windows-latest/Windows_Server-2025-English-Full-Base';

export interface LabEnvironmentStackProps extends cdk.StackProps {
  /** EC2 instance type for both hosts. Default: c7i.xlarge (4 vCPU / 8 GiB). */
  readonly instanceType?: string;
  /** Root volume size in GiB for both hosts. Default: 150. */
  readonly diskGiB?: number;
}

/**
 * Disposable lab: one Debian 13 host and one Windows Server 2025 host, both
 * x86_64, in a dedicated minimal VPC. Designed to be deployed and torn down
 * frequently, and to be portable to any account/region with no code edits.
 *
 * Access is via AWS Systems Manager (Session Manager / RunCommand): both hosts
 * carry the SSM core permissions, and Debian installs the SSM agent at boot, so
 * there are no inbound ports and no SSH keys.
 *
 * Both hosts are provisioned experiment-ready at boot via user data, so a fresh
 * deploy only needs the release bundle fetched and run:
 *   - Debian installs the substrate runtimes the primitives dynamically link
 *     (musl loader, libc++), tmon's runtime deps, and the AWS CLI.
 *   - Windows excludes the release directory from Defender, disables (and, where
 *     the Server feature allows, removes) Defender to keep it from perturbing
 *     ETW or contending for resources, and installs the AWS CLI.
 * A disposable, in-stack S3 bucket carries release bundles in and raw/processed
 * data out; both host roles can read/write it. It is destroyed with the stack,
 * so pull processed outputs down before teardown.
 */
export class LabEnvironmentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: LabEnvironmentStackProps = {}) {
    super(scope, id, props);

    const instanceType = props.instanceType ?? 'c7i.xlarge';
    const diskGiB = props.diskGiB ?? 150;

    cdk.Tags.of(this).add('Project', 'telemetry-lab');
    cdk.Tags.of(this).add('Component', 'lab-environment');
    cdk.Tags.of(this).add('ManagedBy', 'cdk');

    // Disposable data bucket: release bundles in (releases/), raw + processed
    // telemetry out (raw/<os>/, tap-results/). Ephemeral by design -- it is
    // emptied and destroyed with the stack, matching the throwaway lab, so
    // pull any processed outputs down before `cdk destroy`.
    const dataBucket = new s3.Bucket(this, 'LabData', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // Dedicated, minimal VPC: public subnets + internet gateway, NO NAT gateway.
    // Public subnets give each host a direct, free egress path to the internet
    // and S3; a NAT gateway would add ~$32/mo for no benefit here. The VPC is
    // created and destroyed with the stack, so `cdk destroy` leaves nothing
    // behind, and it never depends on the account's default VPC existing.
    const vpc = new ec2.Vpc(this, 'LabVpc', {
      maxAzs: 2,
      natGateways: 0,
      subnetConfiguration: [
        { name: 'public', subnetType: ec2.SubnetType.PUBLIC, cidrMask: 24 },
      ],
    });

    // Egress-only posture is enforced by the security group, not the subnet: all
    // outbound allowed, zero inbound rules. Each host gets its own security
    // group with no rules referencing the other, so the two instances cannot
    // reach each other. A public IP without any inbound rule is not reachable.
    const egressOnlySecurityGroup = (constructId: string, name: string) =>
      new ec2.SecurityGroup(this, constructId, {
        vpc,
        description: `Lab host (${name}): egress only, no inbound`,
        allowAllOutbound: true,
      });

    const rootVolume = () =>
      ec2.BlockDeviceVolume.ebs(diskGiB, {
        volumeType: ec2.EbsDeviceVolumeType.GP3,
        deleteOnTermination: true,
        encrypted: true,
      });

    // Windows Server ships the SSM agent; the official Debian AMI does not, so
    // install it at boot from the region's SSM agent bucket (egress is provided
    // by the public subnet). The region is concrete here because the AMI lookup
    // below requires an explicit env, so the URL interpolation is safe.
    const debianUserData = ec2.UserData.forLinux();
    debianUserData.addCommands(
      'set -eux',
      'export DEBIAN_FRONTEND=noninteractive',
      'apt-get update -y',
      'apt-get install -y curl',
      `curl -fsSL -o /tmp/amazon-ssm-agent.deb "https://s3.${this.region}.amazonaws.com/amazon-ssm-${this.region}/latest/debian_amd64/amazon-ssm-agent.deb"`,
      'dpkg -i /tmp/amazon-ssm-agent.deb',
      'systemctl enable --now amazon-ssm-agent',
      // Provision the substrate runtimes the primitives dynamically link, so
      // every config runs on a fresh host with no manual setup: `musl` supplies
      // the musl loader (linux-c-musl); `libc++1 libc++abi1 libunwind8` supply
      // the LLVM C++ runtime (linux-cpp-libcxx). libelf1/zlib1g/libzstd1 are
      // tmon's dynamic deps. awscli + tar/gzip/xz stage bundles and move data.
      'apt-get install -y --no-install-recommends ' +
        'musl libc++1 libc++abi1 libunwind8 ' +
        'libelf1 zlib1g libzstd1 ' +
        'awscli tar gzip xz-utils ca-certificates',
    );

    // Debian 13 (trixie), x86_64 -- matches the debian:trixie container used in
    // CI, so the libc substrate is identical. AMI resolved by owner + name
    // filter (never a hardcoded ID), so it is correct in any region.
    const debian = new ec2.Instance(this, 'DebianHost', {
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      instanceType: new ec2.InstanceType(instanceType),
      machineImage: ec2.MachineImage.lookup({
        name: 'debian-13-amd64-*',
        owners: [DEBIAN_AMI_OWNER],
        filters: {
          architecture: ['x86_64'],
          'root-device-type': ['ebs'],
          'virtualization-type': ['hvm'],
          state: ['available'],
        },
      }),
      securityGroup: egressOnlySecurityGroup('DebianSecurityGroup', 'debian-13'),
      blockDevices: [{ deviceName: '/dev/xvda', volume: rootVolume() }],
      userData: debianUserData,
      requireImdsv2: true,
    });
    cdk.Tags.of(debian).add('Name', 'lab-debian-13');

    // Windows provisioning, in order:
    //   1. Create the release dir C:\lab and exclude it from Defender FIRST, so
    //      nothing downloaded into it is scanned/quarantined even in the window
    //      before Defender is disabled.
    //   2. Disable Defender broadly -- this is a detection-centric telemetry
    //      study, so Defender is a confound (it can delay/quarantine primitives
    //      and perturb ETW). Then remove the Server feature entirely so MsMpEng
    //      does not run at all (no scan noise, no resource contention); a
    //      feature removal needs a reboot, taken as the last step. Set-MpPreference
    //      may be reverted if Tamper Protection is on, so the removal is the
    //      durable path; both are attempted and verified post-deploy.
    //   3. Install the AWS CLI for moving bundles/data to and from S3.
    const windowsUserData = ec2.UserData.forWindows();
    windowsUserData.addCommands(
      'New-Item -ItemType Directory -Force -Path C:\\lab | Out-Null',
      "try { Add-MpPreference -ExclusionPath 'C:\\lab' -ErrorAction Stop } catch {}",
      'try {',
      '  Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction Stop',
      '  Set-MpPreference -DisableBehaviorMonitoring $true',
      '  Set-MpPreference -DisableIOAVProtection $true',
      '  Set-MpPreference -DisableScriptScanning $true',
      '  Set-MpPreference -DisableArchiveScanning $true',
      '  Set-MpPreference -MAPSReporting Disabled -SubmitSamplesConsent NeverSend',
      '  Set-MpPreference -PUAProtection Disabled',
      '} catch {}',
      "try { New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Force | Out-Null; " +
        "Set-ItemProperty 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System' -Name 'SmartScreenEnabled' -Value 'Off' } catch {}",
      '$msi = "$env:TEMP\\AWSCLIV2.msi"',
      "Invoke-WebRequest -Uri 'https://awscli.amazonaws.com/AWSCLIV2.msi' -OutFile $msi -UseBasicParsing",
      'Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /qn" -Wait',
      // Remove Defender entirely; reboot only if the feature removal asks for it.
      '$rm = $null',
      'try { $rm = Uninstall-WindowsFeature -Name Windows-Defender -ErrorAction Stop } catch {}',
      "if ($rm -and $rm.RestartNeeded -eq 'Yes') { Restart-Computer -Force }",
    );

    // Windows Server 2025, x86_64 -- matches the windows-2025 CI runner, so the
    // UCRT/MSVCRT runtimes and ETW behavior match. AMI resolved via SSM public
    // parameter at deploy time, so it is region-correct and always current.
    const windows = new ec2.Instance(this, 'WindowsHost', {
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      instanceType: new ec2.InstanceType(instanceType),
      machineImage: ec2.MachineImage.fromSsmParameter(WINDOWS_2025_SSM_PARAM, {
        os: ec2.OperatingSystemType.WINDOWS,
      }),
      securityGroup: egressOnlySecurityGroup('WindowsSecurityGroup', 'windows-2025'),
      blockDevices: [{ deviceName: '/dev/sda1', volume: rootVolume() }],
      userData: windowsUserData,
      requireImdsv2: true,
    });
    cdk.Tags.of(windows).add('Name', 'lab-windows-2025');

    // Grant both hosts the SSM core permissions so Session Manager / RunCommand
    // work explicitly, rather than relying on the account's Default Host
    // Management Configuration being enabled. The ec2.Instance construct creates
    // each host's role, exposed as `.role`.
    for (const host of [debian, windows]) {
      host.role.addManagedPolicy(
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      );
      // Both hosts move release bundles and telemetry through the data bucket.
      dataBucket.grantReadWrite(host.role);
    }

    new cdk.CfnOutput(this, 'Region', { value: this.region });
    new cdk.CfnOutput(this, 'DebianInstanceId', { value: debian.instanceId });
    new cdk.CfnOutput(this, 'WindowsInstanceId', { value: windows.instanceId });
    new cdk.CfnOutput(this, 'DataBucketName', { value: dataBucket.bucketName });
  }
}
