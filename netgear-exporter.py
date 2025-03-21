
import time
import re
import requests
from prometheus_client import start_http_server, Gauge
from http import HTTPStatus

# Config
USERNAME = "admin"
PASSWORD = "password"
MODEM_IP = "192.168.100.1"
EXPORTER_PORT = 8000

# Prometheus Gauges
gauges = {
    "downstream_power": Gauge("modem_downstream_power", "Downstream Power Level (dBmV)", ["channel"]),
    "downstream_snr": Gauge("modem_downstream_snr", "Downstream SNR (dB)", ["channel"]),
    "upstream_power": Gauge("modem_upstream_power", "Upstream Power Level (dBmV)", ["channel"]),
    "ofdm_power": Gauge("modem_ofdm_power", "OFDM Downstream Power Level (dBmV)", ["channel"]),
    "ofdm_snr": Gauge("modem_ofdm_snr", "OFDM Downstream SNR (dB)", ["channel"]),
    "ofdma_power": Gauge("modem_ofdma_power", "OFDMA Upstream Power Level (dBmV)", ["channel"]),
}

# Extract value list from JavaScript function
def extract_tag_value(func_name, text):
    pattern = rf"function {func_name}\(\).*?var tagValueList = '([^']+)';"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).split("|") if match else []

# Parse channel values
def parse_downstream(values):
    count = int(values[0])
    metrics = []
    for i in range(count):
        idx = 1 + i * 9
        try:
            metrics.append({
                "channel": values[idx],
                "power": float(values[idx + 5]),
                "snr": float(values[idx + 6]),
            })
        except:
            continue
    return metrics

def parse_upstream(values):
    count = int(values[0])
    metrics = []
    for i in range(count):
        idx = 1 + i * 7
        try:
            metrics.append({
                "channel": values[idx],
                "power": float(values[idx + 6].split()[0]),
            })
        except:
            continue
    return metrics

def parse_ofdm(values):
    count = int(values[0])
    metrics = []
    for i in range(count):
        idx = 1 + i * 11
        try:
            power = float(values[idx + 6].split()[0])
            snr_field = values[idx + 7]
            snr = float(snr_field.split()[0]) if "dB" in snr_field else 0.0
            metrics.append({
                "channel": values[idx],
                "power": power,
                "snr": snr,
            })
        except:
            continue
    return metrics

def parse_ofdma(values):
    count = int(values[0])
    metrics = []
    for i in range(count):
        idx = 1 + i * 6
        try:
            metrics.append({
                "channel": values[idx],
                "power": float(values[idx + 5].split()[0]),
            })
        except:
            continue
    return metrics

# Authenticate and fetch modem page
def fetch_modem_data():
    session = requests.Session()
    login_page = session.get(f"http://{MODEM_IP}/Login.htm")
    login_id_match = re.search(r'/goform/Login\?id=(\d+)', login_page.text)
    if not login_id_match:
        print("Login ID not found")
        return None
    login_id = login_id_match.group(1)

    login_payload = {"loginName": USERNAME, "loginPassword": PASSWORD}
    headers = {
        "Referer": f"http://{MODEM_IP}/Login.htm",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    login = session.post(f"http://{MODEM_IP}/goform/Login?id={login_id}", data=login_payload, headers=headers)
    if "ErrorMsg.htm" in login.text:
        print("Login failed")
        return None

    page = session.get(f"http://{MODEM_IP}/DocsisStatus.htm")
    if "Login.htm" in page.text:
        print("Redirected — session failed")
        return None

    return page.text

# Scrape and update Prometheus metrics
def scrape():
    html = fetch_modem_data()
    if not html:
        return

    ds_values = extract_tag_value("InitDsTableTagValue", html)
    us_values = extract_tag_value("InitUsTableTagValue", html)
    ofdm_values = extract_tag_value("InitDsOfdmTableTagValue", html)
    ofdma_values = extract_tag_value("InitUsOfdmaTableTagValue", html)

    for metric in parse_downstream(ds_values):
        gauges["downstream_power"].labels(channel=metric["channel"]).set(metric["power"])
        gauges["downstream_snr"].labels(channel=metric["channel"]).set(metric["snr"])

    for metric in parse_upstream(us_values):
        gauges["upstream_power"].labels(channel=metric["channel"]).set(metric["power"])

    for metric in parse_ofdm(ofdm_values):
        gauges["ofdm_power"].labels(channel=metric["channel"]).set(metric["power"])
        gauges["ofdm_snr"].labels(channel=metric["channel"]).set(metric["snr"])

    for metric in parse_ofdma(ofdma_values):
        gauges["ofdma_power"].labels(channel=metric["channel"]).set(metric["power"])

# Main
if __name__ == "__main__":
    print(f"Starting Prometheus metrics server on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)
    while True:
        scrape()
        time.sleep(30)
