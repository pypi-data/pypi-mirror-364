#!/usr/bin/env python3
"""
Generate a test audio file for mel spectrogram comparison
"""
import numpy as np
import scipy.io.wavfile as wavfile
import os

def generate_test_audio():
    """Generate a test audio signal matching the Rust implementation exactly"""
    sample_rate = 16000
    duration = 2.0  # 2 seconds
    num_samples = int(sample_rate * duration)
    
    # Generate a test signal with multiple frequency components
    # Match the Rust implementation structure exactly
    signal = np.zeros(num_samples)
    
    # Start from sample 400 (like in Rust)
    for i in range(0, num_samples):
        t = i / sample_rate
        
        # Create a signal with multiple frequency components (same as Rust)
        sample = 0.0
        sample += 0.3 * np.sin(2.0 * np.pi * 220.0 * t)   # A3
        sample += 0.3 * np.sin(2.0 * np.pi * 440.0 * t)   # A4
        sample += 0.2 * np.sin(2.0 * np.pi * 880.0 * t)   # A5
        sample += 0.2 * np.sin(2.0 * np.pi * 1760.0 * t)  # A6
        
        # Add some deterministic "noise" (same as Rust implementation)
        sample += 0.05 * (np.sin(i * 0.001) - 0.5)
        
        signal[i] = sample * 0.8  # Scale to prevent clipping
    
    # Convert to 16-bit integers
    signal_int16 = (signal * 32767).astype(np.int16)
    
    return signal_int16, sample_rate

def main():
    output_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'test.wav')
    
    # Create temp directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print("Generating test audio file...")
    signal, sample_rate = generate_test_audio()
    
    # Save as WAV file
    wavfile.write(output_path, sample_rate, signal)
    
    print(f"Generated test audio file: {output_path}")
    print(f"Duration: {len(signal) / sample_rate:.2f} seconds")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Samples: {len(signal)}")
    print(f"Amplitude range: [{signal.min()}, {signal.max()}]")

if __name__ == "__main__":
    main()
