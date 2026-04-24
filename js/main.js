console.log("The New Current loaded successfully");

const chartCanvas = document.getElementById("carbonChart");
const powerPriceChartCanvas = document.getElementById("powerPriceChart");
const generationMixOverTimeChartCanvas = document.getElementById("generationMixOverTimeChart");
const territorialEmissionsChartCanvas = document.getElementById("territorialEmissionsChart");
const consumptionEmissionsChartCanvas = document.getElementById("consumptionEmissionsChart");
const consumptionPerPersonChartCanvas = document.getElementById("consumptionPerPersonChart");
const historicalGenerationMixChartCanvas = document.getElementById("historicalGenerationMixChart");
const domesticElectricityBillChartCanvas = document.getElementById("domesticElectricityBillChart");
const gatewayConsumptionPerPersonChartCanvas = document.getElementById("gatewayConsumptionPerPersonChart");
const gatewayPowerPriceChartCanvas = document.getElementById("gatewayPowerPriceChart");
const homepageChartCanvas = document.getElementById("homepageCarbonChart");
const pageDataUpdated = document.getElementById("pageDataUpdated");
const lastUpdatedText = document.getElementById("lastUpdatedText");
const powerPriceUpdatedText = document.getElementById("powerPriceUpdatedText");
const generationMixOverTimeUpdatedText = document.getElementById("generationMixOverTimeUpdatedText");
const territorialEmissionsUpdatedText = document.getElementById("territorialEmissionsUpdatedText");
const consumptionEmissionsUpdatedText = document.getElementById("consumptionEmissionsUpdatedText");
const consumptionPerPersonUpdatedText = document.getElementById("consumptionPerPersonUpdatedText");
const historicalGenerationMixUpdatedText = document.getElementById("historicalGenerationMixUpdatedText");
const domesticElectricityBillUpdatedText = document.getElementById("domesticElectricityBillUpdatedText");
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
const gatewayGenerationMixVisual = document.getElementById("gatewayGenerationMixVisual");

let generationMixChart;
let gatewayGenerationMixChart;

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

const chartTextColour = "#3b4758";
const chartTitleColour = "#0f1724";
const chartGridColour = "rgba(198, 208, 221, 0.55)";
const chartFontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif';
const chartActualSeriesColour = "#2457ff";
const chartForecastSeriesColour = "#ff6384";

const generationMixLabelsPlugin = {
  id: "generationMixLabels",
  afterDatasetsDraw(chart) {
    const dataset = chart.data.datasets[0];
    const meta = chart.getDatasetMeta(0);
    const labelLayer = chart.canvas.parentNode.querySelector(".generation-mix-label-layer");

    if (!dataset || !meta || !meta.data || !labelLayer) {
      return;
    }

    labelLayer.innerHTML = "";

    meta.data.forEach((arc, index) => {
      const value = dataset.data[index];

      if (!value || value < 2) {
        return;
      }

      const label = chart.data.labels[index];
      const angle = (arc.startAngle + arc.endAngle) / 2;
      const x = arc.x + Math.cos(angle) * (arc.outerRadius + 16);
      const y = arc.y + Math.sin(angle) * (arc.outerRadius + 16);
      const isRightSide = Math.cos(angle) >= 0;
      const labelNode = document.createElement("div");
      labelNode.className = `generation-mix-chart-label ${isRightSide ? "generation-mix-chart-label-right" : "generation-mix-chart-label-left"}`;
      labelNode.style.left = `${x}px`;
      labelNode.style.top = `${y}px`;
      labelNode.textContent = label;
      labelLayer.appendChild(labelNode);
    });
  }
};

