console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");
const homepageChartCanvas = document.getElementById("homepageCarbonChart");
const lastUpdatedText = document.getElementById("lastUpdatedText");
const homepageChartUpdated = document.getElementById("homepageCarbonChartUpdated");
const dailyAverageTableBody = document.getElementById("dailyAverageTableBody");
const radarRAndD = document.getElementById("radar-r-and-d");
const radarPolicy = document.getElementById("radar-policy");
const recommendedRead = document.getElementById("recommended-read");
const recommendedListen = document.getElementById("recommended-listen");
const newsRadarLastUpdated = document.getElementById("newsRadarLastUpdated");
const brainDumpsContainer = document.getElementById("brainDumpsContainer");
const homepageBrainDumps = document.getElementById("homepageBrainDumps");
const homepageReportingPreview = document.getElementById("homepageReportingPreview");
const thoughtPiecesContainer = document.getElementById("thoughtPiecesContainer");
const homepageThoughtPieces = document.getElementById("homepageThoughtPieces");
const gridSnapshotUpdated = document.getElementById("gridSnapshotUpdated");
const snapshotPowerPrice = document.getElementById("snapshotPowerPrice");
const snapshotPowerPriceUnit = document.getElementById("snapshotPowerPriceUnit");
const snapshotCarbonIntensity = document.getElementById("snapshotCarbonIntensity");
const snapshotCarbonIntensityUnit = document.getElementById("snapshotCarbonIntensityUnit");
const snapshotDemand = document.getElementById("snapshotDemand");
const snapshotDemandUnit = document.getElementById("snapshotDemandUnit");
const snapshotGeneration = document.getElementById("snapshotGeneration");
const snapshotGenerationUnit = document.getElementById("snapshotGenerationUnit");
const generationMixVisual = document.getElementById("generationMixVisual");
const generationMixLegend = document.getElementById("generationMixLegend");

let generationMixChart;

const generationMixColours = {
  wind: "#0f766e",
  solar: "#f5b700",
  hydro: "#0ea5e9",
  nuclear: "#16a34a",
  biomass: "#65a30d",
  storage: "#14b8a6",
  gas: "#111827",
  imports: "#6b7280",
  coal: "#374151",
  other: "#cbd5e1"
};

function buildCarbonChart(canvas, chartData, isHomepagePreview = false) {
  if (!canvas) {
    return;
  }

  new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Actual",
          data: chartData.actual_values,
          borderWidth: 2,
          tension: 0.2
        },
        {
          label: "Forecast",
          data: chartData.forecast_values.map((value, index) => {
            return chartData.actual_values[index] !== null ? null : value;
          }),
          borderWidth: 2,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: !isHomepagePreview,
      plugins: {
        legend: {
          display: !isHomepagePreview
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: !isHomepagePreview,
            text: "gCO2/kWh"
          }
        },
        x: {
          title: {
            display: !isHomepagePreview,
            text: "Time"
          },
          ticks: {
            maxTicksLimit: isHomepagePreview ? 6 : 12
          }
        }
      }
    }
  });
}

function getSnapshotMetricState(metric) {
  if (!metric) {
    return {
      valueText: "Unavailable",
      unitText: "",
      hasNumericValue: false,
      isForecast: false
    };
  }

  const metricDisplay = metric.display || "";
  const isForecast = metricDisplay.toLowerCase().includes("(forecast)");
  const hasNumericValue = metric.value !== null && metric.value !== undefined && !Number.isNaN(Number(metric.value));

  if (!hasNumericValue) {
    return {
      valueText: metricDisplay || "Unavailable",
      unitText: "",
      hasNumericValue: false,
      isForecast
    };
  }

  const numericValue = Number(metric.value);
  let valueText = `${numericValue}`;

  if (metric.unit === "MW" || metric.unit === "GBP/MWh") {
    valueText = `${Math.round(numericValue).toLocaleString("en-GB")}`;
  } else if (metric.unit === "gCO2/kWh") {
    valueText = `${Math.round(numericValue)}`;
  }

  return {
    valueText,
    unitText: isForecast && metric.unit ? `${metric.unit} (forecast)` : (metric.unit || ""),
    hasNumericValue: true,
    isForecast
  };
}

