
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
const pageDataUpdated = document.getElementById("pageDataUpdated");
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

    const labelsBySide = {
      left: [],
      right: []
    };
    const minimumLabelGap = 18;

    meta.data.forEach((arc, index) => {
      const value = Number(dataset.data[index]);

      if (!Number.isFinite(value) || value <= 0) {
        return;
      }

      const label = chart.data.labels[index];
      const angle = (arc.startAngle + arc.endAngle) / 2;
      const x = arc.x + Math.cos(angle) * (arc.outerRadius + 16);
      const y = arc.y + Math.sin(angle) * (arc.outerRadius + 16);
      const isRightSide = Math.cos(angle) >= 0;

      labelsBySide[isRightSide ? "right" : "left"].push({
        label,
        x,
        y,
        isRightSide
      });
    });

    Object.values(labelsBySide).forEach((labels) => {
      labels
        .sort((a, b) => a.y - b.y)
        .forEach((labelPosition, index) => {
          if (index > 0) {
            const previousLabel = labels[index - 1];
            labelPosition.y = Math.max(labelPosition.y, previousLabel.y + minimumLabelGap);
          }

          const labelNode = document.createElement("div");
          labelNode.className = `generation-mix-chart-label ${labelPosition.isRightSide ? "generation-mix-chart-label-right" : "generation-mix-chart-label-left"}`;
          labelNode.style.left = `${labelPosition.x}px`;
          labelNode.style.top = `${labelPosition.y}px`;
          labelNode.textContent = labelPosition.label;
          labelLayer.appendChild(labelNode);
        });
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

function renderCompactGenerationMix(visualElement, snapshotData, currentChart, chartId) {
  if (!visualElement) {
    return currentChart;
  }

  const mixData = snapshotData.generation_mix;

  if (!mixData || !Array.isArray(mixData.segments) || mixData.segments.length === 0) {
    visualElement.textContent = "Generation mix unavailable right now.";
    return currentChart;
  }

  const sortedSegments = sortGenerationMixSegments(
    mixData.segments.filter(isVisibleGenerationMixSegment)
  );

  if (sortedSegments.length === 0) {
    visualElement.textContent = "Generation mix unavailable right now.";
    return currentChart;
  }

  visualElement.classList.remove("loading-placeholder");
  visualElement.innerHTML = `
    <div class="gateway-generation-mix-chart-wrap">
      <canvas id="${chartId}" class="gateway-generation-mix-canvas"></canvas>
      <div class="gateway-generation-mix-center">
        <p class="gateway-generation-mix-percentage">${mixData.low_carbon_percentage}%</p>
        <p class="gateway-generation-mix-caption">Low carbon</p>
      </div>
    </div>
  `;

  const chartCanvas = document.getElementById(chartId);

  if (currentChart) {
    currentChart.destroy();
  }

  return new Chart(chartCanvas, {
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

function renderGatewayGenerationMix(snapshotData) {
  gatewayGenerationMixChart = renderCompactGenerationMix(
    gatewayGenerationMixVisual,
    snapshotData,
    gatewayGenerationMixChart,
    "gatewayGenerationMixChart"
  );
}

if (chartCanvas) {
  fetch("data/carbon-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      if (pageDataUpdated) {
        pageDataUpdated.textContent = `Last updated: ${chartData.last_updated}`;
        pageDataUpdated.classList.remove("loading-placeholder");
      }

      buildCarbonChart(chartCanvas, chartData, false);

      if (snapshotCarbonIntensity) {
        const carbonMetric = getCarbonMetricFromChartData(chartData);
        updateSnapshotMetric(snapshotCarbonIntensity, snapshotCarbonIntensityUnit, carbonMetric);
      }
    })
    .catch((error) => {
      console.error("Error loading chart data:", error);
    });
}

if (powerPriceChartCanvas || gatewayPowerPriceChartCanvas) {
  fetch("data/power-price-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
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
  || gatewayConsumptionPerPersonChartCanvas
) {
  fetch("data/uk-carbon-accounting-chart-data.json")
    .then((response) => response.json())
    .then((chartData) => {
      const sharedEmissionsAxisBounds = getSharedAnnualAxisBounds([
        chartData.territorial_emissions_mtco2e,
        chartData.consumption_emissions_mtco2e
      ]);

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
      buildHistoricalGenerationMixChart(historicalGenerationMixChartCanvas, chartData);
      buildDomesticElectricityBillChart(domesticElectricityBillChartCanvas, chartData);
    })
    .catch((error) => {
      console.error("Error loading green generation and bill chart data:", error);
    });
}

if (
  snapshotPowerPrice ||
  snapshotCarbonIntensity ||
  snapshotDemand ||
  snapshotGeneration ||
  generationMixVisual ||
  gatewayGenerationMixVisual
) {
  fetch("data/live-grid-snapshot.json")
    .then((response) => response.json())
    .then((snapshotData) => {
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

function isSafeExternalUrl(url) {
  if (!url || typeof url !== "string") {
    return false;
  }

  try {
    const parsedUrl = new URL(url);
    return parsedUrl.protocol === "https:" || parsedUrl.protocol === "http:";
  } catch (error) {
    return false;
  }
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  element.textContent = text || "";
  return element;
}

function createSafeExternalLink(url, text) {
  if (!isSafeExternalUrl(url)) {
    return document.createTextNode(text || "");
  }

  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = text || "";
  return link;
}

function renderEmptyMessage(container, message) {
  container.replaceChildren(createTextElement("p", "", message));
}

function renderRadarItems(container, items) {
  if (!container) {
    return;
  }

  if (!items || items.length === 0) {
    renderEmptyMessage(container, "No items available right now.");
    return;
  }

  const sortedItems = sortItemsByPublishedDate(items).slice(0, 5);

  container.replaceChildren();

  sortedItems.forEach((item) => {
    const wrapper = document.createElement("article");
    wrapper.className = "radar-item";
    const title = document.createElement("h4");
    const meta = createTextElement("p", "radar-meta", formatRadarMeta(item));

    title.appendChild(createSafeExternalLink(item.link, item.headline));
    wrapper.append(title, meta);
    container.appendChild(wrapper);
  });
}

function renderRecommendation(container, item, labelText) {
  if (!container || !item) {
    return;
  }

  const card = document.createElement("article");
  card.className = "recommendation-card";

  const kicker = createTextElement("p", "card-kicker recommendation-card-kicker", labelText);
  const title = document.createElement("h4");
  title.className = "recommendation-card-title";
  title.appendChild(createSafeExternalLink(item.link, item.title));
  const source = createTextElement("p", "recommendation-meta recommendation-card-source", item.source);
  const description = createTextElement("p", "recommendation-card-description", item.description);

  card.append(kicker, title, source, description);
  container.replaceChildren(card);
}

if (radarRAndD || radarPolicy) {
  fetch("data/news-radar.json")
    .then((response) => response.json())
    .then((newsData) => {
      if (newsRadarLastUpdated) {
        newsRadarLastUpdated.textContent = `Last updated: ${newsData.last_updated || "not available"}`;
        newsRadarLastUpdated.classList.remove("loading-placeholder");
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
const COPY_ICON_SVG = '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';

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

    const contentArr = Array.isArray(note.content) ? note.content : [note.content];
    const paragraphs = contentArr.map((p) => `<p>${escapeHtml(p)}</p>`).join("");

    wrapper.innerHTML = `
      <div class="brain-dump-card-inner">
        <p class="card-kicker">Brain Dump</p>
        <div class="brain-dump-card-header">
          <h3>${escapeHtml(note.title)}</h3>
          <button class="brain-dump-copy-btn" type="button" aria-label="Copy note">${COPY_ICON_SVG} Copy</button>
        </div>
        <p class="brain-dump-meta">${note.date} · ${note.tag}</p>
        <div class="brain-dump-content">
          ${paragraphs}
        </div>
      </div>
    `;

    const copyBtn = wrapper.querySelector(".brain-dump-copy-btn");
    copyBtn.addEventListener("click", async () => {
      const text = `${note.title}\n\n${contentArr.join("\n\n")}`;
      try {
        await navigator.clipboard.writeText(text);
        copyBtn.innerHTML = `${COPY_ICON_SVG} Copied!`;
        setTimeout(() => { copyBtn.innerHTML = `${COPY_ICON_SVG} Copy`; }, 2000);
      } catch { /* clipboard not available */ }
    });

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
    cards.push({
      kicker: "Recommended",
      title: "Read",
      link: recommendations.recommended_read.link,
      text: recommendations.recommended_read.title
    });
  }

  if (recommendations && recommendations.recommended_listen) {
    cards.push({
      kicker: "Recommended",
      title: "Listen",
      link: recommendations.recommended_listen.link,
      text: recommendations.recommended_listen.title
    });
  }

  if (newsData && newsData.r_and_d && newsData.r_and_d.length > 0) {
    cards.push({
      kicker: "Latest",
      title: "R&D",
      link: newsData.r_and_d[0].link,
      text: newsData.r_and_d[0].headline
    });
  }

  if (newsData && newsData.policy && newsData.policy.length > 0) {
    cards.push({
      kicker: "Latest",
      title: "Policy",
      link: newsData.policy[0].link,
      text: newsData.policy[0].headline
    });
  }

  if (cards.length === 0) {
    renderEmptyMessage(container, "No reporting preview available right now.");
    return;
  }

  container.replaceChildren();

  cards.forEach((cardData) => {
    const card = document.createElement("article");
    card.className = "reporting-preview-card";

    const kicker = createTextElement("p", "card-kicker", cardData.kicker);
    const title = document.createElement("h4");
    title.appendChild(createSafeExternalLink(cardData.link, cardData.title));
    const text = createTextElement("p", "reporting-preview-text", cardData.text);

    card.append(kicker, title, text);
    container.appendChild(card);
  });
}

function formatArticleDate(dateString) {
  const date = new Date(dateString);

  return date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long"
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const BOOKMARKS_KEY = "tnc-bookmarks";

function getBookmarks() {
  try { return new Set(JSON.parse(localStorage.getItem(BOOKMARKS_KEY) || "[]")); } catch { return new Set(); }
}

function saveBookmarks(set) {
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify([...set]));
}

function toggleBookmark(link) {
  const bookmarks = getBookmarks();
  if (bookmarks.has(link)) { bookmarks.delete(link); } else { bookmarks.add(link); }
  saveBookmarks(bookmarks);
  return bookmarks.has(link);
}

function estimateReadingTime(text) {
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 220));
}

const BOOKMARK_ICON_SVG = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>';

function buildThoughtPieceCard(article) {
  const safeTitle = escapeHtml(article.title);
  const safeSummary = escapeHtml(article.summary);
  const isBookmarked = getBookmarks().has(article.link);

  const imageMarkup = article.image
    ? `
      <div class="thought-piece-card-image">
        <img src="${article.image}" alt="${safeTitle}" loading="lazy">
      </div>
    `
    : "";

  const noImageClass = article.image ? "" : " thought-piece-card-no-image";

  const isRead = getReadArticles().has(article.link);
  const featuredBadge = article.featured ? '<span class="card-featured-badge">Featured</span>' : "";
  const readBadge = isRead ? '<span class="card-read-badge" title="Read">✓</span>' : "";

  return `
    <article class="thought-piece-card${noImageClass}" data-article-link="${article.link}">
      <div class="thought-piece-card-text">
        <div class="card-kicker-row">
          <p class="card-kicker">${article.author || "Oliver Branston"}</p>
          <div class="card-badges">${featuredBadge}${readBadge}<button class="bookmark-btn${isBookmarked ? " active" : ""}" data-link="${article.link}" type="button" aria-label="${isBookmarked ? "Remove bookmark" : "Save article"}">${BOOKMARK_ICON_SVG}</button></div>
        </div>
        <h3><a href="${article.link}">${safeTitle}</a></h3>
        <p class="article-meta">${formatArticleDate(article.date)}</p>
        <p>${safeSummary}</p>
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

  const seriesTwoArticles = sortedArticles.filter((article) => article.section === "series-two");
  const seriesOneArticles = sortedArticles.filter((article) => article.section === "series-one");
  const archiveArticles = sortedArticles.filter((article) => article.section === "archive");

  container.innerHTML = `
  <section class="thought-piece-section">
    <div class="thought-piece-section-heading">
      <p class="eyebrow">Series Two</p>
    </div>
    <div class="thought-piece-card-list">
      ${seriesTwoArticles.map(buildThoughtPieceCard).join("")}
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
      if (brainDumpsContainer) {
        initBrainDumpsPage(brainDumpsContainer, brainDumpData.notes);
      }
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
      if (thoughtPiecesContainer) {
        initThoughtPiecesPage(thoughtPiecesContainer, thoughtPiecesData.articles);
      }
      renderHomepageThoughtPieces(homepageThoughtPieces, thoughtPiecesData.articles);
    })
    .catch((error) => {
      console.error("Error loading thought pieces data:", error);
    });
}

/* ─── Dark mode ─────────────────────────────────────────────────── */

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

function initThemeToggle() {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = savedTheme || (prefersDark ? "dark" : "light");
  applyTheme(theme);

  const toggle = document.getElementById("themeToggle");
  if (!toggle) return;

  toggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
  });
}

initThemeToggle();

/* ─── Reading progress bar ─────────────────────────────────────── */

function initReadingProgress() {
  const isArticle = document.body.closest("body") && document.querySelector(".article-content");
  if (!isArticle) return;

  const bar = document.createElement("div");
  bar.className = "reading-progress";
  bar.setAttribute("role", "progressbar");
  bar.setAttribute("aria-label", "Reading progress");
  document.body.prepend(bar);

  function updateProgress() {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (window.scrollY / docHeight) * 100 : 0;
    bar.style.width = `${Math.min(100, progress)}%`;
  }

  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();
}

initReadingProgress();

/* ─── Back to top button ───────────────────────────────────────── */

function initBackToTop() {
  const btn = document.createElement("button");
  btn.className = "back-to-top";
  btn.setAttribute("aria-label", "Back to top");
  btn.setAttribute("type", "button");
  btn.innerHTML = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
  document.body.appendChild(btn);

  function onScroll() {
    btn.classList.toggle("visible", window.scrollY > 320);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  btn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  onScroll();
}

initBackToTop();

/* ─── Thought pieces search and filter ─────────────────────────── */

function parseUrlState() {
  const raw = location.hash.slice(1);
  if (!raw) return { q: "", topics: [] };
  try {
    const params = new URLSearchParams(raw);
    return {
      q: params.get("q") || "",
      topics: params.get("topics") ? params.get("topics").split(",").filter(Boolean) : []
    };
  } catch { return { q: "", topics: [] }; }
}

function serializeUrlState(query, activeTopics) {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  const topicsArr = [...activeTopics].filter((t) => t !== "All" && t !== "Saved");
  if (topicsArr.length) params.set("topics", topicsArr.join(","));
  const str = params.toString();
  history.replaceState(null, "", location.pathname + (str ? "#" + str : ""));
}

function initThoughtPiecesPage(container, articles) {
  if (!container) return;

  const sortedArticles = sortItemsByDate(articles);
  const topicSet = Array.from(new Set(sortedArticles.map((a) => a.topic).filter(Boolean))).sort();
  const initialState = parseUrlState();

  let activeTopics = initialState.topics.length > 0 ? new Set(initialState.topics) : new Set(["All"]);
  let searchQuery = initialState.q;
  let showSavedOnly = false;

  const searchWrap = document.createElement("div");
  searchWrap.className = "tp-search-bar";
  searchWrap.innerHTML = `
    <div class="tp-search-input-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        type="search"
        class="tp-search-input"
        id="tpSearchInput"
        placeholder="Search articles…"
        aria-label="Search articles"
        autocomplete="off"
        value="${escapeHtml(searchQuery)}"
      />
    </div>
    <div class="tp-filter-chips" id="tpFilterChips">
      <button class="tp-filter-chip${activeTopics.has("All") ? " active" : ""}" data-topic="All" type="button">All</button>
      <button class="tp-filter-chip tp-saved-chip" data-topic="Saved" type="button">${BOOKMARK_ICON_SVG} Saved</button>
      ${topicSet.map((topic) => `
        <button class="tp-filter-chip${activeTopics.has(topic) ? " active" : ""}" data-topic="${topic}" type="button">${topic}</button>
      `).join("")}
    </div>
  `;

  const resultCount = document.createElement("p");
  resultCount.className = "tp-result-count";
  resultCount.setAttribute("aria-live", "polite");
  searchWrap.appendChild(resultCount);

  container.parentNode.insertBefore(searchWrap, container);

  const searchInput = document.getElementById("tpSearchInput");
  const chipsContainer = document.getElementById("tpFilterChips");

  function filterArticles() {
    const query = searchQuery.toLowerCase().trim();
    const filterAll = activeTopics.has("All") && !showSavedOnly;
    const bookmarks = showSavedOnly ? getBookmarks() : null;

    return sortedArticles.filter((article) => {
      if (showSavedOnly && !bookmarks.has(article.link)) return false;
      const topicMatch = filterAll || activeTopics.has(article.topic);
      const textMatch = !query || (
        article.title.toLowerCase().includes(query) ||
        (article.summary || "").toLowerCase().includes(query) ||
        (article.author || "").toLowerCase().includes(query)
      );
      return topicMatch && textMatch;
    });
  }

  function render() {
    const filtered = filterArticles();
    const total = sortedArticles.length;
    const isFiltered = searchQuery.trim() || !activeTopics.has("All") || showSavedOnly;
    resultCount.textContent = isFiltered ? `Showing ${filtered.length} of ${total} articles` : "";

    if (filtered.length === 0) {
      const msg = showSavedOnly
        ? "No saved articles yet. Click the bookmark icon on any article to save it."
        : "No articles match your search.";
      container.innerHTML = `<p class="tp-no-results">${msg}</p>`;
      return;
    }

    const seriesTwoArticles = filtered.filter((a) => a.section === "series-two");
    const seriesOneArticles = filtered.filter((a) => a.section === "series-one");
    const archiveArticles = filtered.filter((a) => a.section === "archive");

    const sections = [
      { label: "Series Two", items: seriesTwoArticles },
      { label: "Series One", items: seriesOneArticles },
      { label: "Archive", items: archiveArticles }
    ].filter((s) => s.items.length > 0);

    container.innerHTML = sections.map((s) => `
      <section class="thought-piece-section">
        <div class="thought-piece-section-heading">
          <p class="eyebrow">${s.label}</p>
        </div>
        <div class="thought-piece-card-list">
          ${s.items.map(buildThoughtPieceCard).join("")}
        </div>
      </section>
    `).join("");
  }

  function syncChipStates() {
    chipsContainer.querySelectorAll(".tp-filter-chip").forEach((c) => {
      if (c.dataset.topic === "Saved") {
        c.classList.toggle("active", showSavedOnly);
      } else {
        c.classList.toggle("active", !showSavedOnly && activeTopics.has(c.dataset.topic));
      }
    });
  }

  searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value;
    serializeUrlState(searchQuery, activeTopics);
    render();
  });

  chipsContainer.addEventListener("click", (e) => {
    const chip = e.target.closest(".tp-filter-chip");
    if (!chip) return;
    const topic = chip.dataset.topic;

    if (topic === "Saved") {
      showSavedOnly = !showSavedOnly;
      if (showSavedOnly) activeTopics = new Set(["All"]);
    } else if (topic === "All") {
      showSavedOnly = false;
      activeTopics = new Set(["All"]);
    } else {
      showSavedOnly = false;
      activeTopics.delete("All");
      if (activeTopics.has(topic)) {
        activeTopics.delete(topic);
        if (activeTopics.size === 0) activeTopics.add("All");
      } else {
        activeTopics.add(topic);
      }
    }

    syncChipStates();
    serializeUrlState(searchQuery, activeTopics);
    render();
  });

  container.addEventListener("click", (e) => {
    const btn = e.target.closest(".bookmark-btn");
    if (!btn) return;
    const link = btn.dataset.link;
    const isNowBookmarked = toggleBookmark(link);
    btn.classList.toggle("active", isNowBookmarked);
    btn.setAttribute("aria-label", isNowBookmarked ? "Remove bookmark" : "Save article");
    if (showSavedOnly) render();
  });

  render();
}

/* ─── Article page enhancements ─────────────────────────────────── */

function initArticlePageFeatures() {
  const articleEl = document.querySelector(".article-content");
  if (!articleEl) return;

  const articleHeader = articleEl.querySelector(".article-header");
  const pagePath = location.pathname.replace(/^.*\/articles\//, "articles/");

  // Reading time
  const bodyText = articleEl.textContent || "";
  const minutes = estimateReadingTime(bodyText);

  // Article bookmark (resolve link relative to articles/ folder)
  const articleLink = pagePath;
  const isBookmarked = getBookmarks().has(articleLink);

  // Topic chip
  const topic = articleEl.dataset.topic;
  if (topic && articleHeader) {
    const topicLink = document.createElement("a");
    topicLink.className = "article-topic-chip";
    topicLink.href = `../thought-pieces.html#topics=${encodeURIComponent(topic)}`;
    topicLink.textContent = topic;
    const kicker = articleHeader.querySelector(".article-kicker");
    if (kicker) kicker.after(topicLink);
    else articleHeader.prepend(topicLink);
  }

  // Build actions row below header
  const actionsRow = document.createElement("div");
  actionsRow.className = "article-actions-row";
  actionsRow.innerHTML = `
    <span class="reading-time-badge">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      ${minutes} min read
    </span>
    <button class="article-bookmark-btn${isBookmarked ? " active" : ""}" id="articleBookmarkBtn" type="button" aria-label="${isBookmarked ? "Remove bookmark" : "Save article"}">
      ${BOOKMARK_ICON_SVG}
      <span>${isBookmarked ? "Saved" : "Save"}</span>
    </button>
    <button class="article-share-btn" id="articleShareBtn" type="button">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
      Copy link
    </button>
  `;

  if (articleHeader) {
    articleHeader.after(actionsRow);
  }

  // Bookmark toggle
  const bookmarkBtn = document.getElementById("articleBookmarkBtn");
  if (bookmarkBtn) {
    bookmarkBtn.addEventListener("click", () => {
      const nowBookmarked = toggleBookmark(articleLink);
      bookmarkBtn.classList.toggle("active", nowBookmarked);
      bookmarkBtn.setAttribute("aria-label", nowBookmarked ? "Remove bookmark" : "Save article");
      bookmarkBtn.querySelector("span").textContent = nowBookmarked ? "Saved" : "Save";
      bookmarkBtn.querySelector("svg").style.fill = nowBookmarked ? "currentColor" : "none";
    });
  }

  // Share button
  const shareBtn = document.getElementById("articleShareBtn");
  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const originalHTML = shareBtn.innerHTML;
      try {
        await navigator.clipboard.writeText(location.href);
        shareBtn.textContent = "Copied!";
        setTimeout(() => { shareBtn.innerHTML = originalHTML; }, 2000);
      } catch {
        shareBtn.innerHTML = originalHTML;
      }
    });
  }

  // Table of contents
  const headings = [...articleEl.querySelectorAll("section h2")];
  if (headings.length >= 3) {
    headings.forEach((h, i) => {
      if (!h.id) h.id = `section-${i}`;
    });

    const toc = document.createElement("nav");
    toc.className = "article-toc";
    toc.setAttribute("aria-label", "Table of contents");
    toc.innerHTML = `
      <p class="article-toc-title">Contents</p>
      <ol class="article-toc-list">
        ${headings.map((h) => `<li><a href="#${h.id}">${escapeHtml(h.textContent)}</a></li>`).join("")}
      </ol>
    `;

    const sections = articleEl.querySelectorAll("section");
    if (sections.length >= 2) {
      sections[0].after(toc);
    }
  }
}

