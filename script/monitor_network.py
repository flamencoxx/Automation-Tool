import psutil
import time
import logging
import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    filename='windows_monitor.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configuration parameters
LOCAL_IP = '192.168.32.182'
LOCAL_PORT = 8080
REMOTE_IP = '192.168.32.20'
REMOTE_PORT = 38081
MONITOR_DURATION = 7200  # 2 hours in seconds


def format_duration(seconds):
    """Format duration time"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"


def get_connection_key(conn):
    """Generate unique key for connection"""
    return f"{conn.laddr.ip}:{conn.laddr.port}-{conn.raddr.ip}:{conn.raddr.port}"


def get_current_time():
    """Get current time with millisecond precision"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def log_and_print(message, level='info'):
    """Unified logging and console output"""
    current_time = get_current_time()
    formatted_message = f"{current_time} - {message}"
    print(formatted_message)

    if level == 'info':
        logging.info(message)
    elif level == 'error':
        logging.error(message)
    elif level == 'warning':
        logging.warning(message)


def monitor_connections():
    previous_connections = set()
    connection_start_times = {}
    connection_status = {}

    start_time = time.time()
    end_time = start_time + MONITOR_DURATION

    log_and_print(f"Starting Windows connection monitoring, duration: 2 hours")
    log_and_print(f"Local IP: {LOCAL_IP}, Remote IP: {REMOTE_IP}")
    log_and_print(f"Monitoring start time: {get_current_time()}")
    log_and_print(f"Expected end time: {datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")

    while time.time() < end_time:
        try:
            current_connections = set()
            current_time = time.time()

            # Get all TCP connections
            for conn in psutil.net_connections(kind='tcp'):
                if conn.raddr and (
                        (conn.laddr.ip == LOCAL_IP and conn.raddr.ip == REMOTE_IP and conn.raddr.port == REMOTE_PORT) or
                        (conn.raddr.ip == LOCAL_IP and conn.laddr.ip == REMOTE_IP and conn.laddr.port == REMOTE_PORT)
                ):
                    conn_key = get_connection_key(conn)
                    current_connections.add(conn_key)

                    # New connection established
                    if conn_key not in previous_connections:
                        connection_start_times[conn_key] = current_time
                        connection_status[conn_key] = conn.status
                        log_and_print(f"New connection established: {conn_key}\nStatus: {conn.status}")

                    # Connection status changed
                    elif connection_status.get(conn_key) != conn.status:
                        log_and_print(
                            f"Connection status changed: {conn_key}\nPrevious status: {connection_status[conn_key]}\nNew status: {conn.status}")
                        connection_status[conn_key] = conn.status

            # Check disconnected connections
            for conn_key in previous_connections - current_connections:
                if conn_key in connection_start_times:
                    duration = current_time - connection_start_times[conn_key]
                    log_and_print(f"Connection closed: {conn_key}\nDuration: {format_duration(duration)}")
                    del connection_start_times[conn_key]
                    del connection_status[conn_key]

            previous_connections = current_connections

            # Display remaining monitoring time
            remaining_time = end_time - current_time
            if int(remaining_time) % 300 == 0:  # Show remaining time every 5 minutes
                log_and_print(f"Remaining monitoring time: {format_duration(remaining_time)}")

            time.sleep(0.3)  # Use smaller check interval (100ms)

        except Exception as e:
            log_and_print(f"Monitoring error: {str(e)}", level='error')
            time.sleep(1)

    log_and_print("Monitoring completed, reached preset duration")


if __name__ == "__main__":
    monitor_connections()