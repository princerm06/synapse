const saveButton = document.getElementById("save-page");
const statusText = document.getElementById("status");

saveButton.addEventListener("click", async () => {
  statusText.textContent = "Saving...";

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });

    const [result] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const selectors = [
          "article",
          "main",
          '[role="main"]',
        ];

        let content = "";

        for (const selector of selectors) {
          const element = document.querySelector(selector);

          if (element) {
            const text = element.innerText.trim();

            if (text.length >= 200) {
              content = text;
              break;
            }
          }
        }

        if (!content) {
          content = document.body.innerText.trim();
        }

        return {
          url: window.location.href,
          title: document.title,
          content: content,
        };
      },
    });

    const page = result.result;

    const response = await fetch("http://127.0.0.1:8000/pages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(page),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    statusText.textContent = "Saved to Synapse!";
  } catch (error) {
    console.error(error);
    statusText.textContent = "Failed to save page.";
  }
});