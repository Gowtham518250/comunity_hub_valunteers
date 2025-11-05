// Advanced Analytics Module
class CommunityAnalytics {
    constructor() {
        this.map = null;
        this.heatmap = null;
        this.markers = L.markerClusterGroup();
        this.socket = null;
        this.charts = {};
        this.setupWebSocket();
    }

    setupWebSocket() {
        this.socket = new WebSocket(`ws://${window.location.host}/ws/analytics`);
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateAnalytics(data);
        };
    }

    initializeMap(containerId, center = [20.5937, 78.9629], zoom = 5) {
        this.map = L.map(containerId).setView(center, zoom);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);
        this.map.addLayer(this.markers);

        // Add heatmap layer
        const cfg = {
            "radius": 40,
            "maxOpacity": .8,
            "scaleRadius": false,
            "useLocalExtrema": true,
            latField: 'lat',
            lngField: 'lng',
            valueField: 'count'
        };
        const heatmapLayer = new HeatmapOverlay(cfg);
        this.map.addLayer(heatmapLayer);
        this.heatmap = heatmapLayer;
    }

    zoomToLocation(lat, lng, zoom = 15) {
        if (this.map) {
            this.map.flyTo([lat, lng], zoom, {
                duration: 1.5,
                easeLinearity: 0.25
            });
        }
    }

    updateHeatmap(data) {
        if (this.heatmap) {
            this.heatmap.setData({
                max: 10,
                data: data
            });
        }
    }

    createCategoryChart(containerId, data) {
        const ctx = document.getElementById(containerId).getContext('2d');
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: [
                        '#FF6B6B', '#4ECDC4', '#FFD93D', '#6BCF7F',
                        '#4D96FF', '#9D4EDD', '#F39C12', '#95A5A6'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: 'white' }
                    },
                    datalabels: {
                        color: 'white',
                        formatter: (value, ctx) => {
                            const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = (value * 100 / sum).toFixed(1) + '%';
                            return percentage;
                        }
                    }
                }
            }
        });
    }

    createTrendChart(containerId, data) {
        const ctx = document.getElementById(containerId).getContext('2d');
        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Complaints',
                    data: data.values,
                    borderColor: '#4ECDC4',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(78, 205, 196, 0.1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: { color: 'white' }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: { color: 'white' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: 'white' }
                    }
                }
            }
        });
    }

    updateAnalytics(data) {
        // Update heatmap
        if (data.heatmap) {
            this.updateHeatmap(data.heatmap);
        }

        // Update charts
        if (data.categories && this.charts.category) {
            this.charts.category.data.datasets[0].data = Object.values(data.categories);
            this.charts.category.update();
        }

        if (data.trend && this.charts.trend) {
            this.charts.trend.data.labels = data.trend.labels;
            this.charts.trend.data.datasets[0].data = data.trend.values;
            this.charts.trend.update();
        }

        // Update markers
        if (data.markers) {
            this.markers.clearLayers();
            data.markers.forEach(marker => {
                const m = L.marker([marker.lat, marker.lng])
                    .bindPopup(`
                        <div class="marker-popup">
                            <h3>${marker.title}</h3>
                            <p>${marker.description}</p>
                            <span class="badge" style="background-color: ${marker.categoryColor}">
                                ${marker.category}
                            </span>
                            <button onclick="analytics.zoomToLocation(${marker.lat}, ${marker.lng})" class="zoom-btn">
                                🔍 Zoom Here
                            </button>
                        </div>
                    `);
                this.markers.addLayer(m);
            });
        }

        // Update basic stats in the DOM if present
        try {
            if (typeof data.total_complaints !== 'undefined') {
                const el = document.getElementById('mapTotalComplaints');
                if (el) el.textContent = data.total_complaints;
                // Update main stat cards if they have IDs
                const totalCard = document.getElementById('statTotalComplaints'); if (totalCard) totalCard.textContent = data.total_complaints;
            }
            if (typeof data.resolved_complaints !== 'undefined') {
                const el = document.getElementById('statResolved'); if (el) el.textContent = data.resolved_complaints;
            }
            if (typeof data.pending_complaints !== 'undefined') {
                const el = document.getElementById('statPending'); if (el) el.textContent = data.pending_complaints;
            }
            if (typeof data.urgent_complaints !== 'undefined') {
                const el = document.getElementById('statUrgent'); if (el) el.textContent = data.urgent_complaints;
            }
            if (typeof data.resolution_rate !== 'undefined') {
                const el = document.getElementById('statResolutionRate'); if (el) el.textContent = data.resolution_rate + '%';
            }
            if (typeof data.total_users !== 'undefined') {
                const el = document.getElementById('statTotalUsers'); if (el) el.textContent = data.total_users;
            }
            if (typeof data.performance_score !== 'undefined') {
                const el = document.querySelector('.performance-score'); if (el) el.textContent = data.performance_score + '/100';
                const circleInner = document.querySelector('.chart-container div > div');
                if (circleInner) circleInner.textContent = data.performance_score;
                // update conic gradient if present
                const conic = document.querySelector('.chart-container div');
                if (conic) {
                    conic.style.background = `conic-gradient(#6BCF7F 0% ${data.performance_score * 3.6}deg, rgba(255,255,255,0.2) ${data.performance_score * 3.6}deg 360deg)`;
                }
            }
            // Update map overlay counters
            if (typeof data.heatmap !== 'undefined') {
                const hotspotsEl = document.getElementById('mapHotspots'); if (hotspotsEl) hotspotsEl.textContent = data.heatmap.length || 0;
            }
            // Update clusters count from marker group
            const clustersEl = document.getElementById('mapClusters'); if (clustersEl) clustersEl.textContent = this.markers.getLayers().length || 0;
        } catch (e) {
            console.warn('Error updating DOM stats from analytics payload', e);
        }
    }
}

// Initialize analytics when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.analytics = new CommunityAnalytics();
});