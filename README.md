# Prompt-to-DSPy Pipeline Generator 🔮

Convert natural language prompts and examples into optimized DSPy pipelines using local Ollama models.

## Overview

This tool allows you to:
1. Describe a task in natural language
2. Provide input-output examples
3. Automatically generate a DSPy pipeline
4. Optimize the pipeline using your examples
5. Use the optimized pipeline for production tasks

## Features

- **Local LLM with Ollama**: Uses local models, no API keys needed
- **Interactive Setup**: Guided process for defining tasks and examples
- **DSPy Integration**: Generates proper DSPy signatures and modules
- **Pipeline Optimization**: Uses DSPy's BootstrapFewShot optimizer
- **Synthetic Data Generation**: Creates prompts for generating more training data
- **Flexible Input Types**: Supports text, files, JSON, Excel, and more
- **Reusable Pipelines**: Save and load optimized pipelines

## Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
   ```bash
   # Install Ollama (macOS/Linux)
   curl -fsSL https://ollama.com/install.sh | sh

   # Start Ollama
   ollama serve

   # Pull a model (e.g., llama3.2)
   ollama pull llama3.2
   ```

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd prompt-to-code

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Copy and configure environment variables
cp .env.example .env
```

## Quick Start

```bash
# Make sure Ollama is running
ollama serve

# Run the pipeline generator
python prompt_to_dspy.py
```

## Usage Example

Let's say you want to extract KPIs from Excel data. Here's how you'd use the tool:

### Step 1: Describe Your Task

```
Describe your task: Extract monthly KPI metrics from sales data and provide a text analysis
What type of input: excel
What type of output: text analysis and JSON metrics
```

### Step 2: Provide Examples

```
How many examples: 3

Example 1:
Input: Monthly Sales Report Q1 2024
Revenue: $1.2M, Growth: +15%, Customer Acquisition: 450 new customers
Expected Output: Strong Q1 performance with 15% revenue growth reaching $1.2M. Customer acquisition exceeded targets with 450 new customers.

Example 2:
Input: Monthly Sales Report Q2 2024
Revenue: $980K, Growth: -5%, Customer Acquisition: 320 new customers
Expected Output: Q2 showed a 5% decline in revenue to $980K. Customer acquisition slowed to 320 new customers, indicating market headwinds.

...and so on
```

### Step 3: Generate and Optimize

The tool will:
- Generate a DSPy pipeline structure
- Optimize it using your examples
- Save the optimized pipeline

### Step 4: Use the Pipeline

You can immediately test the pipeline or load it later:

```python
import dspy

# Load the optimized pipeline
pipeline = dspy.Module.load("optimized_pipeline.json")

# Use it
result = pipeline(input_data="Your new data here")
print(result.output)
```

## Output Files

After running, you'll get:

1. **generated_pipeline.py** - The DSPy pipeline code
2. **optimized_pipeline.json** - Serialized optimized pipeline
3. **task_config.json** - Your task definition and examples
4. **synthetic_data_prompt.txt** - Prompt to generate more training data

## Use Cases

### 1. Excel Data Analysis
Extract and analyze KPIs from spreadsheets

### 2. Document Classification
Categorize documents based on content

### 3. Entity Extraction
Extract structured information from unstructured text

### 4. Text Summarization
Generate summaries with specific formats

### 5. Data Transformation
Convert data from one format to another

## Advanced Usage

### Custom Ollama Model

```bash
export OLLAMA_MODEL=mistral
python prompt_to_dspy.py
```

### Programmatic Usage

```python
from prompt_to_dspy import DSPyPipelineGenerator, TaskExample

# Initialize
generator = DSPyPipelineGenerator(ollama_model="llama3.2")
generator.setup_ollama()

# Define task
task_info = {
    "description": "Extract key points from meeting notes",
    "input_type": "text",
    "output_type": "bullet points"
}

# Create examples
examples = [
    TaskExample(
        input_data="Meeting about Q4 planning. Discussed budget, timeline, and resources.",
        expected_output="• Budget allocation for Q4\n• Project timeline\n• Resource planning"
    )
]

# Generate and optimize
pipeline_code = generator.generate_pipeline_code(task_info, examples)
optimized = generator.optimize_pipeline(examples)

# Use pipeline
result = optimized(input_data="Your meeting notes here")
print(result.output)
```

### Generating Synthetic Data

Use the generated `synthetic_data_prompt.txt` with any LLM to create more training examples:

```bash
# Using Ollama
cat synthetic_data_prompt.txt | ollama run llama3.2

# Or copy the prompt to ChatGPT, Claude, etc.
```

## Configuration

Create a `.env` file:

```env
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
VERBOSE=true
```

## Troubleshooting

### Ollama Connection Error

```
✗ Error setting up Ollama: Connection refused
```

**Solution**: Make sure Ollama is running
```bash
ollama serve
```

### Model Not Found

```
✗ Error: model 'llama3.2' not found
```

**Solution**: Pull the model
```bash
ollama pull llama3.2
```

### Optimization Takes Too Long

- Reduce the number of examples
- Use a smaller model
- Decrease `max_bootstrapped_demos` in the code

### Import Errors

```
ModuleNotFoundError: No module named 'dspy'
```

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

## Architecture

```
┌─────────────────┐
│  User Input     │
│  (Task + Examples)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pipeline        │
│ Generator       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DSPy Module     │
│ Generation      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Optimization    │
│ (BootstrapFewShot)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Optimized       │
│ Pipeline        │
└─────────────────┘
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Support for more DSPy optimizers (MIPRO, BayesianSignatureOptimizer)
- [ ] Automatic synthetic data generation
- [ ] Web UI for easier interaction
- [ ] Pipeline versioning and comparison
- [ ] Integration with more LLM providers
- [ ] Batch processing mode
- [ ] Pipeline performance metrics dashboard

## Examples

See the `examples/` directory for more use cases:
- Excel KPI extraction
- Document classification
- Entity extraction
- Text summarization

---

Built with ❤️ using [DSPy](https://github.com/stanfordnlp/dspy) and [Ollama](https://ollama.com)