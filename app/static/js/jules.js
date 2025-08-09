document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('julesModal');
    // Ensure modal exists before proceeding
    if (!modal) return;

    const closeModalButtons = modal.querySelectorAll('.close-button');
    const confirmBtn = document.getElementById('confirmDelegateBtn');
    const issueTitleInput = document.getElementById('issueTitle');
    const issueBodyTextarea = document.getElementById('issueBody');
    const responsesContainer = document.getElementById('responses');

    let activeResponse = null;
    let activeLlm = null;
    let projectName = '';

    // --- Modal Logic ---
    function openModal() {
        // Get the project name from the input field when the modal is opened
        projectName = document.getElementById('projectName').value.trim();
        if (!projectName) {
            alert('Please enter a Project Name before delegating a task.');
            return;
        }

        // Pre-fill the issue title
        issueTitleInput.value = `[${projectName}] - Task delegated from ${activeLlm}`;
        issueBodyTextarea.value = activeResponse;
        modal.style.display = 'block';
    }

    function closeModal() {
        modal.style.display = 'none';
        activeResponse = null;
        activeLlm = null;
        // Reset button state
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '🚀 Create Issue';
    }

    // --- Event Listeners ---

    // Use event delegation on the container for the dynamically created "Delegate" buttons
    if (responsesContainer) {
        responsesContainer.addEventListener('click', (event) => {
            const delegateButton = event.target.closest('.btn-delegate');
            if (delegateButton) {
                activeResponse = delegateButton.dataset.response;
                activeLlm = delegateButton.dataset.llm;
                openModal();
            }
        });
    }

    closeModalButtons.forEach(button => {
        button.addEventListener('click', closeModal);
    });

    // Close modal if user clicks outside of the modal content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Handle the final confirmation and API call
    if (confirmBtn) {
        confirmBtn.addEventListener('click', async () => {
            const title = issueTitleInput.value.trim();
            const body = issueBodyTextarea.value;

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
