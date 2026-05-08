import psutil
import time
import os

last_disk_io = None
last_disk_time = None

def get_system_metrics():
    """Gathers CPU, RAM, and Disk I/O metrics."""
    global last_disk_io, last_disk_time
    
    cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking if called repeatedly
    ram_percent = psutil.virtual_memory().percent
    
    disk_io = psutil.disk_io_counters()
    current_time = time.time()
    
    disk_write_rate = 0.0 # MB/s
    if last_disk_io and last_disk_time:
        time_delta = current_time - last_disk_time
        write_bytes = disk_io.write_bytes - last_disk_io.write_bytes
        if time_delta > 0:
            disk_write_rate = (write_bytes / time_delta) / (1024 * 1024) # MB/s
            
    last_disk_io = disk_io
    last_disk_time = current_time
    
    process_count = len(psutil.pids())
    
    return {
        'cpu_usage': cpu_percent,
        'ram_usage': ram_percent,
        'disk_write_rate': max(0.0, disk_write_rate), # Ensure non-negative
        'process_count': process_count
    }

def get_suspicious_processes():
    """Identifies potentially suspicious processes based on high CPU/Disk usage."""
    suspicious = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Note: p.info['cpu_percent'] might be 0.0 on first call due to how psutil works.
            # For a real implementation, we'd keep process objects alive and poll them.
            if p.info['cpu_percent'] is not None and p.info['cpu_percent'] > 50.0:
                 suspicious.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return suspicious

def kill_process(pid):
    """Terminates a process by PID."""
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.terminate() # Or p.kill() for forceful exit
        return True, f"Killed process {name} (PID {pid})"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Access denied to kill process {pid}"
    except Exception as e:
        return False, str(e)