function getGenerationMixColour(segment) {
  if (segment && segment.key && generationMixColours[segment.key]) {
    return generationMixColours[segment.key];
  }

  return segment.color || "#cbd5e1";
}

function sortGenerationMixSegments(segments) {
  const safeSegments = Array.isArray(segments) ? [...segments] : [];
  const sortBySize = (a, b) => b.percentage - a.percentage;

  const lowCarbonSegments = safeSegments
    .filter((segment) => segment.is_low_carbon)
    .sort(sortBySize);

  const nonLowCarbonSegments = safeSegments
    .filter((segment) => !segment.is_low_carbon)
    .sort(sortBySize);

  return [...lowCarbonSegments, ...nonLowCarbonSegments];
}

function updateCarbonIntensityKicker(metric) {
  const card = snapshotCarbonIntensity ? snapshotCarbonIntensity.closest(".grid-metric-card") : null;
  const kicker = card ? card.querySelector(".grid-metric-kicker") : null;

  if (!kicker) {
    return;
  }

  if (metric && metric.display && metric.display.toLowerCase().includes("(forecast)")) {
    kicker.textContent = "Forecast national GB carbon intensity";
    return;
  }

  kicker.textContent = "Actual national GB carbon intensity";
}

function updateSnapshotMetric(valueElement, unitElement, metric) {
  if (!valueElement) {
    return;
  }

  const card = valueElement.closest(".grid-metric-card");
  const metricState = getSnapshotMetricState(metric);

  if (card) {
    card.classList.remove("grid-metric-card-fallback", "grid-metric-card-forecast");

    if (!metricState.hasNumericValue) {
      card.classList.add("grid-metric-card-fallback");
    } else if (metricState.isForecast) {
      card.classList.add("grid-metric-card-forecast");
    }
  }

  valueElement.textContent = metricState.valueText;
  valueElement.classList.remove("loading-placeholder");
  valueElement.classList.toggle("grid-metric-value-fallback", !metricState.hasNumericValue);

  if (unitElement) {
    unitElement.textContent = metricState.unitText || "\u00A0";
    unitElement.classList.remove("loading-placeholder");
    unitElement.classList.toggle("grid-metric-unit-empty", !metricState.unitText);
  }
}

function renderGenerationMix(snapshotData) {
  if (!generationMixVisual) {
    return;
  }

  const mixData = snapshotData.generation_mix;

  if (!mixData || !Array.isArray(mixData.segments) || mixData.segments.length === 0) {
    generationMixVisual.textContent = "Generation mix unavailable right now.";

    if (generationMixLegend) {
      generationMixLegend.innerHTML = "<p class=\"loading-placeholder\">No generation mix breakdown available.</p>";
    }

    return;
  }

  const sortedSegments = sortGenerationMixSegments(mixData.segments);

  generationMixVisual.classList.remove("loading-placeholder");
  generationMixVisual.innerHTML = `
    <div class="generation-mix-chart-wrap">
      <canvas id="generationMixChart" class="generation-mix-canvas"></canvas>
      <div class="generation-mix-center">
        <p class="generation-mix-percentage">${mixData.low_carbon_percentage}%</p>
        <p class="generation-mix-caption">Low carbon</p>
      </div>
    </div>
  `;

  const chartCanvas = document.getElementById("generationMixChart");

  if (generationMixChart) {
    generationMixChart.destroy();
  }

  generationMixChart = new Chart(chartCanvas, {
    type: "doughnut",
    data: {
      labels: sortedSegments.map((segment) => segment.label),
      datasets: [
        {
          data: sortedSegments.map((segment) => segment.percentage),
          backgroundColor: sortedSegments.map((segment) => getGenerationMixColour(segment)),
          borderColor: "#ffffff",
          borderWidth: 4,
          hoverOffset: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "84%",
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      }
    }
  });

  if (generationMixLegend) {
    generationMixLegend.innerHTML = sortedSegments.map((segment) => `
      <div class="generation-mix-legend-item">
        <span class="generation-mix-swatch" style="background:${getGenerationMixColour(segment)};"></span>
        <span class="generation-mix-legend-label">${segment.label}</span>
        <span class="generation-mix-legend-value">${segment.percentage}%</span>
      </div>
    `).join("");
  }
}

if (chartCanvas || homepageChartCanvas) {
  fetch("data/carbon-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (lastUpdatedText) {
        lastUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
      }

      if (homepageChartUpdated) {
        homepageChartUpdated.textContent = `Last updated: ${chartData.last_updated}`;
      }

      if (dailyAverageTableBody && chartData.daily_average) {
        dailyAverageTableBody.innerHTML = "";

        chartData.daily_average.forEach((row) => {
          const tableRow = document.createElement("tr");

          const dateCell = document.createElement("td");
          dateCell.textContent = row.date;

          const valueCell = document.createElement("td");
          valueCell.textContent = Number(row.chart_value).toFixed(2);

          tableRow.appendChild(dateCell);
          tableRow.appendChild(valueCell);

          dailyAverageTableBody.appendChild(tableRow);
        });
      }

      buildCarbonChart(chartCanvas, chartData, false);
      buildCarbonChart(homepageChartCanvas, chartData, true);
    })
    .catch((error) => {
      console.error("Error loading chart data:", error);
    });
}

