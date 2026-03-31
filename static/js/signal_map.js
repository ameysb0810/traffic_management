document.addEventListener('DOMContentLoaded', () => {
    const detailPanel = document.getElementById('intersection-detail');
    if (!detailPanel) return;
    const intersectionId = detailPanel.dataset.intersectionId;
    if (!intersectionId) return;
    setInterval(() => {
        fetch(`/api/signals/?intersection_id=${intersectionId}`)
            .then(response => response.json())
            .then(signals => {
                signals.forEach(signal => {
                    const card = document.querySelector(`[data-signal-id='${signal.id}']`);
                    if (!card) return;
                    const indicator = card.querySelector('.signal-indicator');
                    if (indicator) {
                        indicator.className = `signal-indicator ${signal.current_phase.toLowerCase()}`;
                    }
                });
            });
    }, 10000);
});
