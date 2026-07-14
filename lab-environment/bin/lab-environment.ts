#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { LabEnvironmentStack } from '../lib/lab-environment-stack';

const app = new cdk.App();

// Region resolution, most specific first:
//   1. `-c region=<r>` on the command line
//   2. the deployer's configured region (CDK_DEFAULT_REGION)
//   3. us-west-2 default
// Account always comes from the deploying credentials, so the app is portable:
// point any account's credentials at it and deploy with no code edits.
const region =
  app.node.tryGetContext('region') ?? process.env.CDK_DEFAULT_REGION ?? 'us-west-2';
const account = process.env.CDK_DEFAULT_ACCOUNT;

const instanceType = app.node.tryGetContext('instanceType');
const diskGiBContext = app.node.tryGetContext('diskGiB');

new LabEnvironmentStack(app, 'LabEnvironmentStack', {
  // A concrete env is required because the Debian AMI is resolved with a
  // context lookup (which needs account + region at synth time).
  env: { account, region },
  instanceType,
  diskGiB: diskGiBContext !== undefined ? Number(diskGiBContext) : undefined,
  description: 'Telemetry lab: Debian 13 + Windows Server 2025 hosts (disposable)',
});