function buildCarbonChart(canvas, chartData, isHomepagePreview = false) {
  if (!canvas) {
    return;
  }

  const hasForecastSeries = Array.isArray(chartData.forecast_values)
    && chartData.forecast_values.some((value) => value !== null && value !== undefined);

  const datasets = [
    {
      label: "Actual",
      data: chartData.actual_values,
      borderColor: chartActualSeriesColour,
      backgroundColor: chartActualSeriesColour,
      pointRadius: isHomepagePreview ? 0 : 2.5,
      pointHoverRadius: isHomepagePreview ? 4 : 6,
      pointHitRadius: isHomepagePreview ? 10 : 14,
      borderWidth: 2,
      tension: 0.2
    }
  ];

  if (hasForecastSeries) {
    datasets.push({
      label: "Forecast",
      data: chartData.forecast_values.map((value, index) => {
        return chartData.actual_values[index] !== null ? null : value;
      }),
      borderColor: chartForecastSeriesColour,
      backgroundColor: chartForecastSeriesColour,
      pointRadius: isHomepagePreview ? 0 : 2.5,
      pointHoverRadius: isHomepagePreview ? 4 : 6,
      pointHitRadius: isHomepagePreview ? 10 : 14,
      borderWidth: 2,
      tension: 0.2
    });
  }

  new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: isHomepagePreview ? 0 : 8
        }
      },
      plugins: {
        legend: {
          display: !isHomepagePreview,
          position: "top",
          align: "center",
          labels: {
            color: chartTextColour,
            padding: 18,
            font: {
              family: chartFontFamily,
              size: 13,
              weight: "400"
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: {
            color: chartGridColour
          },
          ticks: {
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          },
          title: {
            display: !isHomepagePreview,
            text: "gCO2/kWh",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          }
        },
        x: {
          grid: {
            color: chartGridColour
          },
          title: {
            display: !isHomepagePreview,
            text: "Time",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          },
          ticks: {
            maxTicksLimit: isHomepagePreview ? 6 : 12,
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          }
        }
      }
    }
  });
}

function buildPowerPriceChart(canvas, chartData) {
  if (!canvas) {
    return;
  }

  const hasForecastSeries = Array.isArray(chartData.forecast_values)
    && chartData.forecast_values.some((value) => value !== null && value !== undefined);

  const datasets = [
    {
      label: "Actual",
      data: chartData.actual_values,
      borderColor: chartActualSeriesColour,
      backgroundColor: chartActualSeriesColour,
      pointRadius: 2.5,
      pointHoverRadius: 6,
      pointHitRadius: 14,
      borderWidth: 2,
      tension: 0.2
    }
  ];

  if (hasForecastSeries) {
    datasets.push({
      label: "Forecast",
      data: chartData.forecast_values,
      borderColor: chartForecastSeriesColour,
      backgroundColor: chartForecastSeriesColour,
      pointRadius: 2.5,
      pointHoverRadius: 6,
      pointHitRadius: 14,
      borderWidth: 2,
      tension: 0.2
    });
  }

  new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 8
        }
      },
      plugins: {
        legend: {
          position: "top",
          align: "center",
          labels: {
            color: chartTextColour,
            padding: 18,
            font: {
              family: chartFontFamily,
              size: 13,
              weight: "400"
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: {
            color: chartGridColour
          },
          ticks: {
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          },
          title: {
            display: true,
            text: "GBP/MWh",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          }
        },
        x: {
          grid: {
            color: chartGridColour
          },
          title: {
            display: true,
            text: "Time",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          },
          ticks: {
            maxTicksLimit: 12,
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          }
        }
      }
    }
  });
}