initArticlePageFeatures();

/* ─── Brain dumps page search ───────────────────────────────────── */

function initBrainDumpsPage(container, notes) {
  if (!container) return;

  const sortedNotes = sortItemsByDate(notes);
  const tags = ["All", ...Array.from(new Set(sortedNotes.map((n) => n.tag).filter(Boolean))).sort()];

  let searchQuery = "";
  let activeTag = "All";

  const searchWrap = document.createElement("div");
  searchWrap.className = "tp-search-bar";
  searchWrap.innerHTML = `
    <div class="tp-search-input-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        type="search"
        class="tp-search-input bd-search-input"
        id="bdSearchInput"
        placeholder="Search notes…"
        aria-label="Search notes"
        autocomplete="off"
      />
    </div>
    <div class="tp-filter-chips" id="bdFilterChips">
      ${tags.map((tag) => `
        <button class="tp-filter-chip${tag === "All" ? " active" : ""}" data-tag="${tag}" type="button">${tag}</button>
      `).join("")}
    </div>
  `;

  container.parentNode.insertBefore(searchWrap, container);

  const searchInput = document.getElementById("bdSearchInput");
  const chipsContainer = document.getElementById("bdFilterChips");

  function render() {
    const query = searchQuery.toLowerCase().trim();

    const filtered = sortedNotes.filter((note) => {
      const tagMatch = activeTag === "All" || note.tag === activeTag;
      const text = [note.title, note.tag, ...(Array.isArray(note.content) ? note.content : [note.content])].join(" ").toLowerCase();
      const textMatch = !query || text.includes(query);
      return tagMatch && textMatch;
    });

    if (filtered.length === 0) {
      container.innerHTML = '<p class="tp-no-results">No notes match your search.</p>';
      return;
    }

    container.innerHTML = "";
    filtered.forEach((note) => {
      const wrapper = document.createElement("article");
      wrapper.className = "brain-dump-card";
      const paragraphs = Array.isArray(note.content)
        ? note.content.map((p) => `<p>${escapeHtml(p)}</p>`).join("")
        : `<p>${escapeHtml(note.content)}</p>`;
      wrapper.innerHTML = `
        <div class="brain-dump-card-inner">
          <p class="card-kicker">Brain Dump</p>
          <h3>${escapeHtml(note.title)}</h3>
          <p class="brain-dump-meta">${note.date} · ${note.tag}</p>
          <div class="brain-dump-content">${paragraphs}</div>
        </div>
      `;
      container.appendChild(wrapper);
    });
  }

  searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value;
    render();
  });

  chipsContainer.addEventListener("click", (e) => {
    const chip = e.target.closest(".tp-filter-chip");
    if (!chip) return;
    activeTag = chip.dataset.tag;
    chipsContainer.querySelectorAll(".tp-filter-chip").forEach((c) => {
      c.classList.toggle("active", c.dataset.tag === activeTag);
    });
    render();
  });

  render();
}

