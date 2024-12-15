import subprocess

deployments = {
    "adservice": 1,
    "cartservice": 1,
    "checkoutservice": 1,
    "currencyservice": 1,
    "frontend": 3,
    "emailservice": 1,
    "paymentservice": 1,
    "productcatalogservice": 1,
    "recommendationservice": 1,
    "redis-cart": 1,
    "shippingservice": 1
}

# funct update
def update_replicas(deployment_name, replicas):
    command = [
        "kubectl", "scale", "deployment", deployment_name,
        f"--replicas={replicas}", "-n", "default"
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Updated {deployment_name} to {replicas} replicas")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update {deployment_name}: {e}")

# Update
for deployment, replicas in deployments.items():
    update_replicas(deployment, replicas)
