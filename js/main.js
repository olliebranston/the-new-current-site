console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");
const lastUpdatedText = document.getElementById("lastUpdatedText");

if (chartCanvas) {
  fetch("data/carbon-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (lastUpdatedText) {
        lastUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
      }
      new Chart(chartCanvas, {
        type: "line",
        data: {
          labels: chartData.labels,
          datasets: [
            {
              label: "Carbon intensity",
              data: chartData.values,
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