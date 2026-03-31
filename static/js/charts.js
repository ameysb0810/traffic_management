function initHourlyChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Traffic Volume',
                data,
                borderColor: '#0dcaf0',
                backgroundColor: 'rgba(13,202,240,0.25)',
                tension: 0.4,
                fill: true,
            }],
        },
        options: {
            responsive: true,
            scales: {
                x: { ticks: { color: '#f8f9fa' } },
                y: { ticks: { color: '#f8f9fa' } },
            },
            plugins: {
                legend: { labels: { color: '#f8f9fa' } }
            }
        }
    });
}

function initDoughnutChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545'],
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#f8f9fa' } }
            }
        }
    });
}

function initCongestionChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Congestion Score',
                data,
                backgroundColor: '#fd7e14',
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: {
                x: { ticks: { color: '#f8f9fa' } },
                y: { ticks: { color: '#f8f9fa' } },
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}
