from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Navigate to the application
        page.goto("http://localhost:5000")

        # 2. Take a screenshot of the initial layout
        page.screenshot(path="jules-scratch/verification/layout_before_results.png")

        # 3. Fill in the project name and description
        page.fill("#projectName", "Test Project")
        page.fill("#projectDescription", "This is a test project description.")

        # 4. Click the "Start Brainstorming" button
        page.click("#brainstormBtn")

        # 5. Wait for the responses to be generated
        expect(page.locator(".llm-response")).to_have_count(4, timeout=60000)

        # 6. Take a screenshot of the new layout
        page.screenshot(path="jules-scratch/verification/layout_after_results.png")

        browser.close()

if __name__ == "__main__":
    run_verification()