if (
  gridSnapshotUpdated ||
  snapshotPowerPrice ||
  snapshotCarbonIntensity ||
  snapshotDemand ||
  snapshotGeneration ||
  generationMixVisual
) {
  fetch("data/live-grid-snapshot.json")
    .then((response) => response.json())
    .then((snapshotData) => {
      if (gridSnapshotUpdated) {
        gridSnapshotUpdated.textContent = `Last updated: ${snapshotData.last_updated || "not available"}`;
        gridSnapshotUpdated.classList.remove("loading-placeholder");
      }

      updateSnapshotMetric(snapshotPowerPrice, snapshotPowerPriceUnit, snapshotData.power_price);
      updateSnapshotMetric(snapshotCarbonIntensity, snapshotCarbonIntensityUnit, snapshotData.carbon_intensity);
      updateSnapshotMetric(snapshotDemand, snapshotDemandUnit, snapshotData.demand);
      updateSnapshotMetric(snapshotGeneration, snapshotGenerationUnit, snapshotData.generation);
      updateCarbonIntensityKicker(snapshotData.carbon_intensity);
      renderGenerationMix(snapshotData);
    })
    .catch((error) => {
      console.error("Error loading live grid snapshot data:", error);
    });
}
function sortItemsByDate(items) {
  return [...items].sort((a, b) => new Date(b.date) - new Date(a.date));
}
function sortItemsByPublishedDate(items) {
  return [...items].sort((a, b) => {
    const dateA = a.published_at ? new Date(a.published_at) : new Date(0);
    const dateB = b.published_at ? new Date(b.published_at) : new Date(0);
    return dateB - dateA;
  });
}

function formatRadarMeta(item) {
  if (item.source && item.display_date) {
    return `${item.source} · ${item.display_date}`;
  }

  if (item.source) {
    return item.source;
  }

  if (item.display_date) {
    return item.display_date;
  }

  return "";
}

function renderRadarItems(container, items) {
  if (!container) {
    return;
  }

  if (!items || items.length === 0) {
    container.innerHTML = "<p>No items available right now.</p>";
    return;
  }

  const sortedItems = sortItemsByPublishedDate(items).slice(0, 5);

  container.innerHTML = "";

  sortedItems.forEach((item) => {
    const wrapper = document.createElement("article");
    wrapper.className = "radar-item";

    wrapper.innerHTML = `
      <h4><a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.headline}</a></h4>
      <p class="radar-meta">${formatRadarMeta(item)}</p>
    `;

    container.appendChild(wrapper);
  });
}

function renderRecommendation(container, item, labelText) {
  if (!container || !item) {
    return;
  }

  container.innerHTML = `
    <article class="recommendation-card">
      <p class="card-kicker">${labelText}</p>
      <h4><a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.title}</a></h4>
      <p class="recommendation-meta">${item.source}</p>
      <p>${item.description}</p>
    </article>
  `;
}

if (radarRAndD || radarPolicy) {
  fetch("data/news-radar.json")
    .then((response) => response.json())
    .then((newsData) => {
      if (newsRadarLastUpdated) {
        newsRadarLastUpdated.textContent = `Last updated: ${newsData.last_updated || "not available"}`;
      }

      renderRadarItems(radarRAndD, newsData.r_and_d);
      renderRadarItems(radarPolicy, newsData.policy);
    })
    .catch((error) => {
      console.error("Error loading news radar data:", error);
    });
}

