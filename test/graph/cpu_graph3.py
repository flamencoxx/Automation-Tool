import matplotlib.pyplot as plt


# Function to convert memory size with units to kilobytes
def convert_to_kb(mem_str):
    if mem_str.lower().endswith('g'):
        return float(mem_str[:-1]) * 1024 * 1024  # Convert gigabytes to kilobytes
    elif mem_str.lower().endswith('m'):
        return float(mem_str[:-1]) * 1024  # Convert megabytes to kilobytes
    elif mem_str.lower().endswith('k'):
        return float(mem_str[:-1])  # Already in kilobytes
    else:
        return float(mem_str)  # Assume it's already in kilobytes if no unit


# Function to parse the log data from a file
def parse_log_file(file_path):
    cpu_usage = []
    mem_usage = []
    res_mem = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            cpu_usage.append(float(parts[8]))  # %CPU is the 9th element
            mem_usage.append(float(parts[9]))  # %MEM is the 10th element
            res_mem.append(convert_to_kb(parts[5]))  # RES is the 6th element
    return cpu_usage, mem_usage, res_mem


# Function to plot the usage data
def plot_usage(cpu_usage, mem_usage, res_mem, time):
    plt.figure(figsize=(12, 8))

    # Plotting CPU Usage
    plt.subplot(3, 1, 1)
    plt.plot(time, cpu_usage, label='CPU Usage (%)', color='b')
    plt.xlabel('Time (seconds)')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage Over Time')
    plt.legend()

    # Plotting Memory Usage
    plt.subplot(3, 1, 2)
    plt.plot(time, mem_usage, label='Memory Usage (%)', color='g')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Memory Usage (%)')
    plt.title('Memory Usage Over Time')
    plt.legend()

    # Plotting Resident Memory Usage
    plt.subplot(3, 1, 3)
    plt.plot(time, res_mem, label='Resident Memory (KB)', color='r')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Resident Memory (KB)')
    plt.title('Resident Memory Over Time')
    plt.legend()

    # Display the plots
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # Path to the log file
    log_file_path = 'C:\\github\\Prodlyze.ai.py\\test\\graph\\cpu_usage.log'

    # Parse the log data from the file
    cpu_usage, mem_usage, res_mem = parse_log_file(log_file_path)

    # Generate time points
    time_points = list(range(len(cpu_usage)))

    # Plot the usage data
    plot_usage(cpu_usage, mem_usage, res_mem, time_points)
