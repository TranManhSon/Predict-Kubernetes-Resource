import subprocess
import pandas as pd
import time
from datetime import datetime

# Hàm lấy tổng CPU, Memory và số lượng Pod cho một service cụ thể
def get_service_metrics(service_label, namespace="default"):
    # Chạy lệnh kubectl top pod để lấy thông tin tài nguyên của tất cả các Pod
    result = subprocess.run(
        ["kubectl", "top", "pod", "-n", namespace, "--no-headers"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    # Lấy danh sách các Pod liên quan đến service thông qua label selector
    service_pods = subprocess.run(
        ["kubectl", "get", "pods", "-l", f"app={service_label}", "-n", namespace, "--no-headers", "-o", "custom-columns=:metadata.name"],
        stdout=subprocess.PIPE,
        text=True
    ).stdout.strip().split("\n")
    
    lines = result.stdout.strip().split("\n")
    total_cpu = 0
    total_memory = 0
    pod_count = 0
    
    # Duyệt qua từng dòng dữ liệu từ kubectl top
    for line in lines:
        parts = line.split()
        pod_name = parts[0]
        
        # Chỉ tính tài nguyên cho các Pod thuộc service
        if pod_name in service_pods:
            cpu_usage = int(parts[1].replace('m', ''))  # CPU sử dụng đơn vị mili-core
            memory_usage = int(parts[2].replace('Mi', ''))  # Memory sử dụng đơn vị MiB
            
            total_cpu += cpu_usage
            total_memory += memory_usage
            pod_count += 1
    
    # Thêm timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Trả về dữ liệu với service label và timestamp
    return {
        "Service Label": service_label,
        "Total CPU (m)": total_cpu,
        "Total Memory (Mi)": total_memory,
        "Pod Count": pod_count,
        "Timestamp": current_timestamp
    }

# Lấy dữ liệu cho nhiều service
namespace = "default"
services = ["emailservice", "checkoutservice", "recommendationservice", "frontend", "paymentservice", "productcatalogservice", "cartservice", "redis-cart", "currencyservice", 
    "shippingservice", "adservice"]
output_file = "service_metrics.xlsx"


while True:
    all_metrics = []
    for service_label in services:
        metrics = get_service_metrics(service_label, namespace)
        all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    df.to_excel(output_file, index=False)
    
    print(f"Dữ liệu đã được lưu vào {output_file}")
    
    # Đợi 60 giây trước khi lấy dữ liệu tiếp theo
    time.sleep(30)