if (recommendedRead || recommendedListen) {
  fetch("data/recommendations.json")
    .then((response) => response.json())
    .then((recommendationData) => {
      renderRecommendation(recommendedRead, recommendationData.recommended_read, "Recommended read");
      renderRecommendation(recommendedListen, recommendationData.recommended_listen, "Recommended listen");
    })
    .catch((error) => {
      console.error("Error loading recommendations data:", error);
    });
}
function renderBrainDumps(container, notes) {
  if (!container) {
    return;
  }

  if (!notes || notes.length === 0) {
    container.innerHTML = "<p>No notes available right now.</p>";
    return;
  }

  const sortedNotes = sortItemsByDate(notes);

  container.innerHTML = "";

  sortedNotes.forEach((note) => {
    const wrapper = document.createElement("article");
    wrapper.className = "brain-dump-card";

    const paragraphs = Array.isArray(note.content)
      ? note.content.map((paragraph) => `<p>${paragraph}</p>`).join("")
      : `<p>${note.content}</p>`;

    wrapper.innerHTML = `
      <div class="brain-dump-card-inner">
        <p class="card-kicker">Brain Dump</p>
        <h3>${note.title}</h3>
        <p class="brain-dump-meta">${note.date} · ${note.tag}</p>
        <div class="brain-dump-content">
          ${paragraphs}
        </div>
      </div>
    `;

    container.appendChild(wrapper);
  });
}
function renderHomepageBrainDumps(container, notes) {
  if (!container) {
    return;
  }

  if (!notes || notes.length === 0) {
    container.innerHTML = "<p>No Brain Dumps available right now.</p>";
    return;
  }

  const sortedNotes = sortItemsByDate(notes);

  container.innerHTML = "";

  sortedNotes.slice(0, 3).forEach((note) => {
    const wrapper = document.createElement("article");
    wrapper.className = "brain-dump-preview-card";

    const previewText = Array.isArray(note.content)
      ? note.content[0]
      : note.content;

    wrapper.innerHTML = `
  <p class="card-kicker">Preview</p>
  <h4>${note.title}</h4>
  <p class="brain-dump-meta">${note.date} · ${note.tag}</p>
  <p class="brain-dump-preview-text">${previewText}</p>
`;

    container.appendChild(wrapper);
  });
}
function renderHomepageReportingPreview(container, recommendations, newsData) {
  if (!container) {
    return;
  }

  const cards = [];

  if (recommendations && recommendations.recommended_read) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Recommended</p>
        <h4><a href="${recommendations.recommended_read.link}" target="_blank" rel="noopener noreferrer">Read</a></h4>
        <p class="reporting-preview-text">${recommendations.recommended_read.title}</p>
      </article>
    `);
  }

  if (recommendations && recommendations.recommended_listen) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Recommended</p>
        <h4><a href="${recommendations.recommended_listen.link}" target="_blank" rel="noopener noreferrer">Listen</a></h4>
        <p class="reporting-preview-text">${recommendations.recommended_listen.title}</p>
      </article>
    `);
  }

  if (newsData && newsData.r_and_d && newsData.r_and_d.length > 0) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Latest</p>
        <h4><a href="${newsData.r_and_d[0].link}" target="_blank" rel="noopener noreferrer">R&amp;D</a></h4>
        <p class="reporting-preview-text">${newsData.r_and_d[0].headline}</p>
      </article>
    `);
  }

  if (newsData && newsData.policy && newsData.policy.length > 0) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Latest</p>
        <h4><a href="${newsData.policy[0].link}" target="_blank" rel="noopener noreferrer">Policy</a></h4>
        <p class="reporting-preview-text">${newsData.policy[0].headline}</p>
      </article>
    `);
  }

  if (cards.length === 0) {
    container.innerHTML = "<p>No reporting preview available right now.</p>";
    return;
  }

  container.innerHTML = cards.join("");
}

function formatArticleDate(dateString) {
  const date = new Date(dateString);

  return date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long"
  });
}

