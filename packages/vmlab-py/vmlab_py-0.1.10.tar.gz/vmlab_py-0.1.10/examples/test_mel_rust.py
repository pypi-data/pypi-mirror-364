#!/usr/bin/env python3
"""
Test script to generate mel spectrogram using Rust implementation (RTMelV2)
"""
import sys
import os
import numpy as np
import librosa

# Add the project root to the path to import the compiled Rust module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import vmlab_py
except ImportError as e:
    print(f"Error importing vmlab_py: {e}")
    print("Please make sure the Rust module is compiled with 'maturin develop' or 'cargo build'")
    sys.exit(1)

def main():
    # Read the test wav file
    wav_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'test.wav')
    
    if not os.path.exists(wav_path):
        print(f"Error: {wav_path} not found!")
        return
    
    print(f"Reading audio from: {wav_path}")
    
    # Load audio with librosa (same as Python implementation)
    wav, sr = librosa.load(wav_path, sr=16000, mono=True)
    print(f"Audio shape: {wav.shape}, Sample rate: {sr}")
    
    # Initialize RTMelV2
    rt_mel = vmlab_py.RTMelV2(sr)
    
    # Process the audio in streaming chunks
    chunk_size = 200  # 200ms chunks at 16kHz (same as hop_length * 16)
    all_results = []
    
    print("Processing audio through RTMelV2 (streaming)...")
    
    for i in range(0, len(wav), chunk_size):
        chunk = wav[i:i+chunk_size]
        
        # Pad the last chunk if necessary
        # if len(chunk) < chunk_size:
        #     chunk = np.pad(chunk, (0, chunk_size - len(chunk)), mode='constant')
        
        # Convert to float32 numpy array
        chunk_array = chunk.astype(np.float32)
        
        try:
            # Transform the chunk
            result = rt_mel.transform(chunk_array)
            
            if result:  # If we got a result
                all_results.extend(result)
                print(f"Processed chunk {i//chunk_size + 1}, got {len(result)} frames")
            
        except Exception as e:
            print(f"Error processing chunk {i//chunk_size + 1}: {e}")
    
    print(f"Total results: {len(all_results)} frames")
    
    if all_results:
        # Convert results to numpy array
        # Note: The exact format depends on how RTMelV2.transform returns data
        # You may need to adjust this based on the actual output format
        
        # For now, let's save the raw results
        output_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'rust_mel.npy')
        
        # If results are bytes, we need to convert them
        try:
            # Assuming each result is bytes that can be converted to numpy array
            mel_data = []
            for result_bytes in all_results:
                # Convert bytes to numpy array (adjust shape as needed)
                # This depends on the actual output format from RTMelV2
                arr = np.frombuffer(result_bytes, dtype=np.float32)
                mel_data.append(arr)
            
            if mel_data:
                mel_array = np.array(mel_data)
                np.save(output_path, mel_array)
                print(f"Saved Rust mel spectrogram to: {output_path}")
                print(f"Mel spectrogram shape: {mel_array.shape}")
                print(f"Mel spectrogram dtype: {mel_array.dtype}")
                print(f"Mel spectrogram min: {mel_array.min():.6f}")
                print(f"Mel spectrogram max: {mel_array.max():.6f}")
                print(f"Mel spectrogram mean: {mel_array.mean():.6f}")
                print(f"Mel spectrogram std: {mel_array.std():.6f}")
                
                # Save debug info
                debug_info = {
                    'shape': mel_array.shape,
                    'min': mel_array.min(),
                    'max': mel_array.max(),
                    'mean': mel_array.mean(),
                    'std': mel_array.std(),
                    'num_chunks_processed': len(all_results),
                    'chunk_size': chunk_size,
                }
                
                debug_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'rust_mel_debug.txt')
                with open(debug_path, 'w') as f:
                    for key, value in debug_info.items():
                        f.write(f"{key}: {value}\n")
                
                print(f"Saved debug info to: {debug_path}")
            
        except Exception as e:
            print(f"Error converting results to numpy: {e}")
            # Save raw results as backup
            backup_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'rust_mel_raw.txt')
            with open(backup_path, 'w') as f:
                f.write(f"Number of results: {len(all_results)}\n")
                for i, result in enumerate(all_results[:5]):  # Just first 5 for debugging
                    f.write(f"Result {i}: {type(result)}, length: {len(result) if hasattr(result, '__len__') else 'N/A'}\n")
            print(f"Saved raw results info to: {backup_path}")
    
    else:
        print("No results obtained from RTMelV2")

if __name__ == "__main__":
    main()
