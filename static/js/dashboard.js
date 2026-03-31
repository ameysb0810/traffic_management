function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function createToast(message, type='info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'toast align-items-center text-bg-' + type + ' border-0 show';
    wrapper.role = 'alert';
    wrapper.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    toastContainer.appendChild(wrapper);
    setTimeout(() => wrapper.remove(), 5000);
}

async function refreshStatistics() {
    try {
        const response = await fetch('/api/stats/');
        if (!response.ok) return;
        const data = await response.json();
        document.querySelectorAll('[data-stat]').forEach(el => {
            const key = el.dataset.stat;
            if (data[key] !== undefined) {
                el.textContent = data[key];
            }
        });
    } catch (error) {
        console.error(error);
    }
}

async function refreshSimulation() {
    const csrftoken = getCookie('csrftoken');
    try {
        const response = await fetch('/simulate/run/', {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
        });
        const data = await response.json();
        createToast(`Simulation completed, ${data.records_created} records created.`, 'success');
        refreshStatistics();
    } catch (error) {
        createToast('Simulation failed.', 'danger');
    }
}

function updateCongestionBadges() {
    document.querySelectorAll('.congestion-badge').forEach(el => {
        const level = el.textContent.trim();
        el.classList.remove('bg-success','bg-warning','bg-danger','bg-secondary');
        if (level === 'LOW') el.classList.add('bg-success');
        if (level === 'MODERATE') el.classList.add('bg-warning', 'text-dark');
        if (level === 'HIGH') el.classList.add('bg-danger');
        if (level === 'CRITICAL') el.classList.add('bg-dark');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    refreshStatistics();
    updateCongestionBadges();
    setInterval(refreshStatistics, 30000);
    document.querySelectorAll('form[action="/simulate/run/"]').forEach(form => {
        form.addEventListener('submit', event => {
            event.preventDefault();
            refreshSimulation();
        });
    });
});
