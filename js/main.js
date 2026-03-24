console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");
const lastUpdatedText = document.getElementById("lastUpdatedText");
const dailyAverageTableBody = document.getElementById("dailyAverageTableBody");
const radarRAndD = document.getElementById("radar-r-and-d");
const radarPolicy = document.getElementById("radar-policy");
const recommendedRead = document.getElementById("recommended-read");
const recommendedListen = document.getElementById("recommended-listen");

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
  if (!container || !items || items.length === 0) {
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