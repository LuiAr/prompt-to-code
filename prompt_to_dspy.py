#!/usr/bin/env python3
"""
Prompt-to-DSPy Pipeline Generator
Converts user prompts and examples into optimized DSPy pipelines using Ollama
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
import dspy
from dspy.teleprompt import BootstrapFewShot


class TaskExample:
    """Represents a single input-output example for the task"""

    def __init__(self, input_data: Any, expected_output: str, description: str = ""):
        self.input_data = input_data
        self.expected_output = expected_output
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "input": self.input_data,
            "output": self.expected_output,
            "description": self.description
        }


class DSPyPipelineGenerator:
    """Generates and optimizes DSPy pipelines based on user requirements"""

    def __init__(self, ollama_model: str = "llama3.2", ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize the pipeline generator

        Args:
            ollama_model: Name of the Ollama model to use
            ollama_base_url: Base URL for Ollama API
        """
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.lm = None
        self.optimized_pipeline = None

    def setup_ollama(self):
        """Configure DSPy to use Ollama"""
        print(f"\n🔧 Setting up Ollama with model: {self.ollama_model}")

        try:
            self.lm = dspy.OllamaLocal(
                model=self.ollama_model,
                base_url=self.ollama_base_url,
                max_tokens=2000
            )
            dspy.settings.configure(lm=self.lm)
            print("✓ Ollama configured successfully")
        except Exception as e:
            print(f"✗ Error setting up Ollama: {e}")
            print("\nMake sure Ollama is running. You can start it with: ollama serve")
            print(f"And ensure the model '{self.ollama_model}' is available: ollama pull {self.ollama_model}")
            sys.exit(1)

    def collect_task_info(self) -> Dict[str, Any]:
        """Collect task information from the user"""
        print("\n" + "="*80)
        print("📋 TASK DEFINITION")
        print("="*80)

        task_description = input("\nDescribe your task (what do you want to accomplish?):\n> ").strip()

        print("\n💡 Examples of tasks:")
        print("  - Extract key metrics from Excel data")
        print("  - Summarize monthly KPI trends")
        print("  - Classify documents by category")
        print("  - Extract entities from text")

        input_type = input("\nWhat type of input will you provide? (text/file/json/excel):\n> ").strip().lower()
        output_type = input("What type of output do you expect? (text/json/summary/analysis):\n> ").strip().lower()

        return {
            "description": task_description,
            "input_type": input_type,
            "output_type": output_type
        }

    def collect_examples(self) -> List[TaskExample]:
        """Collect input-output examples from the user"""
        print("\n" + "="*80)
        print("📝 EXAMPLE COLLECTION")
        print("="*80)
        print("\nProvide examples of input-output pairs for your task.")
        print("These will be used to optimize the pipeline.")

        examples = []
        example_count = int(input("\nHow many examples do you want to provide? (recommended: 3-10): ").strip() or "3")

        for i in range(example_count):
            print(f"\n--- Example {i+1} ---")

            example_desc = input(f"Description of example {i+1} (optional): ").strip()

            print(f"Input data for example {i+1}:")
            print("(You can paste text, file path, or JSON. Press Enter twice when done)")
            input_lines = []
            while True:
                line = input()
                if line == "" and len(input_lines) > 0:
                    break
                input_lines.append(line)
            input_data = "\n".join(input_lines)

            print(f"\nExpected output for example {i+1}:")
            expected_output = input("> ").strip()

            examples.append(TaskExample(input_data, expected_output, example_desc))
            print(f"✓ Example {i+1} saved")

        return examples

    def generate_pipeline_code(self, task_info: Dict[str, Any], examples: List[TaskExample]) -> str:
        """
        Generate DSPy pipeline code based on task description and examples

        This uses Ollama to generate the appropriate DSPy signature and module
        """
        print("\n" + "="*80)
        print("🤖 GENERATING DSPY PIPELINE")
        print("="*80)

        # Create a prompt for the LLM to generate DSPy code
        generation_prompt = f"""
Task Description: {task_info['description']}
Input Type: {task_info['input_type']}
Output Type: {task_info['output_type']}

Examples:
{self._format_examples_for_prompt(examples[:3])}

Generate a DSPy signature and module for this task. The signature should define the input and output fields clearly.

Return ONLY valid Python code for the DSPy signature and module, no explanations.

Example format:
```python
class TaskSignature(dspy.Signature):
    \"\"\"Your task description here\"\"\"
    input_field = dspy.InputField(desc="description")
    output_field = dspy.OutputField(desc="description")

class TaskModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(TaskSignature)

    def forward(self, input_field):
        return self.predictor(input_field=input_field)
```
"""

        # For now, we'll create a generic pipeline structure
        # In a real implementation, you'd use the LLM to generate this
        print("📝 Generating pipeline structure...")

        pipeline_code = self._create_generic_pipeline(task_info)

        print("✓ Pipeline code generated")
        return pipeline_code

    def _format_examples_for_prompt(self, examples: List[TaskExample]) -> str:
        """Format examples for inclusion in prompts"""
        formatted = []
        for i, ex in enumerate(examples, 1):
            formatted.append(f"Example {i}:")
            formatted.append(f"  Input: {ex.input_data[:200]}...")  # Truncate long inputs
            formatted.append(f"  Output: {ex.expected_output}")
        return "\n".join(formatted)

    def _create_generic_pipeline(self, task_info: Dict[str, Any]) -> str:
        """Create a generic pipeline structure that can be customized"""

        task_desc = task_info['description']

        # Create the signature and module dynamically
        class GenericTaskSignature(dspy.Signature):
            __doc__ = f"""{task_desc}"""
            input_data = dspy.InputField(desc=f"Input data ({task_info['input_type']})")
            output = dspy.OutputField(desc=f"Output result ({task_info['output_type']})")

        class GenericTaskModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.predictor = dspy.ChainOfThought(GenericTaskSignature)

            def forward(self, input_data):
                result = self.predictor(input_data=input_data)
                return result

        # Store the classes for later use
        self.signature_class = GenericTaskSignature
        self.module_class = GenericTaskModule

        return f"""
# Generated DSPy Pipeline
class TaskSignature(dspy.Signature):
    \"\"\"{task_desc}\"\"\"
    input_data = dspy.InputField(desc="Input data ({task_info['input_type']})")
    output = dspy.OutputField(desc="Output result ({task_info['output_type']})")

class TaskModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(TaskSignature)

    def forward(self, input_data):
        result = self.predictor(input_data=input_data)
        return result
"""

    def optimize_pipeline(self, examples: List[TaskExample]) -> dspy.Module:
        """
        Optimize the pipeline using the provided examples

        Args:
            examples: List of TaskExample objects for optimization

        Returns:
            Optimized DSPy module
        """
        print("\n" + "="*80)
        print("⚡ OPTIMIZING PIPELINE")
        print("="*80)

        # Convert examples to DSPy format
        dspy_examples = []
        for ex in examples:
            dspy_examples.append(
                dspy.Example(
                    input_data=ex.input_data,
                    output=ex.expected_output
                ).with_inputs("input_data")
            )

        print(f"📊 Using {len(dspy_examples)} examples for optimization...")

        # Create the module to optimize
        module = self.module_class()

        # Define a simple metric
        def validation_metric(example, pred, trace=None):
            # Simple metric: check if prediction is not empty
            return len(str(pred.output)) > 0

        try:
            # Use BootstrapFewShot optimizer
            print("🔄 Running optimization (this may take a few minutes)...")
            optimizer = BootstrapFewShot(
                metric=validation_metric,
                max_bootstrapped_demos=3,
                max_labeled_demos=3
            )

            optimized = optimizer.compile(
                module,
                trainset=dspy_examples
            )

            self.optimized_pipeline = optimized
            print("✓ Pipeline optimized successfully!")

            return optimized

        except Exception as e:
            print(f"⚠ Optimization encountered an issue: {e}")
            print("Using non-optimized pipeline...")
            self.optimized_pipeline = module
            return module

    def save_pipeline(self, filename: str = "optimized_pipeline.json"):
        """Save the optimized pipeline to disk"""
        if self.optimized_pipeline is None:
            print("⚠ No optimized pipeline to save")
            return

        print(f"\n💾 Saving pipeline to {filename}...")

        try:
            self.optimized_pipeline.save(filename)
            print(f"✓ Pipeline saved to {filename}")
        except Exception as e:
            print(f"⚠ Could not save pipeline: {e}")

    def use_pipeline(self):
        """Interactive mode to use the optimized pipeline"""
        if self.optimized_pipeline is None:
            print("⚠ No pipeline available. Please generate and optimize first.")
            return

        print("\n" + "="*80)
        print("🚀 PIPELINE USAGE MODE")
        print("="*80)
        print("Enter your input data (or 'quit' to exit):\n")

        while True:
            print("\n--- New Query ---")
            user_input = input("Input: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Exiting pipeline usage mode.")
                break

            if not user_input:
                continue

            try:
                print("\n🤔 Processing...")
                result = self.optimized_pipeline(input_data=user_input)
                print(f"\n✨ Output:\n{result.output}")
            except Exception as e:
                print(f"✗ Error processing input: {e}")


