document.addEventListener('DOMContentLoaded', () => {
    // --- Initialize Visuals ---
    createParticles();
    createMatrixRain();

    // Add click listener for the LLM selection buttons to add a visual indicator
    const llmCheckboxes = document.querySelectorAll('.llm-checkbox');
    llmCheckboxes.forEach(box => {
        const input = box.querySelector('input[type="checkbox"]');
        if (input.checked) {
            box.classList.add('selected');
        }
        box.addEventListener('click', () => {
            input.checked = !input.checked;
            box.classList.toggle('selected', input.checked);
        });
    });

    const brainstormBtn = document.getElementById('brainstormBtn');
    const responsesContainer = document.getElementById('responses');
    const loadingIndicator = document.getElementById('loading');
    const matrixRain = document.getElementById('matrixRain');

    // --- Main Brainstorm Button Logic ---
    brainstormBtn.addEventListener('click', async () => {
        const projectName = document.getElementById('projectName').value.trim();
        const projectDescription = document.getElementById('projectDescription').value.trim();

        if (!projectName || !projectDescription) {
            alert('Please fill in the project name and description.');
            return;
        }

        const selectedLLMs = Array.from(document.querySelectorAll('.llm-selection input:checked')).map(input => input.id);

        if (selectedLLMs.length === 0) {
            alert('Please select at least one LLM.');
            return;
        }

        // --- Show Loading State ---
        loadingIndicator.classList.add('active');
        matrixRain.classList.add('active');
        responsesContainer.innerHTML = '';
        brainstormBtn.disabled = true;

        const fullPrompt = `Act as an expert product manager and software architect.
        Project Name: "${projectName}"
        Project Description: "${projectDescription}"
        Based on the above, provide a concise, actionable plan. Focus on:
        1.  Core Concept & Target Audience.
        2.  Key Features (MVP).
        3.  Recommended Technology Stack.
        4.  First Steps for development.`;

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: fullPrompt, llms: selectedLLMs }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An unknown server error occurred.');
            }

            const data = await response.json();
            console.log(data);
            data.forEach(res => createResponseCard(res.llm, res.response, res.model));

        } catch (error) {
            console.error('Error fetching from backend:', error);
            createResponseCard('error', `An error occurred: ${error.message}`);
        } finally {
            // --- Hide Loading State ---
            loadingIndicator.classList.remove('active');
            matrixRain.classList.remove('active');
            brainstormBtn.disabled = false;
            document.querySelector('.main-content').classList.add('show-results');
        }
    });
});

    const generateSummaryBtn = document.getElementById('generate-summary-btn');
    if (generateSummaryBtn) {
        generateSummaryBtn.addEventListener('click', async () => {
            const responseElements = document.querySelectorAll('.llm-response .response-content p');

            if (responseElements.length < 1) {
                alert('Please generate at least one response before generating a summary.');
                return;
            }

            const responseMap = { a: '', b: '', c: '', d: '' };
            const llmClasses = ['gemini', 'claude', 'chatgpt', 'perplexity'];
            const keys = ['a', 'b', 'c', 'd'];

            llmClasses.forEach((llmClass, index) => {
                const responseCard = document.querySelector(`.llm-response.${llmClass} .response-content p`);
                if (responseCard) {
                    responseMap[keys[index]] = responseCard.innerText.trim();
                }
            });

            generateSummaryBtn.disabled = true;
            generateSummaryBtn.textContent = 'Generating Summary...';

            try {
                const response = await fetch('/api/summary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ responses: responseMap }),
                });

                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.error || 'Failed to generate summary.');
                }

                const summaryMarkdown = result.summary;
                const modelName = result.model;

                const existingCard = document.querySelector('.summary-card');
                if (existingCard) {
                    existingCard.remove();
                }

                const summaryCard = document.createElement('div');
                summaryCard.className = 'summary-card';
                summaryCard.innerHTML = `
                    <h3><img src="https://i.ibb.co/3fdp6S4/brain-circuit.png" alt="Summary" class="llm-logo"> Summary Master Plan</h3>
                    <p class="model-name">Model: ${modelName}</p>
                    <div class="summary-content">${marked.parse(summaryMarkdown)}</div>
                    <div class="response-actions">
                        <button class="btn btn-secondary btn-send-to-jules">Send to Jules</button>
                    </div>
                `;

                const sendToJulesBtn = summaryCard.querySelector('.btn-send-to-jules');
                sendToJulesBtn.addEventListener('click', () => {
                    if (window.openJulesModal) {
                        window.openJulesModal(summaryMarkdown, 'Summary Engine');
                    } else {
                        alert('Jules modal functionality is not available.');
                    }
                });

                responsesContainer.prepend(summaryCard);

            } catch (error) {
                console.error('Summary Error:', error);
                alert(`Error during summary generation: ${error.message}`);
            } finally {
                generateSummaryBtn.disabled = false;
                generateSummaryBtn.textContent = 'Generate Summary';
            }
        });
    }
});

// --- UI Helper Functions ---
function createResponseCard(llm, responseText, modelName) {
    const responsesContainer = document.getElementById('responses');
    const card = document.createElement('div');
    card.className = `llm-response ${llm}`;

    const logoEl = document.querySelector(`#${llm} + label img`);
    const logoUrl = logoEl ? logoEl.src : 'https://i.ibb.co/vzVvJ4G/error-icon.png';
    const llmName = llm.charAt(0).toUpperCase() + llm.slice(1);

    // Using a template literal for the main structure
    card.innerHTML = `
        <div class="response-header">
            <h3><img src="${logoUrl}" alt="${llmName} Logo" class="llm-logo">${llmName}</h3>
            <p class="model-name">Model: ${modelName}</p>
        </div>
        <div class="response-content">
            <p>${responseText.replace(/\n/g, '<br>')}</p>
        </div>
        <div class="response-actions">
            <button class="btn btn-secondary btn-delegate">Delegate to Jules</button>
        </div>`;

    // Safely store the raw response text on the button element using a data attribute
    const delegateButton = card.querySelector('.btn-delegate');
    if (delegateButton) {
        delegateButton.dataset.response = responseText;
        delegateButton.dataset.llm = llmName;
    }

    responsesContainer.appendChild(card);
}

function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 6}s`;
        particle.style.animationDuration = `${Math.random() * 4 + 4}s`;
        container.appendChild(particle);
    }
}

function createMatrixRain() {
    const container = document.getElementById('matrixRain');
    if (!container) return;
    const chars = '01';
    for (let i = 0; i < 100; i++) {
        const char = document.createElement('div');
        char.style.position = 'absolute';
        char.style.left = `${Math.random() * 100}%`;
        char.style.animation = `matrix-fall ${Math.random() * 3 + 2}s linear infinite`;
        char.style.animationDelay = `${Math.random() * 3}s`;
        char.style.color = '#00ff88';
        char.style.fontFamily = 'monospace';
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        container.appendChild(char);
    }
    const keyframes = `@keyframes matrix-fall { 0% { transform: translateY(-100vh); opacity: 1; } 100% { transform: translateY(100vh); opacity: 0; } }`;
    const styleSheet = document.createElement("style");
    styleSheet.type = "text/css";
    styleSheet.innerText = keyframes;
    document.head.appendChild(styleSheet);
}