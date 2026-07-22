import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as fs from 'fs';
import * as path from 'path';

/**
 * The host-local self-inventory scripts, embedded (base64) into user data at synth
 * so the authored files under scripts/ stay the single source of truth. Each runs
 * as the last provisioning step on its host and writes inventory.json (versions +
 * SHA-256 + paths) to a deterministic location for tap to discover.
 */
const INVENTORY_LINUX_B64 = Buffer.from(
  fs.readFileSync(path.join(__dirname, '../scripts/inventory-linux.sh')),
).toString('base64');
const INVENTORY_WINDOWS_B64 = Buffer.from(
  fs.readFileSync(path.join(__dirname, '../scripts/inventory-windows.ps1')),
).toString('base64');

/**
 * The constant substrate base image Dockerfile, embedded (base64) at synth. The
 * Debian host builds it once at boot so container detonation of ttp_composites
 * runs every substrate in one identical image (the Option A confound control).
 */
const SUBSTRATE_DOCKERFILE_B64 = Buffer.from(
  fs.readFileSync(path.join(__dirname, '../docker/substrate-base.Dockerfile')),
).toString('base64');

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
      // --- Detection tooling under test: Falco (latest stable) ---
      // Falco is the Linux runtime detector under test. We deliberately consume
      // the LATEST stable release rather than pinning a version, so the lab does
      // not break when the apt repo prunes old versions. Reproducibility is
      // established after the fact by scripts/capture-provenance.sh, which records
      // the exact installed version + binary/rule hashes per deploy.
      // `gnupg` is required to dearmor the repo key and is absent on the minimal
      // Debian AMI. The modern eBPF driver needs no kernel module (kernel BTF).
      'apt-get install -y gnupg',
      'curl -fsSL https://falco.org/repo/falcosecurity-packages.asc ' +
        '| gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg',
      'echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] ' +
        'https://download.falco.org/packages/deb stable main" ' +
        '> /etc/apt/sources.list.d/falcosecurity.list',
      'apt-get update -y',
      'FALCO_FRONTEND=noninteractive FALCO_DRIVER_CHOICE=modern_ebpf ' +
        'apt-get install -y falco',
      // Pull the incubating + sandbox rule feeds too (same corpus as the PoC);
      // non-fatal so a feed hiccup never blocks the deploy.
      'falcoctl index update falcosecurity || true',
      'falcoctl artifact install falco-incubating-rules:latest || true',
      'falcoctl artifact install falco-sandbox-rules:latest || true',
      'systemctl enable falco-modern-bpf.service',
      'systemctl restart falco-modern-bpf.service',
      // --- Lab payload: telemetry-lab release bundle (latest) ---
      // The project's own release (tmon, tap, ttp-primitives, substrate manifests),
      // fetched at its latest tag and extracted under /opt/lab so a fresh host is
      // experiment-ready. The tarball is kept for hashing; inventory.sh derives the
      // version from the extracted directory name and records path + SHA-256.
      'mkdir -p /opt/lab',
      'curl -fsSL https://api.github.com/repos/bluesentinelsec/telemetry-lab/releases/latest -o /opt/lab/release.json',
      'TL_URL=$(grep browser_download_url /opt/lab/release.json | grep linux.tar.gz | cut -d\'"\' -f4)',
      'curl -fsSL -o /opt/lab/telemetry-lab.tar.gz "$TL_URL"',
      'tar -xzf /opt/lab/telemetry-lab.tar.gz -C /opt/lab',
      // --- Container detonation runtime: Docker + constant substrate base image ---
      // ttp_composites detonate in a container (Falco's native deployment). The
      // daemon is standard/rootful (representative; rootless slirp4netns would
      // perturb the network syscall path we measure). The base image is debian:13
      // + all substrate runtimes, held constant across the matrix so it is a fixed
      // offset, not a per-substrate variable. Falco's container plugin (installed
      // above) enriches events with container context so container-scoped rules
      // fire. inventory records the Docker version + base-image digest.
      'apt-get install -y docker.io',
      'systemctl enable --now docker',
      'mkdir -p /opt/lab/base-image',
      `echo ${SUBSTRATE_DOCKERFILE_B64} | base64 -d > /opt/lab/base-image/Dockerfile`,
      'docker build -t lab-substrate:13 /opt/lab/base-image || true',
      // --- Provenance: self-inventory (LAST step, after everything is installed) ---
      // Decode the authored scripts/inventory-linux.sh (embedded at synth) and run it;
      // it writes /opt/lab/inventory.json with versions + SHA-256 + paths. tap reads
      // this file co-located with telemetry data to stamp analysis output.
      `echo ${INVENTORY_LINUX_B64} | base64 -d > /opt/lab/inventory-self.sh`,
      'bash /opt/lab/inventory-self.sh || true',
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
      // --- Detection tooling under test: Sysmon + Hayabusa (latest) ---
      // Installed BEFORE the Defender feature removal below, because that step may
      // reboot and end the user-data script. Both are consumed at their LATEST
      // release (not pinned); scripts/capture-provenance.ps1 records the exact
      // versions + hashes per deploy. Everything lands under C:\lab, which was
      // excluded from Defender first, so nothing is scanned/quarantined.
      'New-Item -ItemType Directory -Force -Path C:\\lab\\sysmon | Out-Null',
      'New-Item -ItemType Directory -Force -Path C:\\lab\\hayabusa | Out-Null',
      // Sysmon (ETW sensor): latest from Sysinternals + a log-all config. The
      // config filters nothing (each event class is onmatch="exclude" with no
      // rules => nothing excluded => everything logged), so Sigma rules see the
      // full event stream and a null result means "robust", not "not captured".
      "Invoke-WebRequest -Uri 'https://download.sysinternals.com/files/Sysmon.zip' -OutFile C:\\lab\\Sysmon.zip -UseBasicParsing",
      'Expand-Archive -Path C:\\lab\\Sysmon.zip -DestinationPath C:\\lab\\sysmon -Force',
      "$cfgB64 = 'PFN5c21vbiBzY2hlbWF2ZXJzaW9uPSI0LjkwIj4KICA8SGFzaEFsZ29yaXRobXM+KjwvSGFzaEFsZ29yaXRobXM+CiAgPEV2ZW50RmlsdGVyaW5nPgogICAgPFByb2Nlc3NDcmVhdGUgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPEZpbGVDcmVhdGVUaW1lIG9ubWF0Y2g9ImV4Y2x1ZGUiLz4KICAgIDxOZXR3b3JrQ29ubmVjdCBvbm1hdGNoPSJleGNsdWRlIi8+CiAgICA8UHJvY2Vzc1Rlcm1pbmF0ZSBvbm1hdGNoPSJleGNsdWRlIi8+CiAgICA8RHJpdmVyTG9hZCBvbm1hdGNoPSJleGNsdWRlIi8+CiAgICA8SW1hZ2VMb2FkIG9ubWF0Y2g9ImV4Y2x1ZGUiLz4KICAgIDxDcmVhdGVSZW1vdGVUaHJlYWQgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPFJhd0FjY2Vzc1JlYWQgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPFByb2Nlc3NBY2Nlc3Mgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPEZpbGVDcmVhdGUgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPFJlZ2lzdHJ5RXZlbnQgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPEZpbGVDcmVhdGVTdHJlYW1IYXNoIG9ubWF0Y2g9ImV4Y2x1ZGUiLz4KICAgIDxQaXBlRXZlbnQgb25tYXRjaD0iZXhjbHVkZSIvPgogICAgPFdtaUV2ZW50IG9ubWF0Y2g9ImV4Y2x1ZGUiLz4KICAgIDxEbnNRdWVyeSBvbm1hdGNoPSJleGNsdWRlIi8+CiAgICA8RmlsZURlbGV0ZSBvbm1hdGNoPSJleGNsdWRlIi8+CiAgICA8Q2xpcGJvYXJkQ2hhbmdlIG9ubWF0Y2g9ImV4Y2x1ZGUiLz4KICAgIDxQcm9jZXNzVGFtcGVyaW5nIG9ubWF0Y2g9ImV4Y2x1ZGUiLz4KICAgIDxGaWxlRGVsZXRlRGV0ZWN0ZWQgb25tYXRjaD0iZXhjbHVkZSIvPgogIDwvRXZlbnRGaWx0ZXJpbmc+CjwvU3lzbW9uPgo='",
      "[IO.File]::WriteAllText('C:\\lab\\sysmon\\config.xml', [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($cfgB64)))",
      '& C:\\lab\\sysmon\\Sysmon64.exe -accepteula -i C:\\lab\\sysmon\\config.xml',
      // Hayabusa (Sigma evaluator): latest win-x64 release asset resolved via the
      // GitHub API, extracted to C:\lab\hayabusa; the release bundles its Sigma
      // ruleset under rules\. Normalize the versioned exe name to hayabusa.exe.
      "$hdr = @{ 'User-Agent' = 'telemetry-lab' }",
      "$rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/Yamato-Security/hayabusa/releases/latest' -Headers $hdr",
      "$asset = $rel.assets | Where-Object { $_.name -like '*-win-x64.zip' -and $_.name -notlike '*live-response*' } | Select-Object -First 1",
      "Invoke-WebRequest -Uri $asset.browser_download_url -OutFile C:\\lab\\hayabusa.zip -UseBasicParsing",
      'Expand-Archive -Path C:\\lab\\hayabusa.zip -DestinationPath C:\\lab\\hayabusa -Force',
      "$hb = Get-ChildItem -Path C:\\lab\\hayabusa -Recurse -Filter 'hayabusa*-win-x64.exe' | Select-Object -First 1",
      "if ($hb) { Copy-Item $hb.FullName C:\\lab\\hayabusa\\hayabusa.exe -Force }",
      // --- Lab payload: telemetry-lab release bundle (latest) ---
      // The project's own release (tmon, tap, ttp-primitives, substrate manifests),
      // fetched at its latest tag and extracted under C:\lab\telemetry-lab so a fresh
      // host is experiment-ready. The zip is kept for hashing; inventory.ps1 derives
      // the version from the extracted directory name and records path + SHA-256.
      "$tl = Invoke-RestMethod -Uri 'https://api.github.com/repos/bluesentinelsec/telemetry-lab/releases/latest' -Headers $hdr",
      "$tla = $tl.assets | Where-Object { $_.name -like '*windows.zip' } | Select-Object -First 1",
      "Invoke-WebRequest -Uri $tla.browser_download_url -OutFile C:\\lab\\telemetry-lab.zip -UseBasicParsing",
      'Expand-Archive -Path C:\\lab\\telemetry-lab.zip -DestinationPath C:\\lab\\telemetry-lab -Force',
      // --- Provenance: self-inventory (LAST step before the reboot, everything installed) ---
      // Decode the authored scripts/inventory-windows.ps1 (embedded at synth) and run
      // it; it writes C:\lab\inventory.json with versions + SHA-256 + paths. tap reads
      // this file co-located with telemetry data to stamp analysis output.
      `$invB64 = '${INVENTORY_WINDOWS_B64}'`,
      "[IO.File]::WriteAllText('C:\\lab\\inventory-self.ps1', [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($invB64)))",
      'powershell -ExecutionPolicy Bypass -File C:\\lab\\inventory-self.ps1',
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
