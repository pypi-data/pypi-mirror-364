// Example Rust file showing how to use Audio2MelSpectrogramV2RT directly
// Note: This file demonstrates the usage but may need adjustments for imports
// depending on how you structure your crate modules.

use std::fs::File;
use std::io::Write;

use vmlab_py::audio::transforms::Audio2MelSpectrogramV2RT;
use vmlab_py::audio::utils::{norm_mean_std, MelParam};

// To compile this example, you would need to either:
// 1. Include this as a binary in your Cargo.toml:
//    [[bin]]
//    name = "test_mel_rust"
//    path = "examples/test_mel.rs"
//
// 2. Or adjust these imports to match your project structure
//    For example, if building as part of the main crate:
//    use vmlab_py_package::audio::transforms::Audio2MelSpectrogramV2RT;
//    use vmlab_py_package::audio::utils::{norm_mean_std, MelParam};

/*
// Uncomment these imports when building as part of the main crate:
use crate::audio::transforms::Audio2MelSpectrogramV2RT;
use crate::audio::utils::{norm_mean_std, MelParam};
*/

// For now, this is a demonstration file showing the structure

fn load_test_audio() -> Vec<f32> {
    println!("Loading test audio from temp/test.wav");

    // use std::fs::File;
    // use std::io::{BufReader, Read};
    //
    // // Simple WAV file reader
    // // Note: This is a basic implementation that assumes 16-bit PCM format
    // let file_path = "temp/test.wav";
    //
    // match File::open(file_path) {
    //     Ok(file) => {
    //         let mut reader = BufReader::new(file);
    //         let mut header = [0u8; 44]; // Standard WAV header is 44 bytes
    //
    //         if reader.read_exact(&mut header).is_err() {
    //             println!("Error reading WAV header, falling back to synthetic audio");
    //             return generate_synthetic_audio();
    //         }
    //
    //         // Basic WAV header validation
    //         if &header[0..4] != b"RIFF" || &header[8..12] != b"WAVE" {
    //             println!("Invalid WAV file format, falling back to synthetic audio");
    //             return generate_synthetic_audio();
    //         }
    //
    //         // Read audio data (assuming 16-bit PCM)
    //         let mut audio_data = Vec::new();
    //         let mut buffer = Vec::new();
    //
    //         if reader.read_to_end(&mut buffer).is_ok() {
    //             // Convert 16-bit PCM to f32
    //             for chunk in buffer.chunks_exact(2) {
    //                 let sample = i16::from_le_bytes([chunk[0], chunk[1]]) as f32 / 32768.0;
    //                 audio_data.push(sample);
    //             }
    //
    //             println!("Loaded {} samples from {}", audio_data.len(), file_path);
    //             audio_data
    //         } else {
    //             println!("Error reading WAV data, falling back to synthetic audio");
    //             generate_synthetic_audio()
    //         }
    //     }
    //     Err(_) => {
    //         println!(
    //             "Could not open {}, falling back to synthetic audio",
    //             file_path
    //         );
    //     }
    // }
            generate_synthetic_audio()
}

fn generate_synthetic_audio() -> Vec<f32> {
    println!("Generating synthetic test audio signal");

    let sample_rate = 16000;
    let duration = 2.0; // 2 seconds
    let num_samples = (sample_rate as f32 * duration) as usize;

    // Generate a test signal with multiple frequency components
    let mut audio_data = Vec::with_capacity(num_samples);

    for i in 0..num_samples {
        let t = i as f32 / sample_rate as f32;

        // Create a signal with multiple frequency components
        let mut sample = 0.0;
        sample += 0.3 * (2.0 * std::f32::consts::PI * 220.0 * t).sin(); // A3
        sample += 0.3 * (2.0 * std::f32::consts::PI * 440.0 * t).sin(); // A4
        sample += 0.2 * (2.0 * std::f32::consts::PI * 880.0 * t).sin(); // A5
        sample += 0.2 * (2.0 * std::f32::consts::PI * 1760.0 * t).sin(); // A6

        // Add some deterministic "noise"
        sample += 0.05 * ((i as f32 * 0.001).sin() - 0.5);

        audio_data.push(sample * 0.8); // Scale to prevent clipping
    }

    println!(
        "Generated {} samples at {}Hz",
        audio_data.len(),
        sample_rate
    );
    audio_data
}

