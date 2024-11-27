import matplotlib.pyplot as plt
import time
import libvirt
import datetime
from collections import deque
import threading

class CPUMonitor:
    def __init__(self, max_points=100):
        """Initialize the CPU monitor with a fixed window of data points."""
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.cpu_data = {
            'server1': deque(maxlen=max_points),
            'server2': deque(maxlen=max_points),
            'server3': deque(maxlen=max_points)  # For when it scales up
        }
        self.conn = libvirt.open("qemu:///system")
        self.running = False
        self.lock = threading.Lock()

    def get_cpu_usage(self, domain):
        """Calculate CPU usage percentage for a domain."""
        try:
            # Get CPU time initially
            prev_stats = domain.getCPUStats(True)[0]
            prev_total = prev_stats['cpu_time']
            
            time.sleep(1)  # Wait 1 second
            
            # Get CPU time again
            curr_stats = domain.getCPUStats(True)[0]
            curr_total = curr_stats['cpu_time']
            
            # Calculate CPU usage percentage
            cpu_usage = (curr_total - prev_total) / (1e9) * 100  # Convert ns to %
            return min(100.0, max(0.0, cpu_usage))  # Clamp between 0-100%
        except:
            return 0.0

    def collect_metrics(self):
        """Collect CPU metrics from all servers."""
        while self.running:
            current_time = datetime.datetime.now()
            
            with self.lock:
                self.timestamps.append(current_time)
                
                for server_name in ['server1', 'server2', 'server3']:
                    try:
                        domain = self.conn.lookupByName(server_name)
                        cpu_usage = self.get_cpu_usage(domain)
                        self.cpu_data[server_name].append(cpu_usage)
                    except libvirt.libvirtError:
                        self.cpu_data[server_name].append(0.0)  # Server not found
            
            time.sleep(5)  # Collect every 5 seconds

    def start_monitoring(self):
        """Start the monitoring thread."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self.collect_metrics)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()

    def plot_metrics(self, save_path='Monitoring/cpu_metrics.png'):
        """Plot the CPU usage metrics and save to file."""
        plt.figure(figsize=(12, 6))
        plt.clf()
        
        with self.lock:
            x_values = [t.strftime('%H:%M:%S') for t in self.timestamps]
            
            for server_name, cpu_data in self.cpu_data.items():
                if len(cpu_data) > 0:  # Only plot if we have data
                    plt.plot(x_values, cpu_data, label=server_name, marker='o', markersize=4)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.title('Server CPU Usage Over Time')
        plt.xlabel('Time')
        plt.ylabel('CPU Usage (%)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Add threshold line
        plt.axhline(y=80.0, color='r', linestyle='--', label='Scale Threshold')

        # Save the plot
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

def main():
    # Create and start the monitor
    monitor = CPUMonitor()
    monitor.start_monitoring()

    try:
        # Run for a desired duration (e.g., 5 minutes)
        duration = 100 # seconds
        print(f"Monitoring CPU usage for {duration} seconds...")
        time.sleep(duration)
    finally:
        # Stop monitoring and create the final plot
        monitor.stop_monitoring()
        monitor.plot_metrics()

if __name__ == "__main__":
    main()
