# Python Examples for SGAI Observability

This directory contains Python examples demonstrating how to use the `sgai-evaluator` package for comprehensive tracing and observability of AI agents and language model applications.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Langfuse instance (local or cloud)

### Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd sgai-observability/examples/python
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys and configuration
   ```

### Required Environment Variables

Create a `.env` file with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Langfuse Configuration for Observability
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=http://localhost:3000

# Optional: Service Configuration
SGAI_SERVICE_NAME=creative_story_agent
SGAI_TRACER=langfuse
```

## 📋 Examples

### Hello World Example (`hello-world.py`)

A comprehensive example demonstrating:

- **Automatic Story Generation**: Using OpenAI API with tracing
- **Decorator-based Tracing**: Using `@trace_method` for automatic function tracing
- **Manual Subspan Creation**: Creating nested spans for complex operations
- **Error Handling**: Proper error tracking in traces
- **Rich Metadata**: Capturing input/output, timing, and custom attributes

**Features Demonstrated:**

1. **Story Generation with OpenAI**:
   - Automatic tracing of API calls
   - Token usage tracking
   - Error handling and logging

2. **Story Enhancement**:
   - Decorated method with automatic tracing
   - Text analysis (character count, sentences, emotional tone)

3. **Multi-step Processing**:
   - Parent span with multiple child spans
   - Text analysis, sentiment evaluation, and summarization
   - Hierarchical trace structure

**Run the example:**
```bash
python hello-world.py
```

## 🎯 Key Features

### 1. **Zero-Config Auto-Instrumentation**
Simply import the package and it automatically detects and instruments supported frameworks:

```python
from sgai_evaluator import trace, start_span, set_agent_name
```

### 2. **Decorator-Based Tracing**
Easily add tracing to any function or method:

```python
class MyProcessor:
    @trace('my_operation', component='processor')
    def process_data(self, data):
        # Your logic here
        return processed_data
```

### 3. **Manual Span Management**
Create custom spans for fine-grained tracing:

```python
with start_span('custom_operation', metadata={'key': 'value'}) as span:
    # Your operation here
    result = do_something()
    # Span automatically ends and captures result
```

### 4. **Framework Support**
- **OpenAI**: Direct API calls with automatic tracing
- **Langfuse**: Native integration for observability backend
- **Custom Frameworks**: Easy to extend with adapter pattern

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SGAI_TRACER` | Tracing backend to use | `langfuse` |
| `SGAI_SERVICE_NAME` | Service name for traces | `agent_service` |
| `AGENT_NAME` | Agent name for automatic tagging | None |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | Required |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | Required |
| `LANGFUSE_HOST` | Langfuse host URL | `http://localhost:3000` |
| `OPENAI_API_KEY` | OpenAI API key | Required |

### Programmatic Configuration

```python
from sgai_evaluator import set_agent_name

# Set global agent name for all traces (overrides AGENT_NAME env var)
set_agent_name('My Custom Agent')

# Or use environment variables (recommended):
# AGENT_NAME=My Custom Agent
# LANGFUSE_PUBLIC_KEY=your_key
# LANGFUSE_SECRET_KEY=your_secret
# LANGFUSE_HOST=https://your-langfuse-instance.com
```

## 📊 Observability Features

### Trace Structure
The examples create hierarchical traces with:

- **Root Span**: Main operation (e.g., story generation)
- **Child Spans**: Sub-operations (e.g., text analysis, sentiment evaluation)
- **Generation Spans**: LLM API calls with token tracking
- **Error Spans**: Automatic error capture and logging

### Metadata Captured
- Input/output data
- Token usage and costs
- Execution timing
- Error messages and stack traces
- Custom attributes and tags
- Model information

### Dashboard Views
In your Langfuse dashboard, you'll see:
- Trace timeline and hierarchy
- Performance metrics
- Error rates and patterns
- Token usage analytics
- Custom metadata and tags

## 🚨 Troubleshooting

### Common Issues

1. **Import Error**: `ModuleNotFoundError: No module named 'sgai_evaluator'`
   ```bash
   pip install sgai-evaluator
   ```

2. **Authentication Error**: Check your environment variables
   ```bash
   # Verify your .env file has the correct keys
   cat .env
   ```

3. **Connection Error**: Ensure Langfuse is running
   ```bash
   # If using local Langfuse
   curl http://localhost:3000/api/public/health
   ```

4. **Trace Not Appearing**: Check flush is called
   ```python
   from sgai_evaluator import flush
   flush()  # Ensure traces are sent
   ```

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

To add new examples:

1. Create a new Python file in this directory
2. Follow the existing pattern with proper documentation
3. Add any new dependencies to `requirements.txt`
4. Update this README with example description

## 📚 Additional Resources

- [SGAi Evaluator Documentation](https://github.com/stackgen-ai/sgai-observability)
- [Langfuse Documentation](https://langfuse.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## 🔗 Related Examples

- [TypeScript Examples](../typescript/) - Node.js/TypeScript equivalent examples
- [Advanced Examples](../advanced/) - More complex use cases and patterns 