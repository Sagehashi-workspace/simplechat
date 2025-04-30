#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BedrockChatbotStack } from '../lib/bedrock-chatbot-stack';

const app = new cdk.App();
new BedrockChatbotStack(app, 'BedrockChatbotStack', {
  // モデルIDをオプションで指定可能
  modelId: 'us.amazon.nova-lite-v1:0',
  //modelId: 'us.amazon.nova-micro-v1:0',
  
  // 環境変数から取得したリージョンを使用、またはデフォルトとしてus-east-1を使用
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
  },
});

// タグはスタックレベルで追加
cdk.Tags.of(app).add('Project', 'BedrockChatbot');
cdk.Tags.of(app).add('Environment', 'Dev');

const fastApiUrl = this.node.tryGetContext('fastapiUrl');
if (!fastApiUrl) {
  throw new Error(
    'ERROR'
  );
}

// Lambda function
const chatFunction = new lambda.Function(this, 'ChatFunction', {
  runtime: lambda.Runtime.PYTHON_3_10,
  handler: 'index.lambda_handler',
  code: lambda.Code.fromAsset(path.join(__dirname, '../lambda')),
  timeout: cdk.Duration.seconds(30),
  memorySize: 128,
  role: lambdaRole,
  environment: {
    MODEL_ID: modelId,
    FASTAPI_URL: fastApiUrl,
  },
});
