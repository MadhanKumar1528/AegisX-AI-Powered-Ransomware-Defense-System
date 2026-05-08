import os
import time
import math
import random
import string
import multiprocessing

# BENIGN LOAD GENERATOR FOR TESTING DETECTION SYSTEM
# This script generates high CPU usage and rapid file modifications
# to test the real-time monitoring and ML prediction without being malicious.

TEST_DIR = 'test_load_dir'

def stress_cpu():
    """Generates high CPU load."""
    print(f"Stressing CPU in process {os.getpid()}...")
    while True:
        _ = math.factorial(500)

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def stress_disk():
    """Generates rapid file creations and high entropy data."""
    print("Stressing Disk and generating high entropy files...")
    os.makedirs(TEST_DIR, exist_ok=True)
    
    file_count = 0
    while True:
        filename = os.path.join(TEST_DIR, f"test_file_{file_count}.locked")
        
        # Write high entropy data (random bytes)
        with open(filename, 'wb') as f:
            f.write(os.urandom(1024 * 1024)) # 1MB of random bytes (high entropy)
            
        file_count += 1
        time.sleep(0.1) # 10 files per second

if __name__ == '__main__':
    print("Starting Benign Load Generator...")
    print("WARNING: This will consume high CPU and Disk IO. Close when done testing.")
    
    # Start CPU stress in multiple processes
    cpu_processes = []
    for _ in range(multiprocessing.cpu_count() - 1):
        p = multiprocessing.Process(target=stress_cpu)
        p.start()
        cpu_processes.append(p)
        
    # Start disk stress in main process
    try:
        stress_disk()
    except KeyboardInterrupt:
        print("\nStopping...")
        for p in cpu_processes:
            p.terminate()
            
        # Cleanup
        print("Cleaning up test files...")
        for f in os.listdir(TEST_DIR):
            os.remove(os.path.join(TEST_DIR, f))
        os.rmdir(TEST_DIR)
        print("Done.")
