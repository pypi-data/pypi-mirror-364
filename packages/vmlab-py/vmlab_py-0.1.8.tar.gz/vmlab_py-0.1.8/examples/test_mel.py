#!/usr/bin/env python3
"""
Test script to generate mel spectrogram using Python implementation
"""
import sys
import os
import numpy as np
import torch

# # Add the py module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from audio_processor import AudioProcessor
from audio_utils import parse_audio_length, crop_pad_audio

def main():
    # Initialize audio processor with same parameters as Rust
    audio_processor = AudioProcessor(
        filter_length=800,
        hop_length=200,
        win_length=800,
        n_mel_channels=80,
        sampling_rate=16000,
        mel_fmin=55.0,
        mel_fmax=7600.0,
        mel_scale="slaney",
        mel_norm="slaney",
        mel_base='10',
    )
    
    # Read the test wav file
    wav_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'test.wav')
    
    if not os.path.exists(wav_path):
        print(f"Error: {wav_path} not found!")
        return
    
    print(f"Reading audio from: {wav_path}")
    sr, wav = audio_processor.read_wav(wav_path)
    print(f"Audio shape: {wav.shape}, Sample rate: {sr}")
    
    # Convert to mel spectrogram
    print(f"Original wav length: {len(wav)}")
    wav = np.concatenate([wav, np.zeros(sr)])
    print(f"After padding: {len(wav)}")
    wav_length, num_frames = parse_audio_length(len(wav), sr, 25)
    print(f"Parsed audio length: {wav_length}, num_frames: {num_frames}")
    wav = crop_pad_audio(wav, wav_length)
    print(f"After crop/pad: {len(wav)}")
    mel_spec = audio_processor.wav_to_melspec(wav, normalize=True)

    # mel_spec print 
    # print(mel_spec[:, 0:10])
    
    print(f"Mel spectrogram shape: {mel_spec.shape}")
    print(f"Mel spectrogram dtype: {mel_spec.dtype}")
    print(f"Mel spectrogram min: {mel_spec.min().item():.6f}")
    print(f"Mel spectrogram max: {mel_spec.max().item():.6f}")
    print(f"Mel spectrogram mean: {mel_spec.mean().item():.6f}")
    print(f"Mel spectrogram std: {mel_spec.std().item():.6f}")
    
    # Save to numpy file
    output_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'python_mel.npy')
    np.save(output_path, mel_spec.cpu().numpy())
    print(f"Saved Python mel spectrogram to: {output_path}")
    
    # Also save some debug info
    debug_info = {
        'shape': mel_spec.shape,
        'min': mel_spec.min().item(),
        'max': mel_spec.max().item(),
        'mean': mel_spec.mean().item(),
        'std': mel_spec.std().item(),
        'first_10_values': mel_spec[:10, 0].cpu().numpy().tolist(),
        'last_10_values': mel_spec[-10:, -1].cpu().numpy().tolist(),
    }
    
    debug_path = os.path.join(os.path.dirname(__file__), '..', 'temp', 'python_mel_debug.txt')
    with open(debug_path, 'w') as f:
        for key, value in debug_info.items():
            f.write(f"{key}: {value}\n")
    
    print(f"Saved debug info to: {debug_path}")

if __name__ == "__main__":
    main()
