#!/usr/bin/env python3
"""
Flask Web UI for Prompt-to-DSPy Pipeline Generator
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from prompt_to_dspy import DSPyPipelineGenerator, TaskExample

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dspy-pipeline-generator-secret-key'

# Store sessions temporarily (in production, use a database)
sessions = {}


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/generate-pipeline', methods=['POST'])
def generate_pipeline():
    """Generate DSPy pipeline from user input"""
    try:
        data = request.json

        # Extract task information
        task_description = data.get('taskDescription', '')
        input_type = data.get('inputType', 'text')
        output_type = data.get('outputType', 'text')
        ollama_model = data.get('ollamaModel', 'llama3.2')

        # Extract examples
        examples_data = data.get('examples', [])

        if not task_description:
            return jsonify({'error': 'Task description is required'}), 400

        if not examples_data or len(examples_data) < 1:
            return jsonify({'error': 'At least one example is required'}), 400

        # Initialize the generator
        generator = DSPyPipelineGenerator(ollama_model=ollama_model)

        # Setup Ollama
        setup_success = generator.setup_ollama()
        if not setup_success:
            return jsonify({
                'error': 'Failed to connect to Ollama. Make sure Ollama is running (ollama serve)',
                'suggestion': 'Run: ollama serve'
            }), 500

        # Create task info
        task_info = {
            'description': task_description,
            'input_type': input_type,
            'output_type': output_type
        }

        # Create examples
        examples = [
            TaskExample(
                input_data=ex.get('input', ''),
                expected_output=ex.get('output', '')
            )
            for ex in examples_data
        ]

        # Generate pipeline code
        pipeline_code = generator.generate_pipeline_code(task_info, examples)

        # Save task configuration
        task_config = {
            'task_info': task_info,
            'examples': [
                {'input': ex.input_data, 'output': ex.expected_output}
                for ex in examples
            ],
            'timestamp': datetime.now().isoformat()
        }

        with open('task_config.json', 'w') as f:
            json.dump(task_config, f, indent=2)

        # Optimize pipeline
        try:
            optimized_pipeline = generator.optimize_pipeline(examples)
            optimization_success = True
            optimization_message = 'Pipeline optimized successfully!'
        except Exception as opt_error:
            optimization_success = False
            optimization_message = f'Pipeline generated but optimization failed: {str(opt_error)}'

        # Generate synthetic data prompt
        synthetic_prompt = generator.generate_synthetic_data_prompt(task_info, examples)

        with open('synthetic_data_prompt.txt', 'w') as f:
            f.write(synthetic_prompt)

        # Create session ID
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        sessions[session_id] = {
            'task_info': task_info,
            'examples': examples,
            'pipeline_code': pipeline_code,
            'optimized': optimization_success
        }

        return jsonify({
            'success': True,
            'sessionId': session_id,
            'pipelineCode': pipeline_code,
            'optimizationSuccess': optimization_success,
            'optimizationMessage': optimization_message,
            'syntheticPrompt': synthetic_prompt,
            'filesGenerated': [
                'generated_pipeline.py',
                'task_config.json',
                'synthetic_data_prompt.txt'
            ] + (['optimized_pipeline.json'] if optimization_success else [])
        })

    except Exception as e:
        return jsonify({
            'error': f'Failed to generate pipeline: {str(e)}',
            'details': str(type(e).__name__)
        }), 500


@app.route('/api/test-pipeline', methods=['POST'])
def test_pipeline():
    """Test the generated pipeline with new input"""
    try:
        data = request.json
        session_id = data.get('sessionId')
        test_input = data.get('testInput', '')

        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400

        if not test_input:
            return jsonify({'error': 'Test input is required'}), 400

        session_data = sessions[session_id]

        if not session_data.get('optimized'):
            return jsonify({'error': 'Pipeline was not successfully optimized'}), 400

        # Load the optimized pipeline
        import dspy
        try:
            # The optimized pipeline should be loaded from file
            # This is a simplified version - in production, you'd properly load the saved pipeline
            return jsonify({
                'success': True,
                'output': 'Pipeline testing will be available once optimization is complete.',
                'note': 'Use the generated Python file to test your pipeline programmatically.'
            })
        except Exception as e:
            return jsonify({'error': f'Failed to test pipeline: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Error testing pipeline: {str(e)}'}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files"""
    allowed_files = [
        'generated_pipeline.py',
        'task_config.json',
        'optimized_pipeline.json',
        'synthetic_data_prompt.txt'
    ]

    if filename not in allowed_files:
        return jsonify({'error': 'Invalid file'}), 400

    file_path = os.path.join(os.getcwd(), filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)


@app.route('/api/health')
def health_check():
    """Check if Ollama is running"""
    try:
        generator = DSPyPipelineGenerator()
        ollama_running = generator.setup_ollama()

        return jsonify({
            'status': 'healthy',
            'ollama': 'running' if ollama_running else 'not running',
            'message': 'OK' if ollama_running else 'Ollama is not running. Run: ollama serve'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Starting Prompt-to-DSPy Web Interface...")
    print("📍 Access the UI at: http://localhost:5000")
    print("\n⚠️  Make sure Ollama is running: ollama serve")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
