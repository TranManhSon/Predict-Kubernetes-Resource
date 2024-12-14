import requests
import pandas as pd
import time
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://localhost:9090/api/v1/query_range"
QUERY = 'sum(rate(container_cpu_usage_seconds_total[5m])) by (service)'

# List services
services = [
    "adservice", "cartservice", "checkoutservice", "currencyservice",
    "emailservice", "frontend", "paymentservice", "productcatalogservice",
    "recommendationservice", "redis-cart", "shippingservice"
]

# Time
end_time = datetime.utcnow()
start_time = end_time - timedelta(days=10)
step = "5m"

# Result
results = []

for service in services:
    query = f'sum(rate(container_cpu_usage_seconds_total{{namespace="default", job="{service}", container!="POD", container!=""}}[{step}]))'
    params = {
        "query": QUERY,
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z",
        "step": step
    }

    # request to prometheus
    response = requests.get(PROMETHEUS_URL, params=params)
    data = response.json()

    if "data" in data and "result" in data["data"]:
        for item in data["data"]["result"]:
            for value in item["values"]:
                timestamp = datetime.utcfromtimestamp(value[0])
                cpu_usage = float(value[1])  # miliCPU
                results.append({
                    "Timestamp": timestamp,
                    "Service": service,
                    "Total CPU (m)": cpu_usage
                })

# Export to excel file
df = pd.DataFrame(results)
output_file = "service_cpu_usage.xlsx"
df.to_excel(output_file, index=False)
print(f"Data saved to {output_file}")