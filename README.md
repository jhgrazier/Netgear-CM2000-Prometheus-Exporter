# Netgear-CM2000-Prometheus-Exporter
A Python-based Prometheus exporter for monitoring Netgear modem metrics. This exporter scrapes data from the modem's web interface and exposes it as Prometheus metrics. Includes a premade Grafana dashboard

This project was inspired by @tylxr59's netgear_cm_exporter ([https://github.com/ickymettle/netgear_cm_exporter](https://github.com/tylxr59/Netgear-Modem-Prometheus-Exporter))

# Officially Supported Modems
 • Netgear CM2000

# Features
 • Scrapes modem information such as vendor, model, hardware version, serial number, MAC address, firmware version, and IPv4 address.
 
 • Monitors downstream and upstream channel statistics including frequency, power, SNR, and symbol rate.
 
 • Periodically updates metrics and exposes them to Prometheus.

# Requirements
 • Python 3.x
 
 • requests
 
 • prometheus_client
 
 • time
 
 • re

# Installation
1. Clone the repository:
   ```
   git clone https://github.com/jhgrazier/Netgear-CM2000-Prometheus-Exporter.git
   ```

2. Change into the cloned directory

   ```
   cd Netgear-CM2000-Prometheus-Exporter
   ```

3. Install required Python requirements

   ```
   pip install prometheus_client requests time re
   ```

4. Copy the netgear-exporter.py into /usr/bin
   
  ```
  cp netgear-exporter.py /usr/bin
  ```

5. Install the service files into /etc/systemd/system
   
   ```   
   cp netgear-exporter.service /etc/systemd/system
   ```

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
   ```
   [root@grafana system]# systemctl enable netgear-exporter.service
   Created symlink /etc/systemd/system/multi-user.target.wants/netgear-exporter.service → /etc/systemd/system/netgear-exporter.service.
   [root@grafana system]# systemctl start netgear-exporter.service
   ```

2. Validate the service started
   ```
   [root@grafana system]# systemctl status netgear-exporter.service
   ● netgear-exporter.service - "Start netgear exporter after network is loaded"
     Loaded: loaded (/etc/systemd/system/netgear-exporter.service; enabled; preset: disabled)
     Active: active (running) since Fri 2025-03-21 09:24:19 MDT; 5s ago
   Main PID: 580599 (python)
      Tasks: 2 (limit: 23111)
     Memory: 18.0M
        CPU: 193ms
     CGroup: /system.slice/netgear-exporter.service
             └─580599 python /usr/bin/netgear-exporter.py

   Mar 21 09:24:19 grafana systemd[1]: Started "Start netgear exporter after network is loaded".
   ```
