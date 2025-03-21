# Netgear-CM2000-Prometheus-Exporter
A Python-based Prometheus exporter for monitoring Netgear modem metrics. This exporter scrapes data from the modem's web interface and exposes it as Prometheus metrics. Includes a premade Grafana dashboard

This project was inspired by @tylxr59's netgear_cm_exporter ([https://github.com/tylerx59/Netgear-Modem-Prometheus-Exporter](https://github.com/tylxr59/Netgear-Modem-Prometheus-Exporter))

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

1. Edit the netgear-exporter.py to adjust the password.

# Prometheus Configuration

1. Add the following job to your Prometheus configuration (adjust localhost to the correct IP if they are not running on the same machine):

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

# Verify Metrics 

1. Run this curl command from command line on your host where prometheus is installed.
   ```
   curl http://localhost:8000/metrics | grep modem_
   ```

2. You should see something like the following:
   ```
   modem_downstream_power{channel="2"} 2.9
   modem_downstream_power{channel="3"} 2.9
   modem_downstream_power{channel="4"} 2.8
   modem_downstream_power{channel="5"} 2.9
   modem_downstream_power{channel="6"} 2.6
   modem_downstream_power{channel="7"} 2.8
   modem_downstream_power{channel="8"} 3.0
   modem_downstream_power{channel="9"} 2.8
   modem_downstream_power{channel="10"} 2.8
   ```

# Dashboard

<img width="1507" alt="dashboard_1" src="https://github.com/user-attachments/assets/627b885f-79e1-4726-a487-a7ce5a3c4bda" />

<img width="1511" alt="dashboard_2" src="https://github.com/user-attachments/assets/8b3cbcf7-3b40-4a94-8323-9a7f33e17c63" />

<img width="1510" alt="dashboard_3" src="https://github.com/user-attachments/assets/b7f356fc-c1ed-445e-b1b0-b127850f5c43" />
