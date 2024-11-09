class ClimateWidget {
    constructor() {
        this.tempElement = document.getElementById('temperature');
        this.humidityElement = document.getElementById('humidity');
        this.lastUpdateElement = document.getElementById('last-update');
        this.apiUrl = '/v1/climate/latest';  // Updated to use local endpoint
        this.updateInterval = 60000; // 60 seconds
    }

    async fetchClimateData() {
        try {
            const response = await fetch(this.apiUrl);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            this.updateUI(data);
        } catch (error) {
            console.error('Error fetching climate data:', error);
            this.showError();
        }
    }

    updateUI(data) {
        this.tempElement.textContent = data.temperature;
        this.humidityElement.textContent = data.humidity;
        this.lastUpdateElement.textContent = data.last_datetime;
    }

    showError() {
        this.tempElement.textContent = 'Error';
        this.humidityElement.textContent = 'Error';
        this.lastUpdateElement.textContent = 'Connection failed';
    }

    start() {
        // Initial fetch
        this.fetchClimateData();
        
        // Set up periodic updates
        setInterval(() => {
            this.fetchClimateData();
        }, this.updateInterval);
    }
}

// Initialize and start the widget when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const climateWidget = new ClimateWidget();
    climateWidget.start();
});
