import requests
import pandas as pd
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"

services = [
    "emailservice",
    "checkoutservice",
    "recommendationservice",
    "frontend",
    "paymentservice",
    "productcatalogservice",
    "cartservice",
    "redis-cart",
    "currencyservice",
    "shippingservice",
    "adservice"
]

# Get data form prometheus
def get_cpu_metrics(service_name, namespace="default"):
    queries = {
        "avg": f"avg(rate(container_cpu_usage_seconds_total{{namespace='{namespace}', pod=~'{service_name}.*'}}[5m]))",
        "min": f"min(rate(container_cpu_usage_seconds_total{{namespace='{namespace}', pod=~'{service_name}.*'}}[5m]))",
        "max": f"max(rate(container_cpu_usage_seconds_total{{namespace='{namespace}', pod=~'{service_name}.*'}}[5m]))"
    }

    results = {}
    for metric, query in queries.items():
        response = requests.get(PROMETHEUS_URL, params={'query': query})
        data = response.json()
        results[metric] = data['data']['result'][0]['value'][1] if data['data']['result'] else 'N/A'
    return results

# Get cpu usage per service
data = []
current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for service in services:
    metrics = get_cpu_metrics(service)
    data.append({
        "Service Label": service,
        "Avg CPU (cores)": metrics['avg'],
        "Min CPU (cores)": metrics['min'],
        "Max CPU (cores)": metrics['max'],
        "Timestamp": current_timestamp
    })

# convert to dataframe
df = pd.DataFrame(data)

# save file
output_file = "/root/Service_Metrics_with_Timestamp.xlsx"
df.to_excel(output_file, index=False, sheet_name="Service Metrics")

print(f"Data is exported to file Excel: {output_file}")

