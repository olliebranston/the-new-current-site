console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");

if (chartCanvas) {
  const labels = [
    "00:00",
    "01:00",
    "02:00",
    "03:00",
    "04:00",
    "05:00",
    "06:00",
    "07:00",
    "08:00",
    "09:00"
  ];

  const carbonIntensityValues = [128, 121, 119, 115, 117, 125, 138, 149, 156, 152];

  new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Carbon intensity",
          data: carbonIntensityValues,
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
}
