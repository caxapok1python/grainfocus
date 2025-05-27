// URL API
const API = {
    stats: '/api/session/stats',
    images: '/api/session/images',
    metrics: '/api/metrics'
};

// Обновление панели со статистикой
async function updateStats() {
    const res = await fetch(API.stats);
    const {now, min, max} = await res.json();
    document.getElementById('weed-now').innerText = now.weed;
    document.getElementById('weed-min').innerText = min.weed;
    document.getElementById('weed-max').innerText = max.weed;
    document.getElementById('broken-now').innerText = now.broken;
    document.getElementById('broken-min').innerText = min.broken;
    document.getElementById('broken-max').innerText = max.broken;
}

// Обновление изображений
async function updateImages() {
    const res = await fetch(API.images);
    const {raw, annot} = await res.json();
    const ts = Date.now();
    document.getElementById('img-raw').src = `${raw}?t=${ts}`;
    // Assuming 'img-annot' might still be needed or was for a different view
    // If not, this line can be removed.
    document.getElementById('image-box').src = `${annot}?t=${ts}`;
}

// Инициализация графиков Chart.js
let charts = {
    weed: null,
    broken: null
};

function initSingleChart(canvasId, dataLabel, initialData, borderColor, thresholdValue) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Initial empty labels
            datasets: [
                {
                    label: dataLabel,
                    data: initialData,
                    borderColor: borderColor,
                    backgroundColor: Chart.helpers.color(borderColor).alpha(0.3).rgbString(),
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Threshold', // Second dataset for threshold line
                    data: [], // Initial empty data for threshold
                    borderColor: 'rgb(0, 0, 0)',
                    borderWidth: 2, // As per user's latest change
                    fill: false,
                    pointRadius: 0,
                    tension: 0 // Straight line
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'category',
                    title: { display: false }
                },
                y: {
                    beginAtZero: true,
                    position: 'right',
                    title: { display: false } // yAxisMax removed as per user's change
                }
            },
            plugins: {
                legend: {
                    display: false
                }
                // Annotation and Title plugins removed
            }
        }
    });
    chart.thresholdValue = thresholdValue; // Store threshold for updates
    return chart;
}

// Обновление данных графиков
async function updateCharts() {
    const res = await fetch(API.metrics);
    const {time, weed, broken} = await res.json();

    if (!charts.weed) {
        charts.weed = initSingleChart('weedChart', 'Сорные вкл.', [], 'rgb(222,194,48)', 10.0); // yAxisMax and title removed
    }
    if (!charts.broken) {
        charts.broken = initSingleChart('brokenChart', 'Дроблёное, %', [], 'rgb(214,119,117)', 7.0); // yAxisMax and title removed
    }

    charts.weed.data.labels = time;
    charts.weed.data.datasets[0].data = weed;
    charts.weed.data.datasets[1].data = Array(time.length).fill(charts.weed.thresholdValue); // Update threshold dataset
    charts.weed.update();

    charts.broken.data.labels = time;
    charts.broken.data.datasets[0].data = broken;
    charts.broken.data.datasets[1].data = Array(time.length).fill(charts.broken.thresholdValue); // Update threshold dataset
    charts.broken.update();
}

// Запускаем опросы раз в 3 секунды
async function tick() {
    await Promise.all([
        updateStats(),
        updateImages(),
        updateCharts()
    ]);
}

// старт
window.addEventListener('DOMContentLoaded', () => {
    charts.weed = initSingleChart('weedChart', 'Сорные вкл.', [], 'rgb(222,194,48)', 7.0); // yAxisMax and title removed
    charts.broken = initSingleChart('brokenChart', 'Дроблёное, %', [], 'rgb(214,119,117)', 5); // yAxisMax and title removed
    
    tick();
    setInterval(tick, 3000);
});