/* ─── Keyboard shortcuts ────────────────────────────────────────── */

function initKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    const tag = (e.target.tagName || "").toLowerCase();
    const isEditing = tag === "input" || tag === "textarea" || e.target.isContentEditable;

    if (e.key === "Escape" && isEditing) {
      e.target.blur();
    }
  });
}

initKeyboardShortcuts();

/* ─── Accessibility: main-content skip target ───────────────────── */

(function setMainId() {
  const mainEl = document.querySelector("main");
  if (mainEl && !mainEl.id) mainEl.id = "main-content";
})();

/* ─── Scroll fade animations ────────────────────────────────────── */

function initScrollAnimations() {
  if (!window.IntersectionObserver) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const TARGETS = ".thought-piece-card, .brain-dump-card, .grid-metric-card, .generation-mix-panel, .data-preview-card, .recommendation-card, .radar-item";

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-in");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -30px 0px" });

  function observeNew(root) {
    root.querySelectorAll(TARGETS).forEach((el) => {
      if (!el.classList.contains("animate-in")) {
        el.classList.add("animate-fade");
        observer.observe(el);
      }
    });
  }

  observeNew(document);

  const mutObs = new MutationObserver((mutations) => {
    mutations.forEach((m) => {
      m.addedNodes.forEach((node) => {
        if (node.nodeType === 1) observeNew(node);
      });
    });
  });

  mutObs.observe(document.body, { childList: true, subtree: true });
}