def generate_synthetic_data_prompt(task_info: Dict[str, Any]) -> str:
    """
    Generate a prompt for creating synthetic test data for the task

    This will be used later to generate more examples automatically
    """
    prompt = f"""
# Synthetic Data Generation Prompt

Task: {task_info['description']}
Input Type: {task_info['input_type']}
Output Type: {task_info['output_type']}

## Instructions for AI to Generate Synthetic Data

Please generate 20-30 diverse examples for this task that cover:

1. **Variety**: Different scenarios and edge cases
2. **Realism**: Data that resembles real-world usage
3. **Complexity**: Mix of simple and complex examples
4. **Edge Cases**: Unusual but valid inputs

### Format for Each Example:
```json
{{
  "input": "...",
  "expected_output": "...",
  "category": "normal|edge_case|complex",
  "notes": "Any relevant notes about this example"
}}
```

### Special Considerations:
- For Excel/file inputs: Describe the file content structure
- For text analysis: Include various text lengths and styles
- For KPI extraction: Include different metric types and formats
- Ensure outputs are consistent with the task description

Generate the synthetic data below:
"""

    return prompt


def main():
    """Main application flow"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🔮 PROMPT-TO-DSPY PIPELINE GENERATOR 🔮            ║
║                                                              ║
║  Convert your prompts into optimized DSPy pipelines         ║
║  using local Ollama models                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Configuration
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    print(f"Configuration:")
    print(f"  Model: {ollama_model}")
    print(f"  Ollama URL: {ollama_url}")

    # Initialize generator
    generator = DSPyPipelineGenerator(
        ollama_model=ollama_model,
        ollama_base_url=ollama_url
    )

    # Setup Ollama
    generator.setup_ollama()

    # Collect task information
    task_info = generator.collect_task_info()

    # Collect examples
    examples = generator.collect_examples()

    # Generate synthetic data prompt for later use
    print("\n" + "="*80)
    print("📄 SYNTHETIC DATA GENERATION PROMPT")
    print("="*80)

    synthetic_prompt = generate_synthetic_data_prompt(task_info)

    # Save the prompt to a file
    prompt_file = "synthetic_data_prompt.txt"
    with open(prompt_file, 'w') as f:
        f.write(synthetic_prompt)

    print(f"\n✓ Synthetic data generation prompt saved to: {prompt_file}")
    print("  You can use this prompt later with an AI to generate more training examples.")

    # Generate pipeline
    pipeline_code = generator.generate_pipeline_code(task_info, examples)

    # Save pipeline code
    code_file = "generated_pipeline.py"
    with open(code_file, 'w') as f:
        f.write("import dspy\n\n")
        f.write(pipeline_code)
    print(f"\n✓ Pipeline code saved to: {code_file}")

    # Optimize pipeline
    optimized_pipeline = generator.optimize_pipeline(examples)

    # Save optimized pipeline
    generator.save_pipeline()

    # Ask user if they want to use the pipeline
    print("\n" + "="*80)
    use_now = input("\nWould you like to test the pipeline now? (y/n): ").strip().lower()

    if use_now == 'y':
        generator.use_pipeline()

    # Save task info and examples for future reference
    task_data = {
        "task_info": task_info,
        "examples": [ex.to_dict() for ex in examples],
        "pipeline_file": code_file,
        "synthetic_data_prompt_file": prompt_file
    }

    with open("task_config.json", 'w') as f:
        json.dump(task_data, f, indent=2)

    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)
    print("\nFiles created:")
    print(f"  • {code_file} - Generated pipeline code")
    print(f"  • {prompt_file} - Prompt for synthetic data generation")
    print(f"  • task_config.json - Task configuration and examples")
    print(f"  • optimized_pipeline.json - Optimized pipeline (if successful)")
    print("\nNext steps:")
    print("  1. Use the synthetic data prompt to generate more examples")
    print("  2. Re-run optimization with more examples for better results")
    print("  3. Integrate the pipeline into your application")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
