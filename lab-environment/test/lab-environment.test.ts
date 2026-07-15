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
