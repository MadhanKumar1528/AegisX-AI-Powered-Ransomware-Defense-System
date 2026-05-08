import math
import os

def calculate_entropy(file_path):
    """
    Calculates the Shannon entropy of a file.
    High entropy (close to 8 for bytes) often indicates encryption or compression.
    """
    try:
        if not os.path.exists(file_path):
            return 0.0
            
        # Read file in chunks to handle large files
        chunk_size = 8192
        byte_counts = [0] * 256
        total_bytes = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                for byte in chunk:
                    byte_counts[byte] += 1
                total_bytes += len(chunk)
                
        if total_bytes == 0:
            return 0.0
            
        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                probability = count / total_bytes
                entropy -= probability * math.log2(probability)
                
        return entropy
        
    except Exception as e:
        print(f"Error calculating entropy for {file_path}: {e}")
        return 0.0
