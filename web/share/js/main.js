// URL API
const API = {
  stats:   '/api/session/stats',
  images:  '/api/session/images',
  metrics: '/api/metrics'
};

// Обновление панели со статистикой
async function updateStats() {
  const res = await fetch(API.stats);
  const { now, min, max } = await res.json();
  document.getElementById('weed-now').innerText   = now.weed;
  document.getElementById('weed-min').innerText   = min.weed;
  document.getElementById('weed-max').innerText   = max.weed;
  document.getElementById('broken-now').innerText = now.broken;
  document.getElementById('broken-min').innerText = min.broken;
  document.getElementById('broken-max').innerText = max.broken;
}

// Обновление изображений
async function updateImages() {
  const res = await fetch(API.images);
  const { raw, annot } = await res.json();
  // добавляем query-параметр, чтобы обойти кеш браузера
  const ts = Date.now();
  document.getElementById('img-raw').src   = `${raw}?t=${ts}`;
  document.getElementById('img-annot').src = `${annot}?t=${ts}`;
}

// Инициализация графика Chart.js
let chart = null;
function initChart(time, weed, broken) {
  const ctx = document.getElementById('combinedChart').getContext('2d');
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: time,
      datasets: [
        {
          label: 'Сорные включения, %',
          data: weed,
          borderColor: 'rgb(222,194,48)',
          fill: false
        },
        {
          label: 'Дроблёное зерно, %',
          data: broken,
          borderColor: 'rgb(214,119,117)',
          fill: false
        }
      ]
    },
    options: {
      scales: {
        x: { type: 'category', title: { display: true, text: 'Время' } },
        y: { beginAtZero: true, title: { display: true, text: 'Процент, %' } }
      }
    }
  });
}

// Обновление данных графика
async function updateChart() {
  const res = await fetch(API.metrics);
  const { time, weed, broken } = await res.json();
  if (!chart) {
    initChart(time, weed, broken);
  } else {
    chart.data.labels    = time;
    chart.data.datasets[0].data = weed;
    chart.data.datasets[1].data = broken;
    chart.update();
  }
}

// Запускаем опросы раз в 3 секунды
async function tick() {
  await Promise.all([
    updateStats(),
    updateImages(),
    updateChart()
  ]);
}

// старт
window.addEventListener('DOMContentLoaded', () => {
  // если нужно сразу показать пустой график:
  initChart([], [], []);
  tick();
  setInterval(tick, 3000);
});