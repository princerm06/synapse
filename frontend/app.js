const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const statusText = document.getElementById("status");
const resultsContainer = document.getElementById("results");

const API_URL = "http://127.0.0.1:8000";

function getSourceLabel(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "Saved webpage";
  }
}

function createResultCard(result) {
  const resultElement = document.createElement("article");
  resultElement.className = "result";

  const sourceRow = document.createElement("div");
  sourceRow.className = "result-source";

  const sourceDot = document.createElement("span");
  sourceDot.className = "source-dot";
  sourceDot.setAttribute("aria-hidden", "true");

  const sourceName = document.createElement("span");
  sourceName.textContent = getSourceLabel(result.url);

  sourceRow.append(sourceDot, sourceName);

  const title = document.createElement("h2");
  const titleLink = document.createElement("a");
  titleLink.href = result.url;
  titleLink.target = "_blank";
  titleLink.rel = "noopener noreferrer";
  titleLink.textContent = result.title || getSourceLabel(result.url);
  title.appendChild(titleLink);

  const contextLabel = document.createElement("p");
  contextLabel.className = "context-label";
  contextLabel.textContent = "Why this matched";

  const content = document.createElement("p");
  content.className = "result-content";
  content.textContent = result.excerpt;

  const footer = document.createElement("div");
  footer.className = "result-footer";

  const link = document.createElement("a");
  link.className = "open-link";
  link.href = result.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "Open original →";

  footer.appendChild(link);
  resultElement.append(sourceRow, title, contextLabel, content, footer);

  return resultElement;
}

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = searchInput.value.trim();

  if (!query) {
    return;
  }

  statusText.textContent = "Searching your saved knowledge…";
  resultsContainer.innerHTML = "";
  searchButton.disabled = true;
  searchButton.textContent = "Searching…";

  try {
    const response = await fetch(
      `${API_URL}/search?query=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const results = await response.json();

    if (results.length === 0) {
      statusText.textContent = `No saved pages matched “${query}”.`;
      return;
    }

    statusText.textContent = `${results.length} saved ${results.length === 1 ? "page" : "pages"} found`;

    for (const result of results) {
      resultsContainer.appendChild(createResultCard(result));
    }
  } catch (error) {
    console.error(error);
    statusText.textContent =
      "Search failed. Make sure the Synapse backend is running.";
  } finally {
    searchButton.disabled = false;
    searchButton.textContent = "Search";
  }
});
