// CommunityHub Pro - FIXED JavaScript

class CommunityHub {
    constructor() {
        this.init();
    }

    init() {
        console.log('CommunityHub Pro initialized');
        this.setupEventListeners();
        this.initAnimations();
        this.initMaps();
        this.initCharts();
    }

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }

        // Signup form
        const signupForm = document.getElementById('signupForm');
        if (signupForm) {
            signupForm.addEventListener('submit', this.handleSignup.bind(this));
        }

        // Complaint form
        const complaintForm = document.getElementById('complaintForm');
        if (complaintForm) {
            complaintForm.addEventListener('submit', this.handleComplaintSubmit.bind(this));
        }

        // File upload preview
        const fileInput = document.getElementById('complaintImage');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleImagePreview.bind(this));
        }

        // Location detection
        const detectLocationBtn = document.getElementById('detectLocation');
        if (detectLocationBtn) {
            detectLocationBtn.addEventListener('click', this.detectLocation.bind(this));
        }

        // Admin actions
        this.setupAdminEventListeners();
    }

    setupAdminEventListeners() {
        // Status update buttons
        document.querySelectorAll('.status-update-btn').forEach(btn => {
            btn.addEventListener('click', this.handleStatusUpdate.bind(this));
        });

        // Delete complaint buttons
        document.querySelectorAll('.delete-complaint-btn').forEach(btn => {
            btn.addEventListener('click', this.handleDeleteComplaint.bind(this));
        });
    }

    initAnimations() {
        // Add fade-in animations to cards
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all cards and stats
        document.querySelectorAll('.card, .complaint-card, .stat-card').forEach(el => {
            el.style.opacity = '0';
            observer.observe(el);
        });

        // Add floating animation to hero elements
        document.querySelectorAll('.hero h1, .hero p').forEach((el, index) => {
            el.style.animationDelay = `${index * 0.2}s`;
        });
    }

    initMaps() {
        const mapElement = document.getElementById('map');
        if (mapElement) {
            this.initializeComplaintMap();
        }
    }

    initializeComplaintMap() {
        // Default coordinates
        const defaultCoords = [20.5937, 78.9629]; // India coordinates
        
        const map = L.map('map').setView(defaultCoords, 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add complaint markers
        this.addComplaintMarkers(map);
    }

    async addComplaintMarkers(map) {
        try {
            const response = await fetch('/api/complaints/map');
            const data = await response.json();

            if (data.success && data.complaints) {
                data.complaints.forEach(complaint => {
                    if (complaint.latitude && complaint.longitude) {
                        const marker = L.marker([complaint.latitude, complaint.longitude]).addTo(map);
                        
                        const popupContent = `
                            <div class="map-popup">
                                <h4>${complaint.title || 'No Title'}</h4>
                                <p><strong>Category:</strong> ${complaint.category || 'Unknown'}</p>
                                <p><strong>Status:</strong> ${complaint.status || 'Unknown'}</p>
                                <p><strong>Severity:</strong> ${complaint.severity || 'Unknown'}</p>
                                <p><strong>Location:</strong> ${complaint.location || 'Unknown'}</p>
                            </div>
                        `;
                        
                        marker.bindPopup(popupContent);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading complaint markers:', error);
        }
    }

    initCharts() {
        const statsChart = document.getElementById('statsChart');
        if (statsChart) {
            this.initializeStatsChart();
        }
    }

    async initializeStatsChart() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            if (data) {
                const ctx = document.getElementById('statsChart').getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Resolved', 'Pending', 'In Progress', 'Other'],
                        datasets: [{
                            data: [
                                data.resolved_complaints || 0,
                                data.pending_complaints || 0,
                                data.total_complaints - (data.resolved_complaints || 0) - (data.pending_complaints || 0),
                                0
                            ],
                            backgroundColor: [
                                '#10b981',
                                '#f59e0b',
                                '#6366f1',
                                '#6b7280'
                            ],
                            borderWidth: 2,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `${context.label}: ${context.raw}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Error loading stats chart:', error);
        }
    }

    async handleLogin(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Login successful!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                throw new Error(data.message || 'Login failed');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleSignup(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Account created successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                throw new Error(data.message || 'Signup failed');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    handleImagePreview(event) {
        const file = event.target.files[0];
        const preview = document.getElementById('imagePreview');
        
        if (file && preview) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `
                    <div class="image-preview-container">
                        <img src="${e.target.result}" alt="Preview" class="image-preview">
                        <button type="button" class="remove-image" onclick="removeImagePreview()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        }
    }

    async detectLocation() {
        const locationInput = document.getElementById('location');
        const latitudeInput = document.getElementById('latitude');
        const longitudeInput = document.getElementById('longitude');

        if (!navigator.geolocation) {
            this.showNotification('Geolocation is not supported by your browser', 'error');
            return;
        }

        this.showNotification('Detecting your location...', 'info');

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                if (latitudeInput) latitudeInput.value = lat;
                if (longitudeInput) longitudeInput.value = lng;

                // Try to get address from coordinates
                try {
                    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
                    const data = await response.json();
                    
                    if (data.display_name && locationInput) {
                        locationInput.value = data.display_name;
                        this.showNotification('Location detected successfully!', 'success');
                    } else {
                        throw new Error('Could not get address');
                    }
                } catch (error) {
                    if (locationInput) {
                        locationInput.value = `Lat: ${lat}, Lng: ${lng}`;
                    }
                    this.showNotification('Location detected (address lookup failed)', 'warning');
                }
            },
            (error) => {
                let message = 'Unable to detect your location';
                if (error.code === error.PERMISSION_DENIED) {
                    message = 'Location access denied. Please enable location permissions.';
                } else if (error.code === error.TIMEOUT) {
                    message = 'Location detection timed out.';
                }
                this.showNotification(message, 'error');
                console.error('Geolocation error:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }

    async handleComplaintSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Raising Complaint...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/raise-complaint', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Complaint raised successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } else {
                throw new Error(data.message || 'Failed to raise complaint');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleStatusUpdate(event) {
        const button = event.currentTarget;
        const complaintId = button.dataset.complaintId;
        const status = button.dataset.status;
        
        const formData = new FormData();
        formData.append('status', status);
        formData.append('admin_notes', `Status changed to ${status} by admin`);

        try {
            const response = await fetch(`/admin/complaints/${complaintId}/update`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(`Complaint status updated to ${status}`, 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.message || 'Failed to update status');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async handleDeleteComplaint(event) {
        const button = event.currentTarget;
        const complaintId = button.dataset.complaintId;
        
        if (!confirm('Are you sure you want to delete this complaint? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/admin/complaints/${complaintId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Complaint deleted successfully', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.message || 'Failed to delete complaint');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Global function to remove image preview
function removeImagePreview() {
    const preview = document.getElementById('imagePreview');
    const fileInput = document.getElementById('complaintImage');
    
    if (preview) preview.innerHTML = '';
    if (fileInput) fileInput.value = '';
}

// Utility function for API calls
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CommunityHub();
});

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card, .complaint-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
            `;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add CSS for ripple effect
    if (!document.querySelector('#ripple-styles')) {
        const styles = document.createElement('style');
        styles.id = 'ripple-styles';
        styles.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            .btn {
                position: relative;
                overflow: hidden;
            }
        `;
        document.head.appendChild(styles);
    }
});