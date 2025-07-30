import requests
import json
from typing import Optional, Dict, Any

class QueueSizeTracker:
    def __init__(self, management_url: str = "http://localhost:15672", 
                 username: str = "guest", password: str = "guest"):
        self.management_url = management_url.rstrip('/')
        self.auth = (username, password)
    
    def get_queue_stats(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Get complete queue statistics from RabbitMQ Management API"""
        try:
            # %2F is URL encoded forward slash for default vhost "/"
            url = f"{self.management_url}/api/queues/%2F/{queue_name}"
            response = requests.get(url, auth=self.auth, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Queue '{queue_name}' not found")
                return None
            else:
                print(f"Error: HTTP {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to RabbitMQ Management API: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def get_queue_size_info(self, queue_name: str) -> Dict[str, Any]:
        """Get queue size and message count information"""
        stats = self.get_queue_stats(queue_name)
        
        if not stats:
            return {
                "queue_name": queue_name,
                "message_count": 0,
                "memory_bytes": 0,
                "memory_mb": 0.0,
                "ready_messages": 0,
                "unacked_messages": 0,
                "status": "error"
            }
        
        # Extract relevant information
        message_count = stats.get('messages', 0)
        memory_bytes = stats.get('memory', 0)
        ready_messages = stats.get('messages_ready', 0)
        unacked_messages = stats.get('messages_unacknowledged', 0)
        
        return {
            "queue_name": queue_name,
            "message_count": message_count,
            "memory_bytes": memory_bytes,
            "memory_mb": round(memory_bytes / (1024 * 1024), 2),
            "ready_messages": ready_messages,
            "unacked_messages": unacked_messages,
            "status": "success"
        }
    
    def print_queue_info(self, queue_name: str) -> None:
        """Print formatted queue information"""
        info = self.get_queue_size_info(queue_name)
        
        print(f"\n{'='*50}")
        print(f"Queue: {info['queue_name']}")
        print(f"{'='*50}")
        
        if info['status'] == 'error':
            print("❌ Could not retrieve queue information")
            return
        
        print(f"📊 Total Messages: {info['message_count']:,}")
        print(f"✅ Ready Messages: {info['ready_messages']:,}")
        print(f"⏳ Unacked Messages: {info['unacked_messages']:,}")
        print(f"💾 Memory Usage: {info['memory_bytes']:,} bytes ({info['memory_mb']} MB)")
        
        if info['message_count'] > 0:
            avg_size = info['memory_bytes'] / info['message_count']
            print(f"📏 Average Message Size: {avg_size:.2f} bytes")
    
    def get_all_queues(self) -> Optional[list]:
        """Get list of all queues"""
        try:
            url = f"{self.management_url}/api/queues"
            response = requests.get(url, auth=self.auth, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting queues: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting all queues: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    queue_name = "data_queue"
    
    # Initialize tracker with default RabbitMQ settings
    # Change these if your RabbitMQ has different credentials/URL
    tracker = QueueSizeTracker(
        management_url="http://localhost:15672",
        username="guest", 
        password="guest"
    )
    
    print("🐰 RabbitMQ Queue Size Checker")
    print("================================")
    
    # Print info for the specific queue
    tracker.print_queue_info(queue_name)
    
