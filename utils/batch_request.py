import aiohttp
import asyncio
import time
from typing import List, Dict, Any
from datetime import datetime
import threading
import sys

# Add timeout constant (10 minutes)
TIMEOUT = aiohttp.ClientTimeout(total=600)

class RequestTimer:
    def __init__(self, request_num, total, source_id):
        self.request_num = request_num
        self.total = total
        self.source_id = source_id
        self.start_time = time.time()
        self.is_running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True

    def _run(self):
        while self.is_running:
            elapsed = time.time() - self.start_time
            sys.stdout.write(f"\rRequest {self.request_num}/{self.total} ({self.source_id}): {elapsed:.1f}s elapsed")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
        sys.stdout.flush()

    def start(self):
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.join()

async def batch_request(url: str, params_list: List[Dict[str, Any]], concurrent_limit: int = 5, method: str = 'POST', show_timestamp: bool = False) -> Dict[str, Any]:
    """Process multiple requests asynchronously with rate limiting."""
    def log_with_timestamp(message: str):
        if show_timestamp:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}")
        else:
            print(f"\n{message}")

    log_with_timestamp(f"Starting batch request processing...")
    log_with_timestamp(f"Total requests to process: {len(params_list)}")
    log_with_timestamp(f"Concurrent limit: {concurrent_limit}")
    
    batch_start_time = time.time()
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        semaphore = asyncio.Semaphore(concurrent_limit)
        total = len(params_list)
        
        async def bounded_request(params, request_num):
            async with semaphore:
                timer = RequestTimer(request_num, total, params['source_id'])
                timer.start()
                try:
                    async with getattr(session, method.lower())(url, json=params) as response:
                        response.raise_for_status()
                        timer.stop()
                        elapsed = time.time() - timer.start_time
                        log_with_timestamp(f"✓ Request {request_num}/{total} completed successfully: {params['source_id']} ({elapsed:.2f}s)")
                        return {
                            'success': True,
                            'params': params,
                            'status': response.status,
                            'data': await response.json(),
                            'elapsed': elapsed
                        }
                except Exception as e:
                    timer.stop()
                    elapsed = time.time() - timer.start_time
                    log_with_timestamp(f"✗ Request {request_num}/{total} failed: {params['source_id']} - Error: {str(e)} ({elapsed:.2f}s)")
                    return {
                        'success': False,
                        'params': params,
                        'error': str(e),
                        'elapsed': elapsed
                    }

        tasks = [bounded_request(params, i+1) for i, params in enumerate(params_list)]
        results = await asyncio.gather(*tasks)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        total_time = time.time() - batch_start_time
        avg_time = sum(r['elapsed'] for r in results) / len(results) if results else 0
        
        print(f"\nBatch processing completed in {total_time:.2f}s:")
        print(f"Average request time: {avg_time:.2f}s")
        print(f"Total processed: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}\n")
        
        return {
            'total': len(results),
            'success_count': len(successful),
            'error_count': len(failed),
            'successful': successful,
            'failed': failed,
            'total_time': total_time,
            'average_time': avg_time
        }

def run_batch_request(url: str, params_list: List[Dict[str, Any]], concurrent_limit: int = 5, method: str = 'POST', show_timestamp: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for batch_request."""
    return asyncio.run(batch_request(url, params_list, concurrent_limit, method, show_timestamp))