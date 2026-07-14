import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

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
 * Scope of this deliverable is the instance happy path only. The management
 * channel (SSM) and all post-deploy configuration (Windows Defender, toolchains,
 * telemetry dependencies, primitive download) are intentionally deferred.
 */
export class LabEnvironmentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: LabEnvironmentStackProps = {}) {
    super(scope, id, props);

    const instanceType = props.instanceType ?? 'c7i.xlarge';
    const diskGiB = props.diskGiB ?? 150;

    cdk.Tags.of(this).add('Project', 'telemetry-lab');
    cdk.Tags.of(this).add('Component', 'lab-environment');
    cdk.Tags.of(this).add('ManagedBy', 'cdk');

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
      requireImdsv2: true,
    });
    cdk.Tags.of(debian).add('Name', 'lab-debian-13');

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
      requireImdsv2: true,
    });
    cdk.Tags.of(windows).add('Name', 'lab-windows-2025');

    new cdk.CfnOutput(this, 'Region', { value: this.region });
    new cdk.CfnOutput(this, 'DebianInstanceId', { value: debian.instanceId });
    new cdk.CfnOutput(this, 'WindowsInstanceId', { value: windows.instanceId });
  }
}