function buildThoughtPieceCard(article) {
  const imageMarkup = article.image
    ? `
      <div class="thought-piece-card-image">
        <img src="${article.image}" alt="${article.title}">
      </div>
    `
    : "";

  const noImageClass = article.image ? "" : " thought-piece-card-no-image";

  return `
    <article class="thought-piece-card${noImageClass}">
      <div class="thought-piece-card-text">
        <p class="card-kicker">${article.author || "Oliver Branston"}</p>
        <h3><a href="${article.link}">${article.title}</a></h3>
        <p class="article-meta">${formatArticleDate(article.date)}</p>
        <p>${article.summary}</p>
      </div>
      ${imageMarkup}
    </article>
  `;
}

function renderThoughtPieces(container, articles) {
  if (!container) {
    return;
  }

  if (!articles || articles.length === 0) {
    container.innerHTML = "<p>No articles available right now.</p>";
    return;
  }

  const sortedArticles = sortItemsByDate(articles);

  const seriesOneArticles = sortedArticles.filter((article) => article.section === "series-one");
  const archiveArticles = sortedArticles.filter((article) => article.section === "archive");

  container.innerHTML = `
  <section class="thought-piece-section">
    <div class="thought-piece-section-heading">
      <p class="eyebrow">Series Two</p>
      <p>Coming soon</p>
    </div>
  </section>

  <section class="thought-piece-section">
    <div class="thought-piece-section-heading">
      <p class="eyebrow">Series One</p>
    </div>
    <div class="thought-piece-card-list">
      ${seriesOneArticles.map(buildThoughtPieceCard).join("")}
    </div>
  </section>

  <section class="thought-piece-section">
    <div class="thought-piece-section-heading">
      <p class="eyebrow">Archive</p>
    </div>
    <div class="thought-piece-card-list">
      ${archiveArticles.map(buildThoughtPieceCard).join("")}
    </div>
  </section>
`;
}

function renderHomepageThoughtPieces(container, articles) {
  if (!container) {
    return;
  }

  if (!articles || articles.length === 0) {
    container.innerHTML = "<p>No thought pieces available right now.</p>";
    return;
  }

  const sortedArticles = sortItemsByDate(articles);
  const featuredArticle = sortedArticles[0];
  const secondaryArticles = sortedArticles.slice(1, 3);

  container.innerHTML = `
    <article class="featured-thought-card">
      <div class="featured-thought-content">
        <p class="card-kicker">Most recent article</p>
        <h3><a href="${featuredArticle.link}">${featuredArticle.title}</a></h3>
        <p class="article-meta">${formatArticleDate(featuredArticle.date)} · ${featuredArticle.author || "Oliver Branston"}</p>
        <p>${featuredArticle.summary}</p>
      </div>
      <div class="featured-thought-image">
        <img src="${featuredArticle.image}" alt="${featuredArticle.title}">
      </div>
    </article>

    <div class="thought-list">
      ${secondaryArticles.map((article) => `
        <article class="compact-thought-card">
          <p class="card-kicker">Recent</p>
          <h4><a href="${article.link}">${article.title}</a></h4>
          <p class="article-meta">${formatArticleDate(article.date)} · ${article.author || "Oliver Branston"}</p>
        </article>
      `).join("")}
    </div>
  `;
}
if (brainDumpsContainer || homepageBrainDumps) {
  fetch("data/brain-dumps.json")
    .then((response) => response.json())
    .then((brainDumpData) => {
      renderBrainDumps(brainDumpsContainer, brainDumpData.notes);
      renderHomepageBrainDumps(homepageBrainDumps, brainDumpData.notes);
    })
    .catch((error) => {
      console.error("Error loading brain dump data:", error);
    });
}
if (homepageReportingPreview) {
  Promise.all([
    fetch("data/recommendations.json").then((response) => response.json()),
    fetch("data/news-radar.json").then((response) => response.json())
  ])
    .then(([recommendationData, newsData]) => {
      renderHomepageReportingPreview(
        homepageReportingPreview,
        recommendationData,
        newsData
      );
    })
    .catch((error) => {
      console.error("Error loading homepage reporting preview:", error);
    });
}
if (thoughtPiecesContainer || homepageThoughtPieces) {
  fetch("data/thought-pieces.json")
    .then((response) => response.json())
    .then((thoughtPiecesData) => {
      renderThoughtPieces(thoughtPiecesContainer, thoughtPiecesData.articles);
      renderHomepageThoughtPieces(homepageThoughtPieces, thoughtPiecesData.articles);
    })
    .catch((error) => {
      console.error("Error loading thought pieces data:", error);
    });
}
