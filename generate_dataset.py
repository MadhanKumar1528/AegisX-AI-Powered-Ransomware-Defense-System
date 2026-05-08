import pandas as pd
import numpy as np
import random
import os

def generate_dataset(num_samples=5000, output_file='dataset.csv'):
    """Generates a synthetic dataset for ransomware detection."""
    print(f"Generating synthetic dataset with {num_samples} samples...")
    data = []
    
    for _ in range(num_samples):
        # 0: Safe, 1: Suspicious, 2: Ransomware
        label = random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
        
        if label == 0:  # Safe
            cpu_usage = random.uniform(5.0, 45.0)
            ram_usage = random.uniform(20.0, 60.0)
            disk_write_rate = random.uniform(0.1, 5.0) # MB/s
            file_modification_rate = random.randint(0, 5) # files/sec
            file_rename_rate = random.randint(0, 2) # files/sec
            suspicious_extension_count = 0
            entropy_score = random.uniform(3.0, 5.5)
            process_count = random.randint(50, 150)
            
        elif label == 1:  # Suspicious (e.g., heavy legitimate task like compiling, zipping)
            cpu_usage = random.uniform(40.0, 85.0)
            ram_usage = random.uniform(50.0, 85.0)
            disk_write_rate = random.uniform(5.0, 20.0)
            file_modification_rate = random.randint(2, 15)
            file_rename_rate = random.randint(0, 5)
            suspicious_extension_count = random.randint(0, 1)
            entropy_score = random.uniform(4.5, 6.5)
            process_count = random.randint(100, 250)
            
        else:  # Ransomware
            cpu_usage = random.uniform(70.0, 100.0)
            ram_usage = random.uniform(60.0, 95.0)
            disk_write_rate = random.uniform(15.0, 100.0)
            file_modification_rate = random.randint(10, 100)
            file_rename_rate = random.randint(10, 80)
            suspicious_extension_count = random.randint(2, 20)
            entropy_score = random.uniform(7.0, 8.0) # High entropy (encrypted)
            process_count = random.randint(80, 200)

        data.append([
            cpu_usage, ram_usage, disk_write_rate, file_modification_rate,
            file_rename_rate, suspicious_extension_count, entropy_score, 
            process_count, label
        ])
        
    columns = [
        'cpu_usage', 'ram_usage', 'disk_write_rate', 'file_modification_rate',
        'file_rename_rate', 'suspicious_extension_count', 'entropy_score',
        'process_count', 'label'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}")

if __name__ == '__main__':
    generate_dataset()