function buildGenerationMixOverTimeChart(canvas, chartData) {
  if (!canvas) {
    return;
  }

  const visibleDatasets = (chartData.datasets || []).filter(isVisibleGenerationMixDataset);

  const datasets = visibleDatasets.map((dataset) => ({
    label: dataset.label,
    data: dataset.values,
    borderColor: getGenerationMixColour({ key: dataset.key }),
    backgroundColor: getGenerationMixColour({ key: dataset.key }),
    fill: true,
    stack: "generation-mix",
    borderWidth: 1.5,
    pointRadius: 0,
    pointHoverRadius: 4,
    pointHitRadius: 10,
    tension: 0.2
  }));

  new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      layout: {
        padding: {
          top: 8
        }
      },
      plugins: {
        legend: {
          position: "top",
          align: "center",
          labels: {
            color: chartTextColour,
            padding: 18,
            font: {
              family: chartFontFamily,
              size: 13,
              weight: "400"
            }
          }
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.dataset.label}: ${context.raw.toFixed(1)}%`;
            }
          }
        }
      },
      scales: {
        y: {
          stacked: true,
          min: 0,
          max: 100,
          grid: {
            color: chartGridColour
          },
          ticks: {
            color: chartTextColour,
            callback(value) {
              return `${value}%`;
            },
            font: {
              family: chartFontFamily,
              size: 12
            }
          },
          title: {
            display: true,
            text: "Share of generation (%)",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          }
        },
        x: {
          stacked: true,
          grid: {
            color: chartGridColour
          },
          title: {
            display: true,
            text: "Time",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          },
          ticks: {
            maxTicksLimit: 12,
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          }
        }
      }
    }
  });
}

function buildAnnualSeriesChart(canvas, labels, values, options) {
  if (!canvas) {
    return;
  }

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: options.label,
          data: values,
          borderColor: options.colour,
          backgroundColor: options.colour,
          pointRadius: 2.5,
          pointHoverRadius: 6,
          pointHitRadius: 14,
          borderWidth: 2,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 8
        }
      },
      plugins: {
        legend: {
          position: "top",
          align: "center",
          labels: {
            color: chartTextColour,
            padding: 18,
            font: {
              family: chartFontFamily,
              size: 13,
              weight: "400"
            }
          }
        },
        tooltip: {
          callbacks: {
            label(context) {
              const rawValue = Number(context.raw);
              const formattedValue = options.decimals === 0
                ? rawValue.toFixed(0)
                : rawValue.toFixed(options.decimals || 1);

              return `${context.dataset.label}: ${formattedValue} ${options.unit}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: options.beginAtZero ?? false,
          min: options.min,
          max: options.max,
          grid: {
            color: chartGridColour
          },
          ticks: {
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          },
          title: {
            display: true,
            text: options.axisTitle,
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          }
        },
        x: {
          grid: {
            color: chartGridColour
          },
          title: {
            display: true,
            text: "Year",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          },
          ticks: {
            maxTicksLimit: 10,
            color: chartTextColour,
            font: {
              family: chartFontFamily,
              size: 12
            }
          }
        }
      }
    }
  });
}

function getAlignedAnnualTickOptions(labels) {
  const years = (labels || [])
    .map((label) => Number(label))
    .filter((year) => Number.isFinite(year));

  if (years.length === 0) {
    return {};
  }

  const firstYear = years[0];
  const lastYear = years[years.length - 1];
  const range = lastYear - firstYear;
  const interval = range > 28 ? 5 : (range > 14 ? 3 : 2);

  return {
    maxRotation: 0,
    autoSkip: false,
    color: chartTextColour,
    callback(value, index) {
      const year = Number(labels[index]);

      if (
        index === 0
        || index === labels.length - 1
        || (Number.isFinite(year) && year % interval === 0)
      ) {
        return labels[index];
      }

      return "";
    },
    font: {
      family: chartFontFamily,
      size: 12
    }
  };
}

function getAnnualGenerationStackData(chartData) {
  const renewableValues = chartData.generation_mix.renewable_percentage || [];
  const lowCarbonValues = chartData.generation_mix.low_carbon_percentage || [];
  const fossilValues = chartData.generation_mix.fossil_percentage || [];

  return {
    renewable: renewableValues.map((value) => Number(value) || 0),
    otherLowCarbon: lowCarbonValues.map((value, index) => {
      return Math.max((Number(value) || 0) - (Number(renewableValues[index]) || 0), 0);
    }),
    fossil: fossilValues.map((value) => Number(value) || 0),
    other: lowCarbonValues.map((value, index) => {
      const lowCarbonValue = Number(value) || 0;
      const fossilValue = Number(fossilValues[index]) || 0;

      return Math.max(100 - lowCarbonValue - fossilValue, 0);
    })
  };
}