// Simple function to save binary data
fn save_binary_data(
    data: &[f32],
    shape: (usize, usize),
    path: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    use std::io::BufWriter;

    let file = File::create(path)?;
    let mut writer = BufWriter::new(file);

    // Write magic number for identification
    writer.write_all(b"RUST")?;

    // Write shape
    writer.write_all(&(shape.0 as u32).to_le_bytes())?;
    writer.write_all(&(shape.1 as u32).to_le_bytes())?;

    // Write data
    for &value in data {
        writer.write_all(&value.to_le_bytes())?;
    }

    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Rust Audio2MelSpectrogramV2RT Example");
    println!("{}", "=".repeat(60));

    // Create temp directory if it doesn't exist
    std::fs::create_dir_all("../temp")?;

    // Load test audio data
    let mut audio_data = load_test_audio();
    println!("Audio data loaded: {} samples", audio_data.len());

    // Match Python preprocessing: add 1 second of zeros
    let sample_rate = 16000;
    let mut padding = vec![0.0; sample_rate];
    audio_data.append(&mut padding);
    println!("After padding: {} samples", audio_data.len());

    // Initialize Audio2MelSpectrogramV2RT with the same parameters as Python
    let mut transformer = Audio2MelSpectrogramV2RT::new(
        16000, // sample_rate
        800,   // fft_size
        200,   // hop_size
        1e-5,  // min_level (epsilon)
        1.0,   // compression_factor
        1.0,   // amplitude_to_db_factor
        0.0,   // ref_level_db
        MelParam {
            sr: 16000.0,
            n_fft: 800,
            n_mels: 80,
            f_min: Some(55.0),
            f_max: Some(7600.0),
            htk: false,
            norm: true,
        },
    );

    println!("Audio2MelSpectrogramV2RT initialized");

    // Option 1: Process entire audio at once (like Python)
    println!("Processing entire audio at once...");
    let result_full = transformer.transform(audio_data.clone(), |mel_spec| {
        norm_mean_std(mel_spec, -2.123307466506958, 1.0819180011749268)
    });

    if let Some((mel_array_full, frame_count_full, start_idx_full)) = result_full {
        println!(
            "Full audio result: shape {:?}, frames: {}, start_idx: {:?}",
            mel_array_full.shape(),
            frame_count_full,
            start_idx_full
        );

        // Extract the mel data and save it
        let mel_2d_full = mel_array_full.index_axis(ndarray::Axis(0), 0);
        let mel_2d_full = mel_2d_full.index_axis(ndarray::Axis(0), 0);

        // Save full processing result
        let data_full: Vec<f32> = mel_2d_full.iter().cloned().collect();
        let shape_full = mel_2d_full.shape();

        // Create a simple binary file (since we don't have proper npy support)
        let mut file = File::create("../temp/rust_mel_full.bin")?;
        file.write_all(b"RUST")?;
        file.write_all(&(shape_full[0] as u32).to_le_bytes())?;
        file.write_all(&(shape_full[1] as u32).to_le_bytes())?;
        for &value in &data_full {
            file.write_all(&value.to_le_bytes())?;
        }

        println!("Saved full audio mel spectrogram: shape {:?}", shape_full);

        // Clear transformer for streaming test
        transformer.clear();
    }

    // Option 2: Process audio in chunks (streaming fashion)
    println!("\nNow testing streaming processing...");
    // Use larger chunk size to match expected behavior - 200ms at 16kHz = 3200 samples
    let chunk_size = 800; // 200ms chunks at 16kHz
    let mut all_mel_outputs = Vec::new();
    let mut processed_chunks = 0;

    for (chunk_idx, chunk_start) in (0..audio_data.len()).step_by(chunk_size).enumerate() {
        let chunk_end = (chunk_start + chunk_size).min(audio_data.len());
        let mut chunk = audio_data[chunk_start..chunk_end].to_vec();

        // Pad the last chunk if necessary
        if chunk.len() < chunk_size {
            chunk.resize(chunk_size, 0.0);
        }

        println!(
            "Processing chunk {} ({} samples) chunkstart({chunk_start}), chunkend({chunk_end})",
            chunk_idx + 1,
            chunk.len()
        );

        // Transform the chunk using the normalization function
        let result = transformer.transform(chunk, |mel_spec| {
            norm_mean_std(mel_spec, -2.123307466506958, 1.0819180011749268)
        });

        if let Some((mel_array, frame_count, start_idx)) = result {
            println!(
                "  -> Got mel spectrogram: shape {:?}, frames: {}, start_idx: {:?}",
                mel_array.shape(),
                frame_count,
                start_idx
            );

            // Extract the mel data (shape is [1, 1, 80, time_frames])
            let mel_2d = mel_array.index_axis(ndarray::Axis(0), 0);

            all_mel_outputs.push(mel_2d.to_owned());
            processed_chunks += 1;
        } else {
            println!("  -> No output (accumulating data)");
        }
    }

    println!(
        "\nProcessed {} chunks, got {} mel outputs",
        (audio_data.len() + chunk_size - 1) / chunk_size,
        all_mel_outputs.len()
    );

    if !all_mel_outputs.is_empty() {
        // Concatenate all mel outputs
        let total_time_frames: usize = all_mel_outputs.iter().map(|m| m.shape()[2]).sum();
        let mut concatenated_mel = ndarray::Array3::<f32>::zeros((1, 80, total_time_frames));

        let mut time_offset = 0;
        for mel_output in &all_mel_outputs {
            let time_frames = mel_output.shape()[2];
            concatenated_mel
                .slice_mut(ndarray::s![0, .., time_offset..time_offset + time_frames])
                .assign(&mel_output.slice(ndarray::s![0, .., ..]));
            time_offset += time_frames;
        }

        println!(
            "Final mel spectrogram shape: {:?}",
            concatenated_mel.shape()
        );
        println!("Mel spectrogram statistics:");
        println!(
            "  Min: {:.6}",
            concatenated_mel
                .iter()
                .fold(f32::INFINITY, |a, &b| a.min(b))
        );
        println!(
            "  Max: {:.6}",
            concatenated_mel
                .iter()
                .fold(f32::NEG_INFINITY, |a, &b| a.max(b))
        );
        println!("  Mean: {:.6}", concatenated_mel.mean().unwrap());
        println!("  Std: {:.6}", concatenated_mel.std(0.0));

        // Convert to flat vector for saving
        let data: Vec<f32> = concatenated_mel.iter().cloned().collect();
        let shape = concatenated_mel.shape();

        // Save to file as binary data
        let output_path = "../temp/rust_mel.bin";
        save_binary_data(&data, (shape[1], shape[2]), output_path)?;
        println!("Saved Rust mel spectrogram to: {}", output_path);

        // Save debug information
        let debug_path = "../temp/rust_mel_debug.txt";
        let mut debug_file = File::create(debug_path)?;
        writeln!(debug_file, "shape: {:?}", concatenated_mel.shape())?;
        writeln!(
            debug_file,
            "min: {:.6}",
            concatenated_mel
                .iter()
                .fold(f32::INFINITY, |a, &b| a.min(b))
        )?;
        writeln!(
            debug_file,
            "max: {:.6}",
            concatenated_mel
                .iter()
                .fold(f32::NEG_INFINITY, |a, &b| a.max(b))
        )?;
        writeln!(debug_file, "mean: {:.6}", concatenated_mel.mean().unwrap())?;
        writeln!(debug_file, "std: {:.6}", concatenated_mel.std(0.0))?;
        writeln!(debug_file, "processed_chunks: {}", processed_chunks)?;
        writeln!(debug_file, "chunk_size: {}", chunk_size)?;
        writeln!(debug_file, "total_time_frames: {}", total_time_frames)?;

        // Save first and last 10 values for comparison
        let first_10: Vec<f32> = concatenated_mel.slice(ndarray::s![0, 0..10, 0]).to_vec();
        let last_col = concatenated_mel.shape()[2] - 1;
        let last_10: Vec<f32> = concatenated_mel
            .slice(ndarray::s![0, 70..80, last_col])
            .to_vec();

        writeln!(debug_file, "first_10_values: {:?}", first_10)?;
        writeln!(debug_file, "last_10_values: {:?}", last_10)?;

        println!("Saved debug info to: {}", debug_path);

        println!("Rust mel spectrogram test completed successfully!");
    } else {
        println!("No mel spectrogram data was generated!");
    }

    println!("This is a template for using Audio2MelSpectrogramV2RT directly in Rust.");
    println!("To use this example:");
    println!("1. Uncomment the imports at the top");
    println!("2. Uncomment the main implementation");
    println!("3. Make sure the module structure matches your project");
    println!("4. Add this as a binary target in Cargo.toml if needed");
    println!();
    println!("The implementation above shows how to:");
    println!("- Initialize Audio2MelSpectrogramV2RT with proper parameters");
    println!("- Process audio in streaming chunks");
    println!("- Apply normalization using norm_mean_std");
    println!("- Concatenate results from multiple chunks");
    println!("- Save results for comparison with Python implementation");

    // Create a placeholder file
    std::fs::create_dir_all("../temp")?;
    let placeholder_path = "../temp/rust_example_info.txt";
    let mut file = File::create(placeholder_path)?;
    writeln!(file, "Rust Audio2MelSpectrogramV2RT Example")?;
    writeln!(
        file,
        "This file shows the structure for using the Rust implementation directly."
    )?;
    writeln!(
        file,
        "See test_mel.rs for the complete implementation template."
    )?;
    println!("Created info file: {}", placeholder_path);

    Ok(())
}
