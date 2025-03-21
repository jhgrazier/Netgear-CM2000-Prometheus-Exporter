import time
import re
import requests
from prometheus_client import start_http_server, Gauge

# Config
USERNAME = "admin"
PASSWORD = "password"
MODEM_IP = "192.168.100.1"
EXPORTER_PORT = 8000

# Prometheus Gauges
gauges = {
    "downstream_power": Gauge("modem_downstream_power", "Downstream Power Level (dBmV)", ["channel"]),
    "downstream_snr": Gauge("modem_downstream_snr", "Downstream SNR (dB)", ["channel"]),
    "downstream_correctables": Gauge("modem_downstream_correctables", "Downstream Correctables", ["channel"]),
    "downstream_uncorrectables": Gauge("modem_downstream_uncorrectables", "Downstream Uncorrectables", ["channel"]),

    "upstream_power": Gauge("modem_upstream_power", "Upstream Power Level (dBmV)", ["channel"]),

    "ofdm_power": Gauge("modem_ofdm_power", "OFDM Downstream Power Level (dBmV)", ["channel"]),
    "ofdm_snr": Gauge("modem_ofdm_snr", "OFDM Downstream SNR/MER (dB)", ["channel"]),
    "ofdm_unerrored": Gauge("modem_ofdm_unerrored", "OFDM Unerrored Codewords", ["channel"]),
    "ofdm_correctable": Gauge("modem_ofdm_correctable", "OFDM Correctable Codewords", ["channel"]),
    "ofdm_uncorrectable": Gauge("modem_ofdm_uncorrectable", "OFDM Uncorrectable Codewords", ["channel"]),

    "ofdma_power": Gauge("modem_ofdma_power", "OFDMA Upstream Power Level (dBmV)", ["channel"]),

    "uptime": Gauge("modem_uptime", "Modem uptime in seconds"),
    "system_time": Gauge("modem_system_time", "Current system time (unix timestamp)"),
}

def extract_tag_value(func_name, text):
    pattern = rf"function {func_name}\(\).*?var tagValueList = '([^']+)';"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).split("|") if match else []

def parse_time_values(values):
    # System time (index 10), Uptime (index 14)
    try:
        system_time_str = values[10].strip()
        uptime_str = values[14].strip()

        # Convert system time string to timestamp
        system_time = time.mktime(time.strptime(system_time_str, "%a %b %d %H:%M:%S %Y"))
        uptime_parts = uptime_str.replace("day", "").replace("days", "").strip().split()
        uptime_seconds = 0
        if len(uptime_parts) == 2:
            days = int(uptime_parts[0])
            h, m, s = map(int, uptime_parts[1].split(":"))
            uptime_seconds = days * 86400 + h * 3600 + m * 60 + s
        return system_time, uptime_seconds
    except:
        return None, None

def parse_downstream(values):
    count = int(values[0])
    for i in range(count):
        idx = 1 + i * 9
        try:
            channel = values[idx]
            power = float(values[idx + 5])
            snr = float(values[idx + 6])
            correctables = int(values[idx + 7])
            uncorrectables = int(values[idx + 8])
            gauges["downstream_power"].labels(channel=channel).set(power)
            gauges["downstream_snr"].labels(channel=channel).set(snr)
            gauges["downstream_correctables"].labels(channel=channel).set(correctables)
            gauges["downstream_uncorrectables"].labels(channel=channel).set(uncorrectables)
        except:
            continue

def parse_upstream(values):
    count = int(values[0])
    for i in range(count):
        idx = 1 + i * 7
        try:
            channel = values[idx]
            power = float(values[idx + 6].split()[0])
            gauges["upstream_power"].labels(channel=channel).set(power)
        except:
            continue

def parse_ofdm(values):
    count = int(values[0])
    for i in range(count):
        idx = 1 + i * 11
        try:
            channel = values[idx]
            power = float(values[idx + 6].split()[0])
            snr = float(values[idx + 7].split()[0]) if "dB" in values[idx + 7] else 0.0
            unerrored = int(values[idx + 9])
            correctable = int(values[idx + 10])
            uncorrectable = int(values[idx + 11])
            gauges["ofdm_power"].labels(channel=channel).set(power)
            gauges["ofdm_snr"].labels(channel=channel).set(snr)
            gauges["ofdm_unerrored"].labels(channel=channel).set(unerrored)
            gauges["ofdm_correctable"].labels(channel=channel).set(correctable)
            gauges["ofdm_uncorrectable"].labels(channel=channel).set(uncorrectable)
        except:
            continue

def parse_ofdma(values):
    count = int(values[0])
    for i in range(count):
        idx = 1 + i * 6
        try:
            channel = values[idx]
            power = float(values[idx + 5].split()[0])
            gauges["ofdma_power"].labels(channel=channel).set(power)
        except:
            continue

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

def scrape():
    html = fetch_modem_data()
    if not html:
        return

    tag_values = extract_tag_value("InitTagValue", html)
    ds_values = extract_tag_value("InitDsTableTagValue", html)
    us_values = extract_tag_value("InitUsTableTagValue", html)
    ofdm_values = extract_tag_value("InitDsOfdmTableTagValue", html)
    ofdma_values = extract_tag_value("InitUsOfdmaTableTagValue", html)

    system_time, uptime = parse_time_values(tag_values)
    if system_time: gauges["system_time"].set(system_time)
    if uptime: gauges["uptime"].set(uptime)

    parse_downstream(ds_values)
    parse_upstream(us_values)
    parse_ofdm(ofdm_values)
    parse_ofdma(ofdma_values)

if __name__ == "__main__":
    print(f"Starting Prometheus metrics server on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)
    while True:
        scrape()
        time.sleep(30)