function buildHistoricalGenerationMixChart(canvas, chartData) {
  if (!canvas) {
    return;
  }

  const stackData = getAnnualGenerationStackData(chartData);

  new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Renewable",
          data: stackData.renewable,
          borderColor: "#16a34a",
          backgroundColor: "#16a34a",
          fill: true,
          stack: "annual-generation-mix",
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHitRadius: 14,
          borderWidth: 1.5,
          tension: 0.2
        },
        {
          label: "Other low-carbon",
          data: stackData.otherLowCarbon,
          borderColor: "#2457ff",
          backgroundColor: "#2457ff",
          fill: true,
          stack: "annual-generation-mix",
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHitRadius: 14,
          borderWidth: 1.5,
          tension: 0.2
        },
        {
          label: "Fossil",
          data: stackData.fossil,
          borderColor: "#374151",
          backgroundColor: "#374151",
          fill: true,
          stack: "annual-generation-mix",
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHitRadius: 14,
          borderWidth: 1.5,
          tension: 0.2
        },
        {
          label: "Other",
          data: stackData.other,
          borderColor: "#cbd5e1",
          backgroundColor: "#cbd5e1",
          fill: true,
          stack: "annual-generation-mix",
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHitRadius: 14,
          borderWidth: 1.5,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      layout: {
        padding: {
          top: 8
        }
      },
      plugins: {
        title: {
          display: true,
          text: "GB electricity generation mix",
          color: chartTitleColour,
          font: {
            family: chartFontFamily,
            size: 14,
            weight: "700"
          }
        },
        legend: {
          position: "top",
          align: "center",
          labels: {
            color: chartTextColour,
            padding: 18,
            font: {
              family: chartFontFamily,
              size: 13,
              weight: "400"
            }
          }
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.dataset.label}: ${Number(context.raw).toFixed(1)}%`;
            }
          }
        }
      },
      scales: {
        y: {
          stacked: true,
          min: 0,
          max: 100,
          grid: {
            color: chartGridColour
          },
          ticks: {
            color: chartTextColour,
            callback(value) {
              return `${value}%`;
            },
            font: {
              family: chartFontFamily,
              size: 12
            }
          },
          title: {
            display: true,
            text: "Share of generation (%)",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          }
        },
        x: {
          stacked: true,
          grid: {
            color: chartGridColour
          },
          title: {
            display: true,
            text: "Year",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          },
          ticks: getAlignedAnnualTickOptions(chartData.labels)
        }
      }
    }
  });
}

function buildDomesticElectricityBillChart(canvas, chartData) {
  if (!canvas) {
    return;
  }

  new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Standard electricity bill (nominal GBP)",
          data: chartData.domestic_electricity_bill.bill_gbp_nominal,
          borderColor: chartActualSeriesColour,
          backgroundColor: chartActualSeriesColour,
          pointRadius: 2.5,
          pointHoverRadius: 6,
          pointHitRadius: 14,
          borderWidth: 2,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      layout: {
        padding: {
          top: 8
        }
      },
      plugins: {
        title: {
          display: true,
          text: "Standard annual domestic electricity bill",
          color: chartTitleColour,
          font: {
            family: chartFontFamily,
            size: 14,
            weight: "700"
          }
        },
        legend: {
          position: "top",
          align: "center",
          labels: {
            color: chartTextColour,
            padding: 18,
            font: {
              family: chartFontFamily,
              size: 13,
              weight: "400"
            }
          }
        },
        tooltip: {
          callbacks: {
            label(context) {
              const value = Number(context.raw).toLocaleString("en-GB", {
                maximumFractionDigits: 0
              });

              return `${context.dataset.label}: GBP ${value}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: {
            color: chartGridColour
          },
          ticks: {
            color: chartTextColour,
            callback(value) {
              return `GBP ${Number(value).toLocaleString("en-GB")}`;
            },
            font: {
              family: chartFontFamily,
              size: 12
            }
          },
          title: {
            display: true,
            text: "Nominal GBP per year",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          }
        },
        x: {
          grid: {
            color: chartGridColour
          },
          title: {
            display: true,
            text: "Year",
            color: chartTitleColour,
            font: {
              family: chartFontFamily,
              size: 12,
              weight: "400"
            }
          },
          ticks: getAlignedAnnualTickOptions(chartData.labels)
        }
      }
    }
  });
}

