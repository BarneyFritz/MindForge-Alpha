// Expose the modal-opening function to the global window object
// This allows other scripts (like script.js) to call it.
window.openJulesModal = function(responseText, llmName) {
    const modal = document.getElementById('julesModal');
    if (!modal) {
        console.error('Jules modal element not found.');
        return;
    }

    const issueTitleInput = document.getElementById('issueTitle');
    const issueBodyTextarea = document.getElementById('issueBody');
    const projectName = document.getElementById('projectName').value.trim();

    if (!projectName) {
        alert('Please enter a Project Name before delegating a task.');
        return;
    }

    // Pre-fill the issue title and body
    issueTitleInput.value = `[${projectName}] - Task from ${llmName}`;
    issueBodyTextarea.value = responseText;

    // Show the modal
    modal.style.display = 'block';
};

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('julesModal');
    if (!modal) return;

    const closeModalButtons = modal.querySelectorAll('.close-button');
    const confirmBtn = document.getElementById('confirmDelegateBtn');
    const responsesContainer = document.getElementById('responses');

    function closeModal() {
        modal.style.display = 'none';
        const confirmBtn = document.getElementById('confirmDelegateBtn');
        // Reset button state
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '🚀 Create Issue';
    }

    // --- Event Listeners for the modal itself ---

    closeModalButtons.forEach(button => {
        button.addEventListener('click', closeModal);
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // --- Event Listeners for buttons that open the modal ---

    // Use event delegation on the container for the original "Delegate" buttons
    if (responsesContainer) {
        responsesContainer.addEventListener('click', (event) => {
            const delegateButton = event.target.closest('.btn-delegate');
            if (delegateButton) {
                const responseText = delegateButton.dataset.response;
                const llmName = delegateButton.dataset.llm;
                window.openJulesModal(responseText, llmName);
            }
        });
    }

    // Handle the final confirmation and API call to create the issue
    if (confirmBtn) {
        confirmBtn.addEventListener('click', async () => {
            const title = document.getElementById('issueTitle').value.trim();
            const body = document.getElementById('issueBody').value;

            if (!title) {
                alert('Please enter an issue title.');
                return;
            }

            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<div class="spinner-small"></div> Creating...';

            try {
                const response = await fetch('/api/jules/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, body }),
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Failed to delegate task.');
                }

                alert(`Successfully created issue #${result.issue_number}!\nURL: ${result.issue_url}`);
                closeModal();

            } catch (error) {
                console.error('Delegation Error:', error);
                alert(`Error: ${error.message}`);
                // Re-enable the button on failure
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '🚀 Create Issue';
            }
        });
    }
});
