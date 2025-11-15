#!/usr/bin/env python3
"""
Example: Programmatic usage of the Prompt-to-DSPy Pipeline Generator

This example shows how to use the pipeline generator in your own code
without the interactive CLI.
"""

from prompt_to_dspy import DSPyPipelineGenerator, TaskExample


def example_kpi_extraction():
    """
    Example: Extract KPIs from sales data

    This demonstrates how you might use the tool for analyzing
    Excel/text data containing business metrics.
    """
    print("\n" + "="*80)
    print("EXAMPLE: KPI Extraction from Sales Data")
    print("="*80 + "\n")

    # Initialize the generator
    generator = DSPyPipelineGenerator(
        ollama_model="llama3.2",
        ollama_base_url="http://localhost:11434"
    )

    # Setup Ollama
    generator.setup_ollama()

    # Define the task
    task_info = {
        "description": "Extract key performance indicators from sales data and provide a concise analysis",
        "input_type": "text",
        "output_type": "text analysis with metrics"
    }

    # Create training examples
    examples = [
        TaskExample(
            input_data="""
            Q1 2024 Sales Report
            Total Revenue: $1,250,000
            YoY Growth: +18%
            New Customers: 450
            Customer Retention: 92%
            Average Deal Size: $12,500
            """,
            expected_output="""
            Strong Q1 performance with $1.25M revenue and 18% YoY growth.
            Customer metrics are healthy with 450 new acquisitions and 92% retention.
            Average deal size of $12.5K indicates good upsell opportunities.
            """,
            description="Positive quarter with growth"
        ),
        TaskExample(
            input_data="""
            Q2 2024 Sales Report
            Total Revenue: $980,000
            YoY Growth: -8%
            New Customers: 320
            Customer Retention: 88%
            Average Deal Size: $11,200
            """,
            expected_output="""
            Q2 showed challenges with $980K revenue and -8% YoY decline.
            Customer acquisition slowed to 320 new customers with retention dropping to 88%.
            Decreased deal size to $11.2K suggests pricing pressure.
            """,
            description="Challenging quarter with decline"
        ),
        TaskExample(
            input_data="""
            Q3 2024 Sales Report
            Total Revenue: $1,100,000
            YoY Growth: +5%
            New Customers: 380
            Customer Retention: 90%
            Average Deal Size: $13,000
            """,
            expected_output="""
            Q3 recovery with $1.1M revenue and modest 5% YoY growth.
            Customer metrics improving with 380 new acquisitions and 90% retention.
            Higher average deal size of $13K shows effective value positioning.
            """,
            description="Recovery quarter"
        )
    ]

    print(f"Task: {task_info['description']}")
    print(f"Training examples: {len(examples)}\n")

    # Generate the pipeline
    pipeline_code = generator.generate_pipeline_code(task_info, examples)
    print("Pipeline generated successfully!\n")

    # Optimize the pipeline
    optimized_pipeline = generator.optimize_pipeline(examples)
    print("Pipeline optimized!\n")

    # Test the pipeline with new data
    test_input = """
    Q4 2024 Sales Report
    Total Revenue: $1,450,000
    YoY Growth: +22%
    New Customers: 520
    Customer Retention: 94%
    Average Deal Size: $14,500
    """

    print("Testing with new data:")
    print("-" * 80)
    print("Input:")
    print(test_input)
    print("\nOutput:")

    try:
        result = optimized_pipeline(input_data=test_input)
        print(result.output)
    except Exception as e:
        print(f"Error during prediction: {e}")

    # Save the pipeline
    generator.save_pipeline("kpi_extraction_pipeline.json")
    print("\nPipeline saved to: kpi_extraction_pipeline.json")


def example_text_classification():
    """
    Example: Classify customer support tickets

    This demonstrates classification tasks.
    """
    print("\n" + "="*80)
    print("EXAMPLE: Customer Support Ticket Classification")
    print("="*80 + "\n")

    generator = DSPyPipelineGenerator(ollama_model="llama3.2")
    generator.setup_ollama()

    task_info = {
        "description": "Classify customer support tickets into categories: Technical, Billing, Feature Request, or General",
        "input_type": "text",
        "output_type": "category"
    }

    examples = [
        TaskExample(
            input_data="My app keeps crashing when I try to export data. Can you help?",
            expected_output="Technical"
        ),
        TaskExample(
            input_data="I was charged twice for my subscription this month.",
            expected_output="Billing"
        ),
        TaskExample(
            input_data="It would be great if you could add dark mode to the app.",
            expected_output="Feature Request"
        ),
        TaskExample(
            input_data="What are your business hours?",
            expected_output="General"
        ),
    ]

    print(f"Task: {task_info['description']}")
    print(f"Training examples: {len(examples)}\n")

    pipeline_code = generator.generate_pipeline_code(task_info, examples)
    optimized_pipeline = generator.optimize_pipeline(examples)

    # Test
    test_cases = [
        "The login page is not loading properly",
        "Can I get a refund for this month?",
        "Please add multi-language support"
    ]

    print("Testing classification:")
    print("-" * 80)
    for test in test_cases:
        try:
            result = optimized_pipeline(input_data=test)
            print(f"Input: {test}")
            print(f"Category: {result.output}\n")
        except Exception as e:
            print(f"Error: {e}\n")


def example_entity_extraction():
    """
    Example: Extract structured information from unstructured text

    This demonstrates entity/information extraction tasks.
    """
    print("\n" + "="*80)
    print("EXAMPLE: Contact Information Extraction")
    print("="*80 + "\n")

    generator = DSPyPipelineGenerator(ollama_model="llama3.2")
    generator.setup_ollama()

    task_info = {
        "description": "Extract contact information (name, email, phone) from text in JSON format",
        "input_type": "text",
        "output_type": "json"
    }

    examples = [
        TaskExample(
            input_data="Hi, I'm John Smith. You can reach me at john.smith@email.com or call 555-1234.",
            expected_output='{"name": "John Smith", "email": "john.smith@email.com", "phone": "555-1234"}'
        ),
        TaskExample(
            input_data="Contact Sarah Johnson (sarah.j@company.com) for more info. Her number is 555-5678.",
            expected_output='{"name": "Sarah Johnson", "email": "sarah.j@company.com", "phone": "555-5678"}'
        ),
    ]

    print(f"Task: {task_info['description']}")
    print(f"Training examples: {len(examples)}\n")

    pipeline_code = generator.generate_pipeline_code(task_info, examples)
    optimized_pipeline = generator.optimize_pipeline(examples)

    # Test
    test_input = "Please contact Michael Brown at m.brown@business.org or 555-9999 for details."

    print("Testing extraction:")
    print("-" * 80)
    print(f"Input: {test_input}")

    try:
        result = optimized_pipeline(input_data=test_input)
        print(f"Extracted: {result.output}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        PROMPT-TO-DSPY EXAMPLES                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print("This script demonstrates various use cases for the pipeline generator.")
    print("\nAvailable examples:")
    print("  1. KPI Extraction from Sales Data")
    print("  2. Customer Support Ticket Classification")
    print("  3. Contact Information Extraction")
    print("\nRunning all examples...\n")

    try:
        # Run examples
        example_kpi_extraction()
        # Uncomment to run more examples:
        # example_text_classification()
        # example_entity_extraction()

        print("\n" + "="*80)
        print("Examples complete!")
        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
