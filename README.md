# Netgear-CM2000-Prometheus-Exporter
A Python-based Prometheus exporter for monitoring Netgear modem metrics. This exporter scrapes data from the modem's web interface and exposes it as Prometheus metrics. Includes a premade Grafana dashboard

This project was inspired by @tylxr59's netgear_cm_exporter ([https://github.com/ickymettle/netgear_cm_exporter](https://github.com/tylxr59/Netgear-Modem-Prometheus-Exporter))

# Officially Supported Modems
    * Netgear CM2000

# Features
    * Scrapes modem information such as vendor, model, hardware version, serial number, MAC address, firmware version, and IPv4 address.
    * Monitors downstream and upstream channel statistics including frequency, power, SNR, and symbol rate.
    * Periodically updates metrics and exposes them to Prometheus.

# Requirements
    * Python 3.x
    * requests
    * prometheus_client
    * time
    * re

# Installation
1. Clone the repository: 
   git clone https://github.com/jhgrazier/Netgear-CM2000-Prometheus-Exporter.git

2. cd Netgear-CM2000-Prometheus-Exporter

3. Install required Python requirements
   pip install prometheus_client requests

4. Install the service files
   copy the service files into /etc/systemd/system
   final location will be /etc/systemd/system/startnetgear-exporter.service

# Configuration
Edit the netgear-exporter.py to adjust the password.

# Prometheus Configuration
Add the following job to your Prometheus configuration (adjust localhost to the correct IP if they are not running on the same machine):

```
scrape_configs:
  - job_name: 'netgear_modem'
    static_configs:
      - targets: ['localhost:8000']
```

# Final Configuration

1. Enable and Start the service
   systemctl enable startnetgear-exporter.service
   systemctl start startnetgear-exporter.service

2. Validate the service started
   systemctl status startnetgear-exporter.service
