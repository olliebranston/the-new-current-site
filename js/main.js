console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");
const lastUpdatedText = document.getElementById("lastUpdatedText");
const dailyAverageTableBody = document.getElementById("dailyAverageTableBody");

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