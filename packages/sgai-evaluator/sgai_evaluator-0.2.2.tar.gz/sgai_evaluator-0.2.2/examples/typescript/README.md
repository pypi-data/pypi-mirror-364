# SGAI Observability - TypeScript Examples

This directory contains TypeScript examples demonstrating how to use SGAI Observability with OpenAI Agents using the `stackgenai/sgai-evaluator` package.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API keys:
   - `OPENAI_API_KEY`: Your OpenAI API key from https://platform.openai.com/api-keys
   - `LANGFUSE_PUBLIC_KEY`: Your Langfuse public key from your Langfuse project settings
   - `LANGFUSE_SECRET_KEY`: Your Langfuse secret key from your Langfuse project settings
   - `LANGFUSE_HOST`: Your Langfuse host URL (defaults to https://cloud.langfuse.com)

3. **Run the example:**
   ```bash
   npm start
   ```

## Examples

### hello-world.ts
A simple example showing an OpenAI Agent that tells creative stories. This demonstrates:
- Basic agent configuration
- Integration with stackgenai/sgai-evaluator for observability
- Creative storytelling vs. technical responses

The agent will generate a story about a robot discovering music, which will be traced automatically using the sgai-evaluator package.

## Features

- **Automated Tracing**: All agent interactions are automatically traced using sgai-evaluator
- **Rich Context**: Captures agent instructions, inputs, outputs, and metadata
- **Error Handling**: Graceful fallback if tracing is not configured
- **TypeScript Support**: Full type safety and IntelliSense

## Troubleshooting

### Installation Issues
If you encounter dependency resolution issues:
```bash
npm install --legacy-peer-deps
```

### Missing API Keys
The example will fail if OpenAI API keys are not configured. Make sure you have:
1. Created an OpenAI account and generated an API key
2. Set up a Langfuse project (free at https://cloud.langfuse.com)
3. Copied `env.example` to `.env` and filled in your actual keys

### Compilation Errors
If TypeScript compilation fails:
```bash
npm run build
```

### Runtime Issues
Check that the sgai-evaluator package is properly initialized by looking for console output indicating tracing setup. 