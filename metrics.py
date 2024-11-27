import random
import time
import matplotlib.pyplot as plt

# Initialize parameters
time_points = []
cpu_vm1 = []
cpu_vm2 = []
vm1_utilization = 20  # Starting utilization of VM1
vm2_utilization = 0   # VM2 is not active initially
auto_scale_threshold = 80  # The threshold for triggering autoscaling
auto_scale_time = 150     # Time (in seconds) when autoscaling happens
duration = 300           # Total simulation time (in seconds)

# Simulate CPU utilization tracking
for t in range(0, duration + 1, 30):  # Simulate every 30 seconds
    time_points.append(t)
    
    # Simulate CPU usage for VM1 before autoscaling
    if t < auto_scale_time:
        vm1_utilization += random.randint(5, 15)  # Increase load on VM1
        if vm1_utilization > auto_scale_threshold:  # Trigger autoscaling
            vm1_utilization = auto_scale_threshold  # Limit CPU usage to prevent overload
    else:
        # After autoscaling, VM2 starts handling some load
        if vm2_utilization == 0:
            vm2_utilization = 10  # Start VM2 usage once autoscaling happens
        # Distribute load between VM1 and VM2
        vm1_utilization -= random.randint(5, 10)
        vm2_utilization += random.randint(5, 10)

    cpu_vm1.append(vm1_utilization)
    cpu_vm2.append(vm2_utilization)

    # Wait for the next time step (simulating real-time)
    time.sleep(1)

# Plot the results
plt.figure(figsize=(12, 6))

# Plot CPU Utilization of VM1 and VM2
plt.plot(time_points, cpu_vm1, label='VM1 CPU Utilization', marker='o', linestyle='-', color='blue')
plt.plot(time_points, cpu_vm2, label='VM2 CPU Utilization', marker='o', linestyle='--', color='green')

# Annotate the autoscaling event
plt.axvline(x=auto_scale_time, color='red', linestyle='--', label='Autoscaling Trigger (VM2 Launched)')
plt.text(auto_scale_time + 10, 45, 'VM2 Launched', color='red', fontsize=10)

# Add titles and labels
plt.title("CPU Utilization Before and After Autoscaling", fontsize=14)
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("CPU Utilization (%)", fontsize=12)
plt.xticks(range(0, duration + 1, 30))
plt.yticks(range(0, 110, 10))
plt.grid(True, linestyle='--', alpha=0.7)

# Add legend
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()
