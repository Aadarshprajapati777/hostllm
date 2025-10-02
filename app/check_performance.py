import requests
import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"
API_KEY = "token-abc123"

def test_single_request():
    """Test single request response time"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated",
        "messages": [
            {"role": "user", "content": "What is the capital of France? Answer in one word."}
        ],
        "max_tokens": 10,
        "temperature": 0.7
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        return {
            "response_time": end_time - start_time,
            "tokens_used": result["usage"]["total_tokens"],
            "content": result["choices"][0]["message"]["content"]
        }
    else:
        return {"error": response.text}

def test_concurrent_requests(num_requests=10, max_workers=5):
    """Test concurrent requests"""
    def make_request(i):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": "/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated",
            "messages": [
                {"role": "user", "content": f"Request {i}: What is {i} + {i}? Answer with just the number."}
            ],
            "max_tokens": 5,
            "temperature": 0.1
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data)
        end_time = time.time()
        
        return {
            "request_id": i,
            "response_time": end_time - start_time,
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
    
    print(f"🚀 Testing {num_requests} concurrent requests with {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        results = [future.result() for future in as_completed(futures)]
    
    return results

def test_different_prompt_lengths():
    """Test performance with different prompt lengths"""
    test_prompts = [
        "Hi",  # Very short
        "Explain machine learning in one sentence",  # Short
        "Write a detailed explanation of artificial intelligence including its history, current applications, and future potential",  # Long
    ]
    
    results = []
    for i, prompt in enumerate(test_prompts):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": "/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            results.append({
                "prompt_length": len(prompt),
                "response_time": end_time - start_time,
                "tokens_used": result["usage"]["total_tokens"]
            })
    
    return results

def analyze_results(results):
    """Analyze and print performance results"""
    response_times = [r["response_time"] for r in results if "response_time" in r]
    
    if response_times:
        print(f"📊 Performance Analysis:")
        print(f"   Total Requests: {len(results)}")
        print(f"   Successful: {len([r for r in results if r.get('success', True)])}")
        print(f"   Average Response Time: {statistics.mean(response_times):.3f}s")
        print(f"   Median Response Time: {statistics.median(response_times):.3f}s")
        print(f"   Min Response Time: {min(response_times):.3f}s")
        print(f"   Max Response Time: {max(response_times):.3f}s")
        print(f"   Standard Deviation: {statistics.stdev(response_times):.3f}s")
        
        # Calculate requests per second
        total_time = sum(response_times)
        rps = len(results) / total_time if total_time > 0 else 0
        print(f"   Estimated RPS: {rps:.2f} requests/second")

if __name__ == "__main__":
    print("🎯 Performance Testing Mistral API Server\n")
    
    # Test 1: Single request
    print("1. Single Request Test:")
    single_result = test_single_request()
    if "error" not in single_result:
        print(f"   ✅ Response Time: {single_result['response_time']:.3f}s")
        print(f"   ✅ Tokens Used: {single_result['tokens_used']}")
        print(f"   ✅ Response: {single_result['content']}")
    else:
        print(f"   ❌ Error: {single_result['error']}")
    print()
    
    # Test 2: Concurrent requests
    print("2. Concurrent Requests Test:")
    concurrent_results = test_concurrent_requests(num_requests=10, max_workers=3)
    analyze_results(concurrent_results)
    print()
    
    # Test 3: Different prompt lengths
    print("3. Prompt Length Impact Test:")
    length_results = test_different_prompt_lengths()
    for result in length_results:
        print(f"   Prompt {result['prompt_length']} chars: {result['response_time']:.3f}s, {result['tokens_used']} tokens")