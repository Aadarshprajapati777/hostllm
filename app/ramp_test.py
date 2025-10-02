import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"
API_KEY = "token-abc123"

def ramp_up_test():
    """Gradually increase load to find breaking point"""
    print("📈 GRADUAL RAMP-UP TEST - FINDING BREAKING POINT")
    print("=" * 50)
    
    concurrency_levels = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50]
    
    for concurrency in concurrency_levels:
        print(f"\n🔁 Testing {concurrency} concurrent requests...")
        
        def make_request(i):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            
            data = {
                "model": "/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated",
                "messages": [
                    {"role": "user", "content": f"Ramp test {i} at concurrency {concurrency}: Answer 'OK'"}
                ],
                "max_tokens": 3,
                "temperature": 0.1
            }
            
            try:
                start_time = time.time()
                response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    return {"response_time": end_time - start_time, "success": True}
                else:
                    return {"success": False, "error": response.status_code}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Run test
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_request, i) for i in range(concurrency)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Analyze
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            response_times = [r['response_time'] for r in successful]
            print(f"   ✅ Success: {len(successful)}/{concurrency}")
            print(f"   ⏱️  Avg Time: {statistics.mean(response_times):.3f}s")
            print(f"   🚀 RPS: {len(successful)/total_time:.2f}")
        else:
            print(f"   ❌ ALL FAILED at concurrency {concurrency}")
            print("   ⚠️  Breaking point reached!")
            break
        
        if failed:
            print(f"   ❌ Failures: {len(failed)}")
            for fail in failed[:3]:  # Show first 3 errors
                print(f"      Error: {fail.get('error', 'Unknown')}")
        
        # Small delay between levels
        time.sleep(2)

if __name__ == "__main__":
    ramp_up_test()