initScrollAnimations();

/* ─── Global command palette ────────────────────────────────────── */

function initCommandPalette() {
  let overlay = null;
  let input = null;
  let resultsEl = null;
  let focusedIndex = -1;
  let allItems = [];
  let dataLoaded = false;

  const ARTICLE_ICON = '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>';
  const BRAIN_ICON = '<svg viewBox="0 0 24 24"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.16z"/></svg>';

  const isArticlePage = location.pathname.includes("/articles/");
  const prefix = isArticlePage ? "../" : "";

  async function loadData() {
    if (dataLoaded) return;
    try {
      const [tpData, bdData] = await Promise.all([
        fetch(`${prefix}data/thought-pieces.json`).then((r) => r.json()),
        fetch(`${prefix}data/brain-dumps.json`).then((r) => r.json())
      ]);

      const articles = sortItemsByDate(tpData.articles || []).map((a) => ({
        type: "article",
        title: a.title,
        meta: `${a.topic || ""} · ${formatArticleDate(a.date)}`,
        url: prefix + a.link,
        icon: ARTICLE_ICON
      }));

      const notes = sortItemsByDate(bdData.notes || []).map((n) => ({
        type: "note",
        title: n.title,
        meta: `Brain Dump · ${n.tag || ""}`,
        url: null,
        content: (Array.isArray(n.content) ? n.content : [n.content]).join(" "),
        icon: BRAIN_ICON
      }));

      allItems = [...articles, ...notes];
      dataLoaded = true;
    } catch (err) {
      console.error("Command palette data load failed:", err);
    }
  }

  function getResults(query) {
    const q = query.trim().toLowerCase();
    if (!q) return allItems.slice(0, 8);
    return allItems.filter((item) =>
      item.title.toLowerCase().includes(q) ||
      (item.meta || "").toLowerCase().includes(q) ||
      (item.content || "").toLowerCase().includes(q)
    ).slice(0, 10);
  }

  function renderResults(query) {
    if (!resultsEl) return;
    const results = getResults(query);
    focusedIndex = -1;

    if (results.length === 0) {
      resultsEl.innerHTML = `<p class="cmd-empty">No results for "${escapeHtml(query)}"</p>`;
      return;
    }

    const articles = results.filter((r) => r.type === "article");
    const notes = results.filter((r) => r.type === "note");

    let html = "";
    const addGroup = (label, items) => {
      if (!items.length) return;
      html += `<p class="cmd-group-label">${label}</p>`;
      items.forEach((item, localIdx) => {
        const globalIdx = results.indexOf(item);
        html += `
          <button class="cmd-result-item" data-index="${globalIdx}" data-url="${item.url ? escapeHtml(item.url) : ""}" type="button">
            <span class="cmd-result-icon">${item.icon}</span>
            <span class="cmd-result-text">
              <span class="cmd-result-title">${escapeHtml(item.title)}</span>
              <span class="cmd-result-meta">${escapeHtml(item.meta || "")}</span>
            </span>
          </button>`;
      });
    };

    addGroup("Articles", articles);
    addGroup("Brain Dumps", notes);
    resultsEl.innerHTML = html;
  }

  function open() {
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.className = "cmd-overlay";
      overlay.setAttribute("role", "dialog");
      overlay.setAttribute("aria-label", "Search");
      overlay.innerHTML = `
        <div class="cmd-palette">
          <div class="cmd-input-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input type="search" class="cmd-input" placeholder="Search articles and notes…" autocomplete="off" aria-label="Search" />
          </div>
          <div class="cmd-results"></div>
          <div class="cmd-footer">
            <span class="cmd-hint"><kbd>↑↓</kbd> navigate</span>
            <span class="cmd-hint"><kbd>↵</kbd> open</span>
            <span class="cmd-hint"><kbd>Esc</kbd> close</span>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      input = overlay.querySelector(".cmd-input");
      resultsEl = overlay.querySelector(".cmd-results");

      input.addEventListener("input", () => renderResults(input.value));
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) close();
        const btn = e.target.closest(".cmd-result-item");
        if (btn) navigate(btn.dataset.url);
      });

      overlay.addEventListener("keydown", (e) => {
        const items = [...resultsEl.querySelectorAll(".cmd-result-item")];
        if (e.key === "ArrowDown") {
          e.preventDefault();
          focusedIndex = Math.min(focusedIndex + 1, items.length - 1);
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          focusedIndex = Math.max(focusedIndex - 1, -1);
        } else if (e.key === "Enter") {
          e.preventDefault();
          const focused = items[focusedIndex];
          if (focused) navigate(focused.dataset.url);
        } else if (e.key === "Escape") {
          close();
          return;
        }
        items.forEach((item, i) => item.classList.toggle("focused", i === focusedIndex));
        if (focusedIndex >= 0 && items[focusedIndex]) {
          items[focusedIndex].scrollIntoView({ block: "nearest" });
        }
      });
    }

    overlay.classList.add("open");
    input.value = "";
    loadData().then(() => renderResults(""));
    requestAnimationFrame(() => input.focus());
  }

  function close() {
    if (overlay) overlay.classList.remove("open");
  }

  function navigate(url) {
    if (!url) return;
    close();
    location.href = url;
  }

  document.addEventListener("keydown", (e) => {
    const tag = (e.target.tagName || "").toLowerCase();
    const isEditing = tag === "input" || tag === "textarea" || e.target.isContentEditable;
    if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !isEditing && !e.metaKey && !e.ctrlKey)) {
      e.preventDefault();
      open();
    }
  });

  const triggerBtn = document.getElementById("cmdSearchTrigger");
  if (triggerBtn) triggerBtn.addEventListener("click", open);
}

initCommandPalette();

/* ─── Skeleton loading for containers ───────────────────────────── */

function showSkeletons(container, count = 3) {
  if (!container) return;
  container.innerHTML = Array.from({ length: count }, () => `
    <div class="skeleton-card">
      <div class="skeleton-line narrow"></div>
      <div class="skeleton-line title"></div>
      <div class="skeleton-line medium"></div>
      <div class="skeleton-line full"></div>
      <div class="skeleton-line wide"></div>
      <div class="skeleton-line medium"></div>
    </div>
  `).join("");
}

(function initSkeletons() {
  if (thoughtPiecesContainer) showSkeletons(thoughtPiecesContainer, 3);
  if (brainDumpsContainer) showSkeletons(brainDumpsContainer, 3);
})();

/* ─── Reading history panel ─────────────────────────────────────── */

function initReadingHistory() {
  const HISTORY_ARTICLES_KEY = "tnc-read";

  function getHistoryData(thoughtPiecesData) {
    const articles = thoughtPiecesData || [];
    const readSet = getReadArticles();
    const bookmarkSet = getBookmarks();
    const isArticlePage = location.pathname.includes("/articles/");
    const prefix = isArticlePage ? "../" : "";

    const readArticles = articles
      .filter((a) => readSet.has(a.link))
      .sort((a, b) => new Date(b.date) - new Date(a.date));

    const savedArticles = articles
      .filter((a) => bookmarkSet.has(a.link))
      .sort((a, b) => new Date(b.date) - new Date(a.date));

    return { readArticles, savedArticles, prefix };
  }

  function renderTab(listEl, articles, prefix, emptyMsg) {
    if (!articles.length) {
      listEl.innerHTML = `<p class="history-empty">${emptyMsg}</p>`;
      return;
    }
    listEl.innerHTML = articles.map((a) => `
      <a class="history-item" href="${prefix}${a.link}">
        <div class="history-item-title">${escapeHtml(a.title)}</div>
        <div class="history-item-meta">${a.topic || ""} · ${formatArticleDate(a.date)}</div>
      </a>
    `).join("");
  }

  let overlay = null;
  let activeTab = "saved";
  let tpData = null;

  async function ensureData() {
    if (tpData) return;
    const isArticlePage = location.pathname.includes("/articles/");
    const prefix = isArticlePage ? "../" : "";
    try {
      const resp = await fetch(`${prefix}data/thought-pieces.json`);
      const json = await resp.json();
      tpData = json.articles || [];
    } catch { tpData = []; }
  }

  function updatePanel() {
    if (!overlay) return;
    const listEl = overlay.querySelector(".history-list");
    const { readArticles, savedArticles, prefix } = getHistoryData(tpData);

    if (activeTab === "saved") {
      renderTab(listEl, savedArticles, prefix, "No saved articles yet. Click the bookmark icon on any article.");
    } else {
      renderTab(listEl, readArticles, prefix, "No articles read yet. Articles are marked read when you reach the bottom.");
    }
  }

  function open() {
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.className = "history-overlay";
      overlay.setAttribute("role", "dialog");
      overlay.setAttribute("aria-label", "Reading history");
      overlay.innerHTML = `
        <div class="history-panel">
          <div class="history-panel-header">
            <h2 class="history-panel-title">Your Library</h2>
            <button class="history-close-btn" aria-label="Close" type="button">
              <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div class="history-tabs">
            <button class="history-tab active" data-tab="saved" type="button">Saved</button>
            <button class="history-tab" data-tab="read" type="button">Read</button>
          </div>
          <div class="history-list"></div>
          <div class="history-panel-footer">
            <button class="history-clear-btn" type="button">Clear all</button>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      overlay.querySelector(".history-close-btn").addEventListener("click", close);
      overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });

      overlay.querySelectorAll(".history-tab").forEach((tab) => {
        tab.addEventListener("click", () => {
          activeTab = tab.dataset.tab;
          overlay.querySelectorAll(".history-tab").forEach((t) => t.classList.toggle("active", t === tab));
          updatePanel();
        });
      });

      overlay.querySelector(".history-clear-btn").addEventListener("click", () => {
        if (activeTab === "saved") {
          localStorage.removeItem(BOOKMARKS_KEY);
        } else {
          localStorage.removeItem(READ_KEY);
        }
        updatePanel();
      });
    }

    overlay.classList.add("open");
    ensureData().then(updatePanel);
  }

  function close() {
    if (overlay) overlay.classList.remove("open");
  }

  const historyBtn = document.getElementById("historyBtn");
  if (historyBtn) historyBtn.addEventListener("click", open);

  return { open };
}

