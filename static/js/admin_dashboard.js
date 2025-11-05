document.addEventListener('DOMContentLoaded', function () {
    try {
        const complaintsScript = document.getElementById('complaints-data');
        const complaintsData = complaintsScript ? JSON.parse(complaintsScript.textContent || '[]') : [];

        const mapEl = document.getElementById('india-map');
        if (!mapEl) return;

        // Initialize map centered on India
        const indiaCenter = [22.5937, 78.9629];
        const map = L.map('india-map', { preferCanvas: true }).setView(indiaCenter, 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        const markers = L.markerClusterGroup();
        const markerIndex = {};

        // Populate markers and the problem list
        const listEl = document.getElementById('problem-list');
        if (listEl) listEl.innerHTML = '';

        complaintsData.forEach(c => {
            if (c.latitude && c.longitude) {
                const lat = parseFloat(c.latitude);
                const lng = parseFloat(c.longitude);
                if (!isNaN(lat) && !isNaN(lng)) {
                    const popupHtml = `<strong>${escapeHtml(c.title || '')}</strong><br>${escapeHtml(c.location || '')}<br><em>${escapeHtml(c.category || '')}</em>`;
                    const m = L.marker([lat, lng]);
                    m.bindPopup(popupHtml);
                    markers.addLayer(m);
                    markerIndex[c.id] = m;

                    // Add to problem list
                    if (listEl) {
                        const item = document.createElement('div');
                        item.className = 'problem-item';
                        item.dataset.id = c.id;
                        item.style.cssText = 'padding:0.6rem; border-radius:8px; margin-bottom:0.4rem; cursor:pointer; background: rgba(255,255,255,0.03); color: white;';
                        item.innerHTML = `<div style="font-weight:700;">${escapeHtml(c.title || '')}</div><div style="font-size:0.85rem; color:rgba(255,255,255,0.7);">${escapeHtml(c.location || '')} • ${escapeHtml(c.category || '')}</div>`;
                        item.addEventListener('click', () => {
                            map.setView([lat, lng], 13, { animate: true });
                            m.openPopup();
                            highlightRow(c.id);
                        });
                        listEl.appendChild(item);
                    }
                }
            }
        });

        map.addLayer(markers);

        // Clicking table rows also zooms to marker when available
        function highlightRow(complaintId) {
            document.querySelectorAll('tr[data-complaint-id]').forEach(r => r.style.background = '');
            const row = document.querySelector(`tr[data-complaint-id="${complaintId}"]`);
            if (row) {
                row.style.background = 'rgba(255,255,255,0.06)';
                row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        document.querySelectorAll('tr[data-complaint-id]').forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                const lat = row.getAttribute('data-lat');
                const lng = row.getAttribute('data-lng');
                const id = row.getAttribute('data-complaint-id');
                if (lat && lng) {
                    const la = parseFloat(lat), lo = parseFloat(lng);
                    map.setView([la, lo], 13, { animate: true });
                    const mk = markerIndex[id];
                    if (mk) mk.openPopup();
                    // highlight corresponding list item
                    const listItem = document.querySelector(`#problem-list .problem-item[data-id='${id}']`);
                    if (listItem) {
                        listItem.style.background = 'rgba(255,255,255,0.06)';
                        setTimeout(() => listItem.style.background = '', 2000);
                    }
                }
            });
        });

        // Resize map when pane sizes change
        setTimeout(() => map.invalidateSize(), 500);

        // Utility: escape HTML to avoid injection
        function escapeHtml(str) {
            return str.replace(/[&<>"']/g, function (c) {
                return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c];
            });
        }

    } catch (err) {
        console.error('admin_dashboard.js error', err);
    }
});
