// State management
let exampleCount = 0;
let sessionId = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
    addExample(); // Add first example by default
});

// Check Ollama health status
async function checkHealth() {
    const statusElement = document.getElementById('health-status');

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy' && data.ollama === 'running') {
            statusElement.textContent = '✓ Ollama is running';
            statusElement.className = 'health-status healthy';
        } else {
            statusElement.textContent = '⚠ Ollama is not running - Run: ollama serve';
            statusElement.className = 'health-status unhealthy';
        }
    } catch (error) {
        statusElement.textContent = '✗ Cannot connect to backend';
        statusElement.className = 'health-status unhealthy';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Add example button
    document.getElementById('add-example-btn').addEventListener('click', addExample);

    // Generate button
    document.getElementById('generate-btn').addEventListener('click', generatePipeline);

    // Test button
    document.getElementById('test-btn').addEventListener('click', testPipeline);

    // Copy buttons
    document.getElementById('copy-code-btn').addEventListener('click', () => {
        copyToClipboard('pipeline-code');
    });

    document.getElementById('copy-synthetic-btn').addEventListener('click', () => {
        copyToClipboard('synthetic-prompt');
    });

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
}

// Add a new example input
function addExample() {
    exampleCount++;
    const container = document.getElementById('examples-container');

    const exampleDiv = document.createElement('div');
    exampleDiv.className = 'example-item';
    exampleDiv.dataset.exampleId = exampleCount;

    exampleDiv.innerHTML = `
        <div class="example-header">
            <span class="example-number">Example ${exampleCount}</span>
            <button type="button" class="remove-example-btn" onclick="removeExample(${exampleCount})">
                Remove
            </button>
        </div>
        <div class="form-group">
            <label for="example-input-${exampleCount}">Input</label>
            <textarea id="example-input-${exampleCount}" rows="3" placeholder="Enter example input..." required></textarea>
        </div>
        <div class="form-group">
            <label for="example-output-${exampleCount}">Expected Output</label>
            <textarea id="example-output-${exampleCount}" rows="3" placeholder="Enter expected output..." required></textarea>
        </div>
    `;

    container.appendChild(exampleDiv);
}

// Remove an example
function removeExample(id) {
    const exampleDiv = document.querySelector(`[data-example-id="${id}"]`);
    if (exampleDiv) {
        exampleDiv.remove();
    }

    // Renumber remaining examples
    const remainingExamples = document.querySelectorAll('.example-item');
    remainingExamples.forEach((example, index) => {
        const numberSpan = example.querySelector('.example-number');
        numberSpan.textContent = `Example ${index + 1}`;
    });
}

// Collect form data
function collectFormData() {
    const taskDescription = document.getElementById('task-description').value.trim();
    const inputType = document.getElementById('input-type').value;
    const outputType = document.getElementById('output-type').value;
    const ollamaModel = document.getElementById('ollama-model').value.trim() || 'llama3.2';

    // Collect examples
    const examples = [];
    const exampleItems = document.querySelectorAll('.example-item');

    exampleItems.forEach((item, index) => {
        const inputId = item.querySelector('textarea[id^="example-input-"]').id;
        const outputId = item.querySelector('textarea[id^="example-output-"]').id;

        const input = document.getElementById(inputId).value.trim();
        const output = document.getElementById(outputId).value.trim();

        if (input && output) {
            examples.push({ input, output });
        }
    });

    return {
        taskDescription,
        inputType,
        outputType,
        ollamaModel,
        examples
    };
}

// Validate form data
function validateFormData(data) {
    if (!data.taskDescription) {
        showError('Please provide a task description');
        return false;
    }

    if (data.examples.length === 0) {
        showError('Please provide at least one example');
        return false;
    }

    return true;
}

// Generate pipeline
async function generatePipeline() {
    const data = collectFormData();

    if (!validateFormData(data)) {
        return;
    }

    // Show loading
    const generateBtn = document.getElementById('generate-btn');
    const loadingDiv = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');

    generateBtn.disabled = true;
    loadingDiv.style.display = 'block';
    resultsSection.style.display = 'none';

    try {
        const response = await fetch('/api/generate-pipeline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to generate pipeline');
        }

        // Store session ID
        sessionId = result.sessionId;

        // Display results
        displayResults(result);

    } catch (error) {
        showError(error.message);
    } finally {
        generateBtn.disabled = false;
        loadingDiv.style.display = 'none';
    }
}

// Display results
function displayResults(result) {
    const resultsSection = document.getElementById('results-section');
    const testSection = document.getElementById('test-section');
    const statusMessage = document.getElementById('status-message');
    const pipelineCode = document.getElementById('pipeline-code');
    const syntheticPrompt = document.getElementById('synthetic-prompt');
    const downloadLinks = document.getElementById('download-links');

    // Show results section
    resultsSection.style.display = 'block';

    // Display status message
    if (result.optimizationSuccess) {
        statusMessage.className = 'message success';
        statusMessage.textContent = '✓ ' + result.optimizationMessage;
        testSection.style.display = 'block';
    } else {
        statusMessage.className = 'message warning';
        statusMessage.textContent = '⚠ ' + result.optimizationMessage;
        testSection.style.display = 'none';
    }

    // Display pipeline code
    pipelineCode.textContent = result.pipelineCode;

    // Display synthetic prompt
    syntheticPrompt.textContent = result.syntheticPrompt;

    // Display download links
    downloadLinks.innerHTML = '';
    result.filesGenerated.forEach(filename => {
        const link = document.createElement('a');
        link.href = `/api/download/${filename}`;
        link.className = 'download-link';
        link.textContent = `📥 Download ${filename}`;
        link.download = filename;
        downloadLinks.appendChild(link);
    });

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Test pipeline
async function testPipeline() {
    const testInput = document.getElementById('test-input').value.trim();

    if (!testInput) {
        showError('Please provide test input');
        return;
    }

    if (!sessionId) {
        showError('No pipeline session found');
        return;
    }

    const testBtn = document.getElementById('test-btn');
    testBtn.disabled = true;

    try {
        const response = await fetch('/api/test-pipeline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                testInput: testInput
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to test pipeline');
        }

        // Display test output
        const testOutput = document.getElementById('test-output');
        const testResult = document.getElementById('test-result');

        testOutput.style.display = 'block';
        testResult.textContent = result.output;

        if (result.note) {
            testResult.textContent += '\n\nNote: ' + result.note;
        }

    } catch (error) {
        showError(error.message);
    } finally {
        testBtn.disabled = false;
    }
}

// Switch tabs
function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Copy to clipboard
async function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;

    try {
        await navigator.clipboard.writeText(text);
        showSuccess('Copied to clipboard!');
    } catch (error) {
        showError('Failed to copy to clipboard');
    }
}

// Show error message
function showError(message) {
    const statusMessage = document.getElementById('status-message');
    const resultsSection = document.getElementById('results-section');

    resultsSection.style.display = 'block';
    statusMessage.className = 'message error';
    statusMessage.textContent = '✗ ' + message;

    resultsSection.scrollIntoView({ behavior: 'smooth' });

    setTimeout(() => {
        if (statusMessage.className.includes('error')) {
            resultsSection.style.display = 'none';
        }
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const statusMessage = document.getElementById('status-message');
    const originalContent = statusMessage.innerHTML;
    const originalClass = statusMessage.className;

    statusMessage.className = 'message success';
    statusMessage.textContent = '✓ ' + message;

    setTimeout(() => {
        statusMessage.innerHTML = originalContent;
        statusMessage.className = originalClass;
    }, 3000);
}
