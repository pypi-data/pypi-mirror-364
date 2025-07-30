import requests
from typing import Optional

class QueueSizeTracker:
    def __init__(self):
        self.management_url = "http://localhost:15672"
        self.auth = ("guest", "guest")
    
    def get_queue_stats(self, queue_name: str) -> Optional[dict]:
        """Get queue statistics including message count and memory usage"""
        try:
            response = requests.get(
                f"{self.management_url}/api/queues/%2F/{queue_name}",  # %2F is URL encoded /
                auth=self.auth
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting queue stats: {e}")
            return None
    
    def get_queue_memory_usage(self, queue_name: str) -> Optional[int]:
        """Get approximate memory usage of queue in bytes"""
        stats = self.get_queue_stats(queue_name)
        if stats:
            # 'memory' field gives approximate memory usage in bytes
            return stats.get('memory', 0)
        return None
    
    def get_message_count(self, queue_name: str) -> Optional[int]:
        """Get number of messages in queue"""
        stats = self.get_queue_stats(queue_name)
        if stats:
            return stats.get('messages', 0)
        return None