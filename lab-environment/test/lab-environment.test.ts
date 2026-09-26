import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { LabEnvironmentStack } from '../lib/lab-environment-stack';

function synth() {
  const app = new cdk.App();
  const stack = new LabEnvironmentStack(app, 'TestStack', {
    env: { account: '123456789012', region: 'us-west-2' },
  });
  return Template.fromStack(stack);
}

test('one dedicated VPC, no NAT gateway', () => {
  const template = synth();
  template.resourceCountIs('AWS::EC2::VPC', 1);
  template.resourceCountIs('AWS::EC2::NatGateway', 0);
});

test('two EC2 hosts', () => {
  const template = synth();
  template.resourceCountIs('AWS::EC2::Instance', 2);
});

test('security groups open no inbound ports', () => {
  const template = synth();
  // Each host security group is egress-only: it declares no ingress rules.
  const groups = template.findResources('AWS::EC2::SecurityGroup');
  for (const group of Object.values(groups)) {
    const ingress = group.Properties?.SecurityGroupIngress ?? [];
    expect(ingress).toHaveLength(0);
  }
});

test('both hosts get the SSM managed policy', () => {
  const json = JSON.stringify(synth().toJSON());
  const matches = json.match(/AmazonSSMManagedInstanceCore/g) ?? [];
  expect(matches.length).toBeGreaterThanOrEqual(2);
});

test('a single disposable data bucket is created and exported', () => {
  const template = synth();
  template.resourceCountIs('AWS::S3::Bucket', 1);
  // Ephemeral: emptied and removed with the stack.
  template.hasResource('AWS::S3::Bucket', {
    DeletionPolicy: 'Delete',
    UpdateReplacePolicy: 'Delete',
  });
  template.hasOutput('DataBucketName', {});
});

test('both host roles can read and write the data bucket', () => {
  const json = JSON.stringify(synth().toJSON());
  // grantReadWrite emits both Get* and Put* actions in the role policies.
  expect(json).toContain('s3:GetObject');
  expect(json).toContain('s3:PutObject');
});

test('Debian user data installs the substrate runtimes', () => {
  const json = JSON.stringify(synth().toJSON());
  // musl loader and libc++ runtime are the packages the smoke test found missing.
  for (const pkg of ['musl', 'libc++1', 'libc++abi1', 'libunwind8']) {
    expect(json).toContain(pkg);
  }
});

test('Windows user data excludes the release dir then disables Defender', () => {
  const json = JSON.stringify(synth().toJSON());
  expect(json).toContain('Add-MpPreference -ExclusionPath');
  expect(json).toContain('DisableRealtimeMonitoring');
  expect(json).toContain('Uninstall-WindowsFeature -Name Windows-Defender');
});


test('Linux-only validation omits Windows resources and retains SSM and storage', () => {
  const app = new cdk.App();
  const stack = new LabEnvironmentStack(app, 'LinuxOnly', {
    env: { account: '123456789012', region: 'us-west-2' }, linuxOnly: true,
  });
  const template = Template.fromStack(stack);
  template.resourceCountIs('AWS::EC2::Instance', 1);
  template.hasOutput('DebianInstanceId', {});
  template.hasOutput('DataBucketName', {});
  const json = JSON.stringify(template.toJSON());
  expect(json).not.toContain('WindowsInstanceId');
  expect(json).not.toContain('DisableRealtimeMonitoring');
  expect(json).toContain('AmazonSSMManagedInstanceCore');
});


test('Windows-only validation excludes the Debian host', () => {
  const app = new cdk.App();
  const stack = new LabEnvironmentStack(app, 'WindowsTest', {
    env: { account: '123456789012', region: 'us-west-2' }, windowsOnly: true,
  });
  const template = Template.fromStack(stack);
  template.resourceCountIs('AWS::EC2::Instance', 1);
  template.hasOutput('WindowsInstanceId', {});
  expect(template.toJSON().Outputs.DebianInstanceId).toBeUndefined();
});


test('fleet scaling preserves first pair outputs and isolates every host', () => {
  const app = new cdk.App();
  const stack = new LabEnvironmentStack(app, 'Fleet', {
    env: { account: '123456789012', region: 'us-west-2' }, hostPairs: 3,
  });
  const template = Template.fromStack(stack);
  template.resourceCountIs('AWS::EC2::Instance', 6);
  template.resourceCountIs('AWS::EC2::VPC', 1);
  template.hasOutput('DebianInstanceId', {});
  template.hasOutput('WindowsInstanceId03', {});
  for (const group of Object.values(template.findResources('AWS::EC2::SecurityGroup'))) {
    expect(group.Properties?.SecurityGroupIngress ?? []).toHaveLength(0);
  }
});

test.each([0, -1, 1.5, 21, NaN])('invalid fleet size %s is rejected', (hostPairs) => {
  expect(() => new LabEnvironmentStack(new cdk.App(), 'Invalid', {
    env: { account: '123456789012', region: 'us-west-2' }, hostPairs,
  })).toThrow('hostPairs must be an integer');
});


test('bootstrap waits for the first-boot dpkg lock', () => {
  expect(JSON.stringify(synth().toJSON())).toContain('DPkg::Lock::Timeout');
});
