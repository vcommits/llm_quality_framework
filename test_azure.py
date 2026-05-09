import sys
print("1. Starting Azure test...")
sys.stdout.flush()
try:
    from azure.cosmos import CosmosClient
    print("2. Azure library loaded successfully!")
except Exception as e:
    print(f"Error: {e}")
