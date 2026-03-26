console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");
const lastUpdatedText = document.getElementById("lastUpdatedText");
const dailyAverageTableBody = document.getElementById("dailyAverageTableBody");
const radarRAndD = document.getElementById("radar-r-and-d");
const radarPolicy = document.getElementById("radar-policy");
const recommendedRead = document.getElementById("recommended-read");
const recommendedListen = document.getElementById("recommended-listen");
const newsRadarLastUpdated = document.getElementById("newsRadarLastUpdated");
const brainDumpsContainer = document.getElementById("brainDumpsContainer");
const homepageBrainDumps = document.getElementById("homepageBrainDumps");
const homepageReportingPreview = document.getElementById("homepageReportingPreview");

if (chartCanvas) {
  fetch("data/carbon-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (lastUpdatedText) {
        lastUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
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
      new Chart(chartCanvas, {
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
          plugins: {
            legend: {
              display: true
            }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: "gCO2/kWh"
              }
            },
            x: {
              title: {
                display: true,
                text: "Time"
              }
            }
          }
        }
      });
    })
    .catch((error) => {
      console.error("Error loading chart data:", error);
    });
}
function renderRadarItems(container, items) {
  if (!container) {
    return;
  }

  if (!items || items.length === 0) {
    container.innerHTML = "<p>No items available right now.</p>";
    return;
  }

  container.innerHTML = "";

  items.forEach((item) => {
    const wrapper = document.createElement("article");
    wrapper.className = "radar-item";

    wrapper.innerHTML = `
      <h4><a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.headline}</a></h4>
      <p class="radar-meta">${item.source}</p>
      <p>${item.summary}</p>
    `;

    container.appendChild(wrapper);
  });
}

function renderRecommendation(container, item) {
  if (!container || !item) {
    return;
  }

  container.innerHTML = `
    <article class="recommendation-card">
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
      renderRecommendation(recommendedRead, recommendationData.recommended_read);
      renderRecommendation(recommendedListen, recommendationData.recommended_listen);
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

  container.innerHTML = "";

  notes.forEach((note) => {
    const wrapper = document.createElement("article");
    wrapper.className = "brain-dump-card";

    wrapper.innerHTML = `
      <h4>${note.title}</h4>
      <p class="brain-dump-meta">${note.date} · ${note.tag}</p>
      <p>${note.content}</p>
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

  container.innerHTML = "";

  notes.slice(0, 3).forEach((note) => {
    const wrapper = document.createElement("article");
    wrapper.className = "brain-dump-preview-card";

    wrapper.innerHTML = `
      <p class="card-kicker">Preview</p>
      <h4>${note.title}</h4>
      <p class="brain-dump-meta">${note.date} · ${note.tag}</p>
      <p>${note.content}</p>
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
        <p>${recommendations.recommended_read.title}</p>
      </article>
    `);
  }

  if (recommendations && recommendations.recommended_listen) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Recommended</p>
        <h4><a href="${recommendations.recommended_listen.link}" target="_blank" rel="noopener noreferrer">Listen</a></h4>
        <p>${recommendations.recommended_listen.title}</p>
      </article>
    `);
  }

  if (newsData && newsData.r_and_d && newsData.r_and_d.length > 0) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Latest</p>
        <h4><a href="${newsData.r_and_d[0].link}" target="_blank" rel="noopener noreferrer">R&amp;D</a></h4>
        <p>${newsData.r_and_d[0].headline}</p>
      </article>
    `);
  }

  if (newsData && newsData.policy && newsData.policy.length > 0) {
    cards.push(`
      <article class="reporting-preview-card">
        <p class="card-kicker">Latest</p>
        <h4><a href="${newsData.policy[0].link}" target="_blank" rel="noopener noreferrer">Policy</a></h4>
        <p>${newsData.policy[0].headline}</p>
      </article>
    `);
  }

  if (cards.length === 0) {
    container.innerHTML = "<p>No reporting preview available right now.</p>";
    return;
  }

  container.innerHTML = cards.join("");
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