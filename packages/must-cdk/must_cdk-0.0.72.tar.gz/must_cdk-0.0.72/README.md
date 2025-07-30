# Must CDK

A collection of AWS CDK constructs that implement common architectural patterns and best practices for AWS services. This library aims to simplify the deployment of common cloud infrastructure patterns while maintaining security, scalability, and operational excellence.

## Features

### 🏗️ Amplify Patterns

* Next.js application deployment optimizations
* Multi-environment branch configurations
* Custom domain and SSL setup
* Enterprise-grade security configurations
* Automated build and deployment pipelines

### 🚢 ECS CodeDeploy Patterns

* Blue/Green deployment strategies
* Load balanced service deployments
* Auto-scaling configurations
* Health check implementations
* Container security best practices

### 🌐 CloudFront Patterns

* API Gateway integrations
* Multi-origin configurations
* Cross-region setups
* Security headers and WAF integration
* Caching strategies
* Custom domain configurations

### 🔌 API Gateway Lambda Patterns

* REST API implementations
* WebSocket API setups
* Custom domain configurations
* Lambda authorizers
* Rate limiting and API key management

## Installation

### TypeScript/JavaScript

```bash
npm install must-cdk
# or
yarn add must-cdk
```

### Python

```bash
pip install must-cdk
```

## Usage

### TypeScript Example

```python
import * as cdk from 'aws-cdk-lib';
import { AmplifyApp } from 'must-cdk';

export class MyStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new AmplifyApp(this, 'WebApp', {
      appName: 'my-next-app',
      repository: 'https://github.com/org/repo',
      buildSettings: {
        computeType: 'STANDARD_8GB'
      }
    });
  }
}
```

### Python Example

```python
from aws_cdk import App, Stack
from must_cdk import AmplifyApp

class MyStack(Stack):
    def __init__(self, scope: App, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        AmplifyApp(self, "WebApp",
            app_name="my-next-app",
            repository="https://github.com/org/repo",
            build_settings={
                "computeType": "STANDARD_8GB"
            }
        )
```

## Documentation

Detailed documentation for each construct can be found in:

* [Python API Reference](./docs/python/api.md)
* [Examples](./examples/README.md)

## Examples

The [examples](./examples) directory contains working examples for each construct category:

* Amplify deployment patterns
* ECS with CodeDeploy configurations
* CloudFront distribution setups
* API Gateway with Lambda integrations

Each example is provided in both TypeScript and Python with detailed comments and instructions.
