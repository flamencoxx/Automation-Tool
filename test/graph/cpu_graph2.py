import matplotlib.pyplot as plt

# Data extracted from the provided log
cpu_usage = [0.0, 0.0, 0.5, 0.5, 1.0, 0.5, 0.5, 0.0, 1.0, 0.0, 0.5, 2.0, 1.5, 29.5, 5.5, 1.0, 1.5, 1.0, 1.5, 1.0, 2.5, 1.0, 1.0, 0.5, 1.0, 3.0, 1.0, 1.5, 1.0, 0.5, 1.5, 0.0, 1.0, 2.5, 1.0, 0.5, 1.0, 2.0, 0.5, 3.0, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.5, 0.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.5, 0.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 0.0, 0.5, 0.5, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 1.5, 0.0, 0.5, 1.5, 1.5, 0.0]
mem_usage = [3.3] * 70 + [3.4] * 2  # Memory usage is constant at 3.3% except the last two entries

# Time points (assuming each entry represents a consecutive 2-second interval)
time = [i * 2 for i in range(len(cpu_usage))]

# Plotting CPU Usage
plt.subplot(2, 1, 1)
plt.plot(time, cpu_usage, label='CPU Usage (%)', color='b')
plt.xlabel('Time (seconds)')
plt.ylabel('CPU Usage (%)')
plt.title('CPU Usage Over Time')
plt.legend()

# Plotting Memory Usage
plt.subplot(2, 1, 2)
plt.plot(time, mem_usage, label='Memory Usage (%)', color='g')
plt.xlabel('Time (seconds)')
plt.ylabel('Memory Usage (%)')
plt.title('Memory Usage Over Time')
plt.legend()

# Display the plots
plt.tight_layout()
plt.show()
