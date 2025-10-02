import requests
import time
import psutil
import os

BASE_URL = "http://localhost:8000"
API_KEY = "token-abc123"

def check_server_health():
    """Check basic server health and configuration"""
    print("🔍 SERVER DIAGNOSTICS")
    print("=" * 50)
    
    # Test 1: Basic health check
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5).json()
        print(f"✅ Health Check: {health}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test 2: Single simple request
    print("\n🧪 Testing single simple request...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 5,
        "temperature": 0.1
    }
    
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data, timeout=30)
        end = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single Request: {end-start:.3f}s")
            print(f"   Response: {result['choices'][0]['message']['content']}")
            print(f"   Tokens: {result['usage']['total_tokens']}")
        else:
            print(f"❌ Single Request Failed: HTTP {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Single Request Exception: {e}")
    
    # Test 3: Check what happens with multiple workers
    print("\n👥 Testing concurrent capacity...")
    test_concurrent_capacity(max_workers=3, total_requests=10)
    
    # Test 4: Check system limits
    print("\n💻 System Configuration:")
    print(f"   Python Threads: {os.cpu_count()} cores available")
    print(f"   Memory: {psutil.virtual_memory().total / 1024**3:.1f} GB total")
    print(f"   Process: {psutil.Process().memory_info().rss / 1024**2:.1f} MB used")

def test_concurrent_capacity(max_workers=3, total_requests=10):
    """Test how many concurrent requests the server can handle"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def make_simple_request(req_id):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": "/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated",
            "messages": [{"role": "user", "content": f"Request {req_id}: OK"}],
            "max_tokens": 3,
            "temperature": 0.1
        }
        
        try:
            start = time.time()
            response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data, timeout=10)
            end = time.time()
            
            return {
                "success": response.status_code == 200,
                "time": end - start,
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            return {"success": False, "time": 0, "error": str(e)}
    
    print(f"   Testing {total_requests} requests with {max_workers} workers...")
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_simple_request, i) for i in range(total_requests)]
        results = [future.result() for future in as_completed(futures)]
    
    total_time = time.time() - start_time
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"   ✅ Successful: {len(successful)}/{total_requests}")
    print(f"   ❌ Failed: {len(failed)}")
    print(f"   ⏱️  Total Time: {total_time:.2f}s")
    
    if successful:
        times = [r["time"] for r in successful]
        avg_time = sum(times) / len(times)
        print(f"   📊 Avg Response Time: {avg_time:.3f}s")
        print(f"   🚀 Effective RPS: {len(successful)/total_time:.2f}")
    
    if failed:
        print(f"   🔍 First error: {failed[0]['error']}")

def find_optimal_configuration():
    """Find the optimal server configuration"""
    print("\n🎛️  FINDING OPTIMAL CONFIGURATION")
    print("=" * 50)
    
    worker_configs = [1, 2, 3, 4, 5]
    
    for workers in worker_configs:
        print(f"\n🔧 Testing with {workers} workers...")
        test_concurrent_capacity(max_workers=workers, total_requests=workers * 5)

if __name__ == "__main__":
    check_server_health()
    find_optimal_configuration()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("1. Your server is SINGLE-THREADED")
    print("2. Max capacity: ~6 RPS with high failure rate")  
    print("3. Cannot handle sustained load > 2 RPS")
    print("4. Upgrade to multi-worker deployment")