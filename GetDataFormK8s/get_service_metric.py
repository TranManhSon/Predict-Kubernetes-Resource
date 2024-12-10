import subprocess
import pandas as pd
import time
from datetime import datetime

# get total CPU, Memory and number Pod
def get_service_metrics(service_label, namespace="default"):
    # run cmd kubectl top pod 
    result = subprocess.run(
        ["kubectl", "top", "pod", "-n", namespace, "--no-headers"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    # get Pods via service label selector
    service_pods = subprocess.run(
        ["kubectl", "get", "pods", "-l", f"app={service_label}", "-n", namespace, "--no-headers", "-o", "custom-columns=:metadata.name"],
        stdout=subprocess.PIPE,
        text=True
    ).stdout.strip().split("\n")
    
    lines = result.stdout.strip().split("\n")
    total_cpu = 0
    total_memory = 0
    pod_count = 0
    
    # loop lines of output kube cmd
    for line in lines:
        parts = line.split()
        pod_name = parts[0]
        
        if pod_name in service_pods:
            cpu_usage = int(parts[1].replace('m', ''))  # CPU used
            memory_usage = int(parts[2].replace('Mi', ''))  # Memory used
            
            total_cpu += cpu_usage
            total_memory += memory_usage
            pod_count += 1
    
    # timestamp
    current_timestamp = time.time()

    return {
        "Service Label": service_label,
        "Total CPU (m)": total_cpu,
        "Total Memory (Mi)": total_memory,
        "Pod Count": pod_count,
        "Timestamp": current_timestamp
    }

# define array of service
namespace = "default"
services = ["emailservice", "checkoutservice", "recommendationservice", "frontend", "paymentservice", "productcatalogservice", "cartservice", "redis-cart", "currencyservice", 
    "shippingservice", "adservice"]
output_file = "service_metrics_1.xlsx"

while True:
    all_metrics = []
    for service_label in services:
        metrics = get_service_metrics(service_label, namespace)
        all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    
    # Write data to file
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            if 'Sheet1' in writer.sheets:
                df.to_excel(writer, index=False, startrow=writer.sheets['Sheet1'].max_row, header=False)
            else:
                df.to_excel(writer, index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
    
    print(f"Data is appended {output_file}")
    
    time.sleep(60)
