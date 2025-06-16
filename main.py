import requests
import json
import time
import os
from datetime import datetime

class NetworkMonitor:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.last_ip = None
        
    def get_network_status(self):
        """Kiểm tra trạng thái kết nối mạng"""
        try:
            # Thử nhiều service để đảm bảo độ tin cậy
            services = [
                "https://api.ipify.org?format=json",
                "https://httpbin.org/ip",
                "https://api.my-ip.io/ip.json",
                "https://ipapi.co/json/"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Xử lý format khác nhau của các API
                        if 'ip' in data:
                            return data['ip']
                        elif 'origin' in data:
                            return data['origin']
                        
                except Exception as e:
                    print(f"Service {service} failed: {e}")
                    continue
                    
            return None
            
        except Exception as e:
            print(f"Error getting IP: {e}")
            return None
    
    def get_location_info(self, address):
        """Lấy thông tin vị trí từ địa chỉ mạng"""
        try:
            response = requests.get(f"http://ip-api.com/json/{address}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting location info: {e}")
        return {}
    
    def send_notification(self, message):
        """Gửi thông báo hệ thống"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(self.telegram_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("Notification sent successfully")
                return True
            else:
                print(f"Failed to send notification: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def format_system_report(self, address, location_info, is_changed=False):
        """Tạo báo cáo trạng thái hệ thống"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_changed:
            status = "🔄 <b>NETWORK STATUS CHANGED</b>"
        else:
            status = "📊 <b>SYSTEM STATUS REPORT</b>"
        
        message = f"""
{status}

🌐 <b>Network Address:</b> <code>{address}</code>
⏰ <b>Timestamp:</b> {current_time}

📍 <b>Location Details:</b>
• Country: {location_info.get('country', 'N/A')} ({location_info.get('countryCode', 'N/A')})
• City: {location_info.get('city', 'N/A')}
• Region: {location_info.get('regionName', 'N/A')}

🌍 <b>ISP:</b> {location_info.get('isp', 'N/A')}
🏢 <b>Organization:</b> {location_info.get('org', 'N/A')}

📊 <b>Coordinates:</b> {location_info.get('lat', 'N/A')}, {location_info.get('lon', 'N/A')}
🕐 <b>Timezone:</b> {location_info.get('timezone', 'N/A')}
        """
        
        return message.strip()
    
    def monitor_and_notify(self):
        """Monitor network và gửi thông báo nếu có thay đổi"""
        current_address = self.get_network_status()
        
        if not current_address:
            error_msg = f"❌ <b>SYSTEM ERROR:</b> Cannot retrieve network status\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_notification(error_msg)
            return False
        
        print(f"Current Network Address: {current_address}")
        
        # Kiểm tra có thay đổi không
        is_changed = self.last_ip is not None and self.last_ip != current_address
        
        # Lấy thông tin location
        location_info = self.get_location_info(current_address)
        
        # Gửi thông báo nếu có thay đổi hoặc lần đầu chạy
        if is_changed or self.last_ip is None:
            message = self.format_system_report(current_address, location_info, is_changed)
            
            if self.send_notification(message):
                self.last_ip = current_address
                return True
        
        self.last_ip = current_address
        return True
    
    def run_continuous_monitoring(self, interval=300):
        """Chạy liên tục monitor system"""
        print(f"Starting Network Monitoring Service... Check interval: {interval} seconds")
        
        # Gửi thông báo khởi động
        start_msg = f"🚀 <b>NETWORK MONITOR STARTED</b>\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🔄 Check interval: {interval}s"
        self.send_notification(start_msg)
        
        # Monitor ngay lập tức
        self.monitor_and_notify()
        
        # Loop kiểm tra định kỳ
        while True:
            try:
                time.sleep(interval)
                self.monitor_and_notify()
            except KeyboardInterrupt:
                print("\nStopping Network Monitor...")
                stop_msg = f"⛔ <b>NETWORK MONITOR STOPPED</b>\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.send_notification(stop_msg)
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry

def main():
    # Lấy config từ environment variables hoặc hardcode
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7657217421:AAFcCRGCbDARpPVw8h-WvJfQ5FFcoCVfL1I')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7657217421')
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default
    
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Chat ID: {CHAT_ID}")
    print(f"Monitor Interval: {CHECK_INTERVAL}s")
    
    # Khởi tạo network monitor
    network_monitor = NetworkMonitor(BOT_TOKEN, CHAT_ID)
    
    # Chạy mode
    mode = os.getenv('RUN_MODE', 'continuous')
    
    if mode == 'once':
        # Chạy 1 lần (cho GitHub Actions)
        print("Running in ONCE mode...")
        network_monitor.monitor_and_notify()
    else:
        # Chạy liên tục
        print("Running in CONTINUOUS mode...")
        network_monitor.run_continuous_monitoring(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
