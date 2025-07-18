document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    createMatrixRain();
    const brainstormBtn = document.getElementById('brainstormBtn');
    const responsesContainer = document.getElementById('responses');
    const loadingIndicator = document.getElementById('loading');
    const matrixRain = document.getElementById('matrixRain');
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
            data.forEach(res => createResponseCard(res.llm, res.response));
        } catch (error) {
            console.error('Error fetching from backend:', error);
            createResponseCard('error', `An error occurred: ${error.message}`);
        } finally {
            loadingIndicator.classList.remove('active');
            matrixRain.classList.remove('active');
            brainstormBtn.disabled = false;
        }
    });
});
function createResponseCard(llm, responseText) {
    const responsesContainer = document.getElementById('responses');
    const card = document.createElement('div');
    card.className = `llm-response ${llm}`;
    const logoUrl = document.querySelector(`#${llm} + label img`)?.src || 'https://i.ibb.co/vzVvJ4G/error-icon.png';
    const llmName = llm.charAt(0).toUpperCase() + llm.slice(1);
    card.innerHTML = `
        <div class="response-header">
            <h3><img src="${logoUrl}" alt="${llmName} Logo" class="llm-logo">${llmName}</h3>
        </div>
        <div class="response-content">
            <p>${responseText.replace(/\n/g, '<br>')}</p>
        </div>`;
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