const readingHistory = initReadingHistory();

/* ─── Mobile hamburger nav ──────────────────────────────────────── */

function initMobileNav() {
  const hamburger = document.getElementById("navHamburger");
  const nav = document.getElementById("siteNav");
  if (!hamburger || !nav) return;

  hamburger.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    hamburger.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", (e) => {
    if (!hamburger.contains(e.target) && !nav.contains(e.target)) {
      nav.classList.remove("is-open");
      hamburger.setAttribute("aria-expanded", "false");
    }
  });

  nav.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("is-open");
      hamburger.setAttribute("aria-expanded", "false");
    });
  });
}

initMobileNav();

/* ─── Mark as read ──────────────────────────────────────────────── */

const READ_KEY = "tnc-read";

function getReadArticles() {
  try { return new Set(JSON.parse(localStorage.getItem(READ_KEY) || "[]")); } catch { return new Set(); }
}

function markCurrentArticleRead() {
  const articleEl = document.querySelector(".article-content");
  if (!articleEl) return;

  const pagePath = location.pathname.replace(/^.*\/articles\//, "articles/");
  let marked = false;

  window.addEventListener("scroll", () => {
    if (marked) return;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight > 0 && (window.scrollY / docHeight) >= 0.85) {
      const readSet = getReadArticles();
      readSet.add(pagePath);
      localStorage.setItem(READ_KEY, JSON.stringify([...readSet]));
      marked = true;
    }
  }, { passive: true });
}

markCurrentArticleRead();
