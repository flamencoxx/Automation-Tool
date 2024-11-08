import matplotlib.pyplot as plt

def plot_usage(cpu_usage, mem_usage, time):
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

if __name__ == '__main__':
    # Data extracted from the provided log
    cpu_usage = [0.0, 0.0, 0.5, 0.5, 1.0, 0.5, 0.5, 0.0, 1.0, 0.0, 0.5, 2.0, 1.5, 29.5, 5.5, 1.0, 1.5, 1.0, 1.5, 1.0, 2.5, 1.0, 1.0, 0.5, 1.0, 3.0, 1.0, 1.5, 1.0, 0.5, 1.5, 0.0, 1.0, 2.5, 1.0, 0.5, 1.0, 2.0, 0.5, 3.0, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.5, 0.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.5, 0.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 0.0, 0.5, 0.5, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 1.5, 0.0, 0.5, 1.5, 1.5, 0.0]
    mem_usage = [3.3] * 70 + [3.4] * 2  # Memory usage is constant at 3.3% except the last two entries

    # Ensure all arrays have the same length
    min_length = min(len(cpu_usage), len(mem_usage))
    cpu_usage = cpu_usage[:min_length]
    mem_usage = mem_usage[:min_length]
    time = [i * 2 for i in range(min_length)]

    plot_usage(cpu_usage, mem_usage, time)