function buildGatewayLineChart(canvas, labels, values, options) {
  if (!canvas) {
    return;
  }

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          data: values,
          borderColor: options.colour,
          backgroundColor: options.colour,
          pointRadius: 0,
          pointHoverRadius: 0,
          pointHitRadius: 8,
          borderWidth: 2.25,
          tension: 0.22
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      },
      scales: {
        y: {
          display: false,
          beginAtZero: options.beginAtZero ?? false,
          min: options.min,
          max: options.max,
          grid: {
            display: false
          },
          border: {
            display: false
          }
        },
        x: {
          display: false,
          grid: {
            display: false
          },
          border: {
            display: false
          }
        }
      },
      elements: {
        line: {
          capBezierPoints: true
        }
      }
    }
  });
}

function getSharedAnnualAxisBounds(seriesList) {
  const numericValues = seriesList
    .flat()
    .filter((value) => value !== null && value !== undefined && !Number.isNaN(Number(value)))
    .map((value) => Number(value));

  if (numericValues.length === 0) {
    return {};
  }

  const minValue = Math.min(...numericValues);
  const maxValue = Math.max(...numericValues);
  const range = maxValue - minValue;
  const padding = Math.max(range * 0.08, 20);

  return {
    min: Math.max(0, Math.floor((minValue - padding) / 10) * 10),
    max: Math.ceil((maxValue + padding) / 10) * 10
  };
}

function getCurrentHalfHourLabel() {
  const now = new Date();
  const utcHours = now.getUTCHours().toString().padStart(2, "0");
  const utcMinutes = now.getUTCMinutes();
  const roundedMinutes = utcMinutes < 30 ? "00" : "30";

  return `${utcHours}:${roundedMinutes}`;
}

function getCarbonMetricFromChartData(chartData) {
  if (!chartData || !Array.isArray(chartData.labels)) {
    return null;
  }

  const currentLabel = getCurrentHalfHourLabel();
  let slotIndex = chartData.labels.lastIndexOf(currentLabel);

  if (slotIndex === -1) {
    slotIndex = chartData.labels.length - 1;
  }

  if (slotIndex >= 0) {
    const actualValue = chartData.actual_values?.[slotIndex];

    if (actualValue !== null && actualValue !== undefined) {
      return {
        value: actualValue,
        unit: "gCO2/kWh",
        display: `${Math.round(actualValue)} gCO2/kWh`
      };
    }
  }

  for (let index = Math.min(slotIndex, chartData.labels.length - 1); index >= 0; index -= 1) {
    const actualValue = chartData.actual_values?.[index];

    if (actualValue !== null && actualValue !== undefined) {
      return {
        value: actualValue,
        unit: "gCO2/kWh",
        display: `${Math.round(actualValue)} gCO2/kWh`
      };
    }
  }

  return {
    value: null,
    unit: "gCO2/kWh",
    display: "Carbon intensity unavailable"
  };
}

