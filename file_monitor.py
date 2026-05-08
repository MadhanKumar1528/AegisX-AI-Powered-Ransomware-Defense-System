import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from .entropy_detector import calculate_entropy
import os
import shutil

# Global state to share with ML process
file_stats = {
    'modifications': 0,
    'renames': 0,
    'suspicious_extensions': 0,
    'high_entropy_files': 0,
    'avg_entropy': 0.0,
    'total_entropy_calc': 0
}

SUSPICIOUS_EXTENSIONS = ['.locked', '.encrypted', '.crypt', '.wnry', '.crypted']
HONEYPOT_DIR = 'honeypot'
QUARANTINE_DIR = 'quarantine'

class RansomwareFileHandler(FileSystemEventHandler):
    def __init__(self, alert_callback):
        self.alert_callback = alert_callback

    def on_modified(self, event):
        if not event.is_directory:
            file_stats['modifications'] += 1
            self._check_file(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            file_stats['modifications'] += 1
            self._check_file(event.src_path, "created")

    def on_moved(self, event):
        if not event.is_directory:
            file_stats['renames'] += 1
            self._check_file(event.dest_path, "renamed")
            
    def _check_file(self, file_path, action):
        # 1. Check Honeypot
        if HONEYPOT_DIR in file_path:
            self.alert_callback("CRITICAL", "Honeypot Triggered", f"File {action} in honeypot: {file_path}")
            return
            
        # 2. Check Extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() in SUSPICIOUS_EXTENSIONS:
            file_stats['suspicious_extensions'] += 1
            self.alert_callback("HIGH", "Suspicious Extension", f"File with suspicious extension {ext} {action}: {file_path}")
            
        # 3. Check Entropy (sample some files to save CPU)
        if file_stats['modifications'] % 5 == 0: 
            entropy = calculate_entropy(file_path)
            if entropy > 0:
                # Update rolling average
                file_stats['total_entropy_calc'] += 1
                n = file_stats['total_entropy_calc']
                old_avg = file_stats['avg_entropy']
                file_stats['avg_entropy'] = old_avg + (entropy - old_avg) / n
                
                if entropy > 7.5:
                    file_stats['high_entropy_files'] += 1
                    # self.alert_callback("MEDIUM", "High Entropy File", f"File {file_path} has high entropy ({entropy:.2f})")

def start_monitoring(paths_to_monitor, alert_callback):
    """Starts watchdog observers on given paths."""
    print(f"Starting file monitoring on {paths_to_monitor}")
    
    # Ensure dirs exist
    os.makedirs(HONEYPOT_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    
    # Create honeypot files
    with open(os.path.join(HONEYPOT_DIR, 'passwords.txt'), 'w') as f: f.write("admin:1234\n")
    with open(os.path.join(HONEYPOT_DIR, 'bank.xlsx'), 'w') as f: f.write("dummy data")
    
    # Add honeypot to monitor paths if not there
    if HONEYPOT_DIR not in paths_to_monitor:
        paths_to_monitor.append(HONEYPOT_DIR)
        
    observers = []
    event_handler = RansomwareFileHandler(alert_callback)
    
    for path in paths_to_monitor:
        if os.path.exists(path):
            observer = Observer()
            observer.schedule(event_handler, path, recursive=True)
            observer.start()
            observers.append(observer)
            
    return observers

def reset_stats():
    """Reset counters every second for rate calculation"""
    stats_copy = file_stats.copy()
    file_stats['modifications'] = 0
    file_stats['renames'] = 0
    file_stats['suspicious_extensions'] = 0
    file_stats['high_entropy_files'] = 0
    # Keep avg_entropy running
    return stats_copy
