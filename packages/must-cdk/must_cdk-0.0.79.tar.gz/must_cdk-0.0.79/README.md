# Must CDK

A collection of AWS CDK constructs that implement common architectural patterns and best practices for AWS services. This library aims to simplify the deployment of common cloud infrastructure patterns while maintaining security, scalability, and operational excellence.

## Features

### 🏗️ Amplify Patterns

* Next.js application deployment optimizations
* Multi-environment branch configurations
* Custom domain and SSL setup
* GitHub personal access token authentication
* Automated build and deployment pipelines
* Migration path to GitHub Apps for production
* CLI tool for quick project initialization

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

### CLI Tool

Install globally to quickly initialize Amplify projects:

```bash
# Install CLI globally
npm install -g must-cdk

# Initialize Amplify project with React template
must-cdk amplify init

# Initialize in specific directory
must-cdk amplify init -d /path/to/project
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