function getPowerPriceMetricFromChartData(chartData) {
  if (!chartData || !Array.isArray(chartData.labels)) {
    return null;
  }

  for (let index = chartData.labels.length - 1; index >= 0; index -= 1) {
    const actualValue = chartData.actual_values?.[index];

    if (actualValue !== null && actualValue !== undefined) {
      return {
        value: actualValue,
        unit: "GBP/MWh",
        display: `${Math.round(actualValue)} GBP/MWh`
      };
    }
  }

  return {
    value: null,
    unit: "GBP/MWh",
    display: "Price unavailable"
  };
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

function isVisibleGenerationMixSegment(segment) {
  return Boolean(
    segment
    && segment.key
    && generationMixColours[segment.key]
    && Number(segment.percentage) > 0
  );
}

function isVisibleGenerationMixDataset(dataset) {
  return Boolean(
    dataset
    && dataset.key
    && generationMixColours[dataset.key]
    && Array.isArray(dataset.values)
    && dataset.values.some((value) => value !== null && value !== undefined && Number(value) > 0)
  );
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
    return;
  }

  const sortedSegments = sortGenerationMixSegments(
    mixData.segments.filter(isVisibleGenerationMixSegment)
  );

  if (sortedSegments.length === 0) {
    generationMixVisual.textContent = "Generation mix unavailable right now.";
    return;
  }

  generationMixVisual.classList.remove("loading-placeholder");
  generationMixVisual.innerHTML = `
    <div class="generation-mix-chart-wrap">
      <canvas id="generationMixChart" class="generation-mix-canvas"></canvas>
      <div class="generation-mix-label-layer"></div>
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
    },
    plugins: [generationMixLabelsPlugin]
  });
}

function renderGatewayGenerationMix(snapshotData) {
  if (!gatewayGenerationMixVisual) {
    return;
  }

  const mixData = snapshotData.generation_mix;

  if (!mixData || !Array.isArray(mixData.segments) || mixData.segments.length === 0) {
    gatewayGenerationMixVisual.textContent = "Generation mix unavailable right now.";
    return;
  }

  const sortedSegments = sortGenerationMixSegments(
    mixData.segments.filter(isVisibleGenerationMixSegment)
  );

  if (sortedSegments.length === 0) {
    gatewayGenerationMixVisual.textContent = "Generation mix unavailable right now.";
    return;
  }

  gatewayGenerationMixVisual.classList.remove("loading-placeholder");
  gatewayGenerationMixVisual.innerHTML = `
    <div class="gateway-generation-mix-chart-wrap">
      <canvas id="gatewayGenerationMixChart" class="gateway-generation-mix-canvas"></canvas>
      <div class="gateway-generation-mix-center">
        <p class="gateway-generation-mix-percentage">${mixData.low_carbon_percentage}%</p>
        <p class="gateway-generation-mix-caption">Low carbon</p>
      </div>
    </div>
  `;

  const chartCanvas = document.getElementById("gatewayGenerationMixChart");

  if (gatewayGenerationMixChart) {
    gatewayGenerationMixChart.destroy();
  }

  gatewayGenerationMixChart = new Chart(chartCanvas, {
    type: "doughnut",
    data: {
      labels: sortedSegments.map((segment) => segment.label),
      datasets: [
        {
          data: sortedSegments.map((segment) => segment.percentage),
          backgroundColor: sortedSegments.map((segment) => getGenerationMixColour(segment)),
          borderColor: "#ffffff",
          borderWidth: 3,
          hoverOffset: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      cutout: "78%",
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      }
    }
  });
}

if (chartCanvas || homepageChartCanvas) {
  fetch("data/carbon-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (pageDataUpdated) {
        pageDataUpdated.textContent = `Last updated: ${chartData.last_updated}`;
        pageDataUpdated.classList.remove("loading-placeholder");
      }

      if (lastUpdatedText) {
        lastUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
      }

      if (homepageChartUpdated) {
        homepageChartUpdated.textContent = `Last updated: ${chartData.last_updated}`;
      }

      buildCarbonChart(chartCanvas, chartData, false);
      buildCarbonChart(homepageChartCanvas, chartData, true);

      if (snapshotCarbonIntensity) {
        const carbonMetric = getCarbonMetricFromChartData(chartData);
        updateSnapshotMetric(snapshotCarbonIntensity, snapshotCarbonIntensityUnit, carbonMetric);
      }
    })
    .catch((error) => {
      console.error("Error loading chart data:", error);
    });
}

if (powerPriceChartCanvas) {
  fetch("data/power-price-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (powerPriceUpdatedText) {
        powerPriceUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        powerPriceUpdatedText.classList.remove("loading-placeholder");
      }

      buildPowerPriceChart(powerPriceChartCanvas, chartData);
      buildGatewayLineChart(
        gatewayPowerPriceChartCanvas,
        chartData.labels,
        chartData.actual_values,
        {
          colour: "#2457ff"
        }
      );

      if (snapshotPowerPrice) {
        const powerPriceMetric = getPowerPriceMetricFromChartData(chartData);
        updateSnapshotMetric(snapshotPowerPrice, snapshotPowerPriceUnit, powerPriceMetric);
      }
    })
    .catch((error) => {
      console.error("Error loading power price chart data:", error);
    });
}

if (generationMixOverTimeChartCanvas) {
  fetch("data/generation-mix-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (generationMixOverTimeUpdatedText) {
        generationMixOverTimeUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        generationMixOverTimeUpdatedText.classList.remove("loading-placeholder");
      }

      buildGenerationMixOverTimeChart(generationMixOverTimeChartCanvas, chartData);
    })
    .catch((error) => {
      console.error("Error loading generation mix chart data:", error);
    });
}

if (
  territorialEmissionsChartCanvas
  || consumptionEmissionsChartCanvas
  || consumptionPerPersonChartCanvas
) {
  fetch("data/uk-carbon-accounting-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      const sharedEmissionsAxisBounds = getSharedAnnualAxisBounds([
        chartData.territorial_emissions_mtco2e,
        chartData.consumption_emissions_mtco2e
      ]);

      if (territorialEmissionsUpdatedText) {
        territorialEmissionsUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        territorialEmissionsUpdatedText.classList.remove("loading-placeholder");
      }

      if (consumptionEmissionsUpdatedText) {
        consumptionEmissionsUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        consumptionEmissionsUpdatedText.classList.remove("loading-placeholder");
      }

      if (consumptionPerPersonUpdatedText) {
        consumptionPerPersonUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        consumptionPerPersonUpdatedText.classList.remove("loading-placeholder");
      }

      buildAnnualSeriesChart(
        territorialEmissionsChartCanvas,
        chartData.labels,
        chartData.territorial_emissions_mtco2e,
        {
          label: "Territorial emissions",
          colour: "#2457ff",
          unit: "MtCO2e",
          axisTitle: "MtCO2e",
          decimals: 1,
          beginAtZero: true,
          ...sharedEmissionsAxisBounds
        }
      );

      buildAnnualSeriesChart(
        consumptionEmissionsChartCanvas,
        chartData.labels,
        chartData.consumption_emissions_mtco2e,
        {
          label: "Consumption-based emissions",
          colour: "#2457ff",
          unit: "MtCO2e",
          axisTitle: "MtCO2e",
          decimals: 1,
          beginAtZero: true,
          ...sharedEmissionsAxisBounds
        }
      );

      buildAnnualSeriesChart(
        consumptionPerPersonChartCanvas,
        chartData.labels,
        chartData.consumption_per_person_tco2e,
        {
          label: "Consumption emissions per person",
          colour: "#2457ff",
          unit: "tCO2e per person",
          axisTitle: "tCO2e per person",
          decimals: 2
        }
      );

      buildGatewayLineChart(
        gatewayConsumptionPerPersonChartCanvas,
        chartData.labels,
        chartData.consumption_per_person_tco2e,
        {
          colour: "#2457ff"
        }
      );
    })
    .catch((error) => {
      console.error("Error loading UK carbon accounting chart data:", error);
    });
}

if (historicalGenerationMixChartCanvas || domesticElectricityBillChartCanvas) {
  fetch("data/green-generation-bills-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (historicalGenerationMixUpdatedText) {
        historicalGenerationMixUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        historicalGenerationMixUpdatedText.classList.remove("loading-placeholder");
      }

      if (domesticElectricityBillUpdatedText) {
        domesticElectricityBillUpdatedText.textContent = `Last updated: ${chartData.last_updated}`;
        domesticElectricityBillUpdatedText.classList.remove("loading-placeholder");
      }

      buildHistoricalGenerationMixChart(historicalGenerationMixChartCanvas, chartData);
      buildDomesticElectricityBillChart(domesticElectricityBillChartCanvas, chartData);
    })
    .catch((error) => {
      console.error("Error loading green generation and bill chart data:", error);

      if (historicalGenerationMixUpdatedText) {
        historicalGenerationMixUpdatedText.textContent = "Last updated: data unavailable";
        historicalGenerationMixUpdatedText.classList.remove("loading-placeholder");
      }

      if (domesticElectricityBillUpdatedText) {
        domesticElectricityBillUpdatedText.textContent = "Last updated: data unavailable";
        domesticElectricityBillUpdatedText.classList.remove("loading-placeholder");
      }
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

      updateSnapshotMetric(snapshotDemand, snapshotDemandUnit, snapshotData.demand);
      updateSnapshotMetric(snapshotGeneration, snapshotGenerationUnit, snapshotData.generation);
      renderGenerationMix(snapshotData);
      renderGatewayGenerationMix(snapshotData);
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
