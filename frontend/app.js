const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const statusText = document.getElementById("status");
const resultsContainer = document.getElementById("results");

const API_URL = "http://127.0.0.1:8000";


searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = searchInput.value.trim();

  if (!query) {
    return;
  }

  statusText.textContent = "Searching...";
  resultsContainer.innerHTML = "";

  try {
    const response = await fetch(
      `${API_URL}/search?query=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const results = await response.json();

    if (results.length === 0) {
      statusText.textContent = "No results found.";
      return;
    }

    statusText.textContent = `${results.length} results`;

    for (const result of results) {
      const resultElement = document.createElement("article");
      resultElement.className = "result";

      const title = document.createElement("h2");
      title.textContent = result.title;

      const meta = document.createElement("div");
      meta.className = "result-meta";
      meta.textContent = `Similarity: ${result.similarity.toFixed(3)}`;

      const content = document.createElement("p");
      content.className = "result-content";
      content.textContent = result.excerpt;

      const link = document.createElement("a");
      link.href = result.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Open source →";

      resultElement.append(title, meta, content, link);
      resultsContainer.appendChild(resultElement);
    }
  } catch (error) {
    console.error(error);
    statusText.textContent =
      "Search failed. Make sure the Synapse backend is running.";
  }
});
