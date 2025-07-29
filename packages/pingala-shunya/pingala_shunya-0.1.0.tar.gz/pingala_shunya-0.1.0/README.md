# Pingala Shunya

A comprehensive speech transcription package by **Shunya Labs** supporting **ct2 (CTranslate2)** and **transformers** backends. Get superior transcription quality with unified API and advanced features.

## Overview

Pingala Shunya provides a unified interface for transcribing audio files using state-of-the-art backends optimized by Shunya Labs. Whether you want the high-performance CTranslate2 optimization or the flexibility of Hugging Face transformers, Pingala Shunya delivers exceptional results with the `shunyalabs/pingala-v1-en-verbatim` model.

## Features

- **Shunya Labs Optimized**: Built by Shunya Labs for superior performance
- **CT2 Backend**: High-performance CTranslate2 optimization (default)
- **Transformers Backend**: Hugging Face models and latest research
- **Auto-Detection**: Automatically selects the best backend for your model
- **Unified API**: Same interface across all backends
- **Word-Level Timestamps**: Precise timing for individual words
- **Confidence Scores**: Quality metrics for transcription segments and words
- **Voice Activity Detection (VAD)**: Filter out silence and background noise
- **Language Detection**: Automatic language identification
- **Multiple Output Formats**: Text, SRT subtitles, and WebVTT
- **Streaming Support**: Process segments as they are generated
- **Advanced Parameters**: Full control over all backend features
- **Rich CLI**: Command-line tool with comprehensive options
- **Error Handling**: Comprehensive error handling and validation

## Installation

### Basic Installation (ct2 backend)
```bash
pip install pingala-shunya
```

### Backend-Specific Installations

```bash
# For Hugging Face transformers support
pip install "pingala-shunya[transformers]"

# For all backends
pip install "pingala-shunya[all]"

# Complete installation with development tools
pip install "pingala-shunya[complete]"
```

### Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for optimal performance)
- PyTorch and torchaudio

## Supported Backends

### ct2 (CTranslate2) - Default
- **Performance**: Fastest inference with CTranslate2 optimization
- **Features**: Full parameter control, VAD, streaming, GPU acceleration
- **Models**: All compatible models, optimized for Shunya Labs models
- **Best for**: Production use, real-time applications

### transformers  
- **Performance**: Good performance with Hugging Face ecosystem
- **Features**: Access to latest models, easy fine-tuning integration
- **Models**: Any Seq2Seq model on Hugging Face Hub
- **Best for**: Research, latest models, custom transformer models

## Supported Models

### Default Model
- `shunyalabs/pingala-v1-en-verbatim` - High-quality English transcription model by Shunya Labs

### Shunya Labs Models
- `shunyalabs/pingala-v1-en-verbatim` - Optimized for English verbatim transcription
- More Shunya Labs models coming soon!

### Custom Models (Advanced Users)
- Any Hugging Face Seq2Seq model compatible with automatic-speech-recognition pipeline
- Local model paths supported

### Local Models
- `/path/to/local/model` - Local model directory or file

## Quick Start

### Basic Usage with Auto-Detection

```python
from pingala_shunya import PingalaTranscriber

# Initialize with default Shunya Labs model and auto-detected backend
transcriber = PingalaTranscriber()

# Simple transcription
segments = transcriber.transcribe_file_simple("audio.wav")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

### Backend Selection

```python
from pingala_shunya import PingalaTranscriber

# Explicitly choose backends with Shunya Labs model
transcriber_ct2 = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="ct2")
transcriber_tf = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="transformers")  

# Auto-detection (recommended)
transcriber_auto = PingalaTranscriber()  # Uses default Shunya Labs model with ct2
```

### Advanced Usage with All Features

```python
from pingala_shunya import PingalaTranscriber

# Initialize with specific backend and settings
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim",
    backend="ct2",
    device="cuda", 
    compute_type="float16"
)

# Advanced transcription with full metadata
segments, info = transcriber.transcribe_file(
    "audio.wav",
    beam_size=10,                    # Higher beam size for better accuracy
    word_timestamps=True,            # Enable word-level timestamps
    temperature=0.0,                 # Deterministic output
    compression_ratio_threshold=2.4, # Filter out low-quality segments
    log_prob_threshold=-1.0,         # Filter by probability
    no_speech_threshold=0.6,         # Silence detection threshold
    initial_prompt="High quality audio recording",  # Guide the model
    hotwords="Python, machine learning, AI",        # Boost specific words
    vad_filter=True,                 # Enable voice activity detection
    task="transcribe"                # or "translate" for translation
)

# Print transcription info
model_info = transcriber.get_model_info()
print(f"Backend: {model_info['backend']}")
print(f"Model: {model_info['model_name']}")
print(f"Language: {info.language} (confidence: {info.language_probability:.3f})")
print(f"Duration: {info.duration:.2f} seconds")

# Process segments with all metadata
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    if segment.confidence:
        print(f"Confidence: {segment.confidence:.3f}")
    
    # Word-level details
    for word in segment.words:
        print(f"  '{word.word}' [{word.start:.2f}-{word.end:.2f}s] (conf: {word.probability:.3f})")
```

### Using Transformers Backend

```python
# Use Shunya Labs model with transformers backend
transcriber = PingalaTranscriber(
    model_name="shunyalabs/pingala-v1-en-verbatim",
    backend="transformers"
)

segments = transcriber.transcribe_file_simple("audio.wav")

# Auto-detection will use ct2 by default for Shunya Labs models
transcriber = PingalaTranscriber()  # Uses ct2 backend (recommended)
```

## Command-Line Interface

The package includes a comprehensive CLI supporting both backends:

### Basic CLI Usage

```bash
# Basic transcription with auto-detected backend
pingala audio.wav

# Specify backend explicitly  
pingala audio.wav --backend ct2
pingala audio.wav --backend transformers

# Use Shunya Labs model with different backends
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend ct2
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend transformers

# Save to file
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim -o transcript.txt

# Use CPU for processing
pingala audio.wav --device cpu
```

### Advanced CLI Features

```bash
# Word-level timestamps with confidence scores (ct2)
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --word-timestamps --show-confidence --show-words

# Voice Activity Detection (ct2 only)
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --vad --verbose

# Language detection with different backends
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --detect-language --backend ct2

# SRT subtitles with word-level timing
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --format srt --word-timestamps -o subtitles.srt

# Transformers backend with Shunya Labs model
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim --backend transformers --verbose

# Advanced parameters (ct2)
pingala audio.wav --model shunyalabs/pingala-v1-en-verbatim \
  --beam-size 10 \
  --temperature 0.2 \
  --compression-ratio-threshold 2.4 \
  --log-prob-threshold -1.0 \
  --initial-prompt "This is a technical presentation" \
  --hotwords "Python,AI,machine learning"
```

### CLI Options Reference

| Option | Description | Backends | Default |
|--------|-------------|----------|---------|
| `--model` | Model name or path | All | shunyalabs/pingala-v1-en-verbatim |
| `--backend` | Backend selection | All | auto-detect |
| `--device` | Device: cuda, cpu, auto | All | cuda |
| `--compute-type` | Precision: float16, float32, int8 | All | float16 |
| `--beam-size` | Beam size for decoding | All | 5 |
| `--language` | Language code (e.g., 'en') | All | auto-detect |
| `--word-timestamps` | Enable word-level timestamps | ct2 | False |
| `--show-confidence` | Show confidence scores | All | False |
| `--show-words` | Show word-level details | All | False |
| `--vad` | Enable VAD filtering | ct2 | False |
| `--detect-language` | Language detection only | All | False |
| `--format` | Output format: text, srt, vtt | All | text |
| `--temperature` | Sampling temperature | All | 0.0 |
| `--compression-ratio-threshold` | Compression ratio filter | ct2 | 2.4 |
| `--log-prob-threshold` | Log probability filter | ct2 | -1.0 |
| `--no-speech-threshold` | No speech threshold | All | 0.6 |
| `--initial-prompt` | Initial prompt text | All | None |
| `--hotwords` | Hotwords to boost | ct2 | None |
| `--task` | Task: transcribe, translate | All | transcribe |

## Backend Comparison

| Feature | ct2 | transformers |
|---------|-----|--------------|
| **Performance** | Fastest | Good |
| **GPU Acceleration** | Optimized | Standard |
| **Memory Usage** | Lowest | Moderate |
| **Model Support** | Any model | Any HF model |
| **Word Timestamps** | Full support | Limited |
| **VAD Filtering** | Built-in | No |
| **Streaming** | True streaming | Batch only |
| **Advanced Params** | All features | Basic |
| **Latest Models** | Updated | Latest |
| **Custom Models** | CTranslate2 | Any format |

### Recommendations

- **Production/Performance**: Use `ct2` with Shunya Labs models
- **Latest Research Models**: Use `transformers`
- **Real-time Applications**: Use `ct2` with VAD
- **Custom Transformer Models**: Use `transformers`

## Performance Optimization

### Backend Selection Tips

```python
# Real-time/Production: Use ct2 with Shunya Labs model
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="ct2")

# Maximum accuracy: Use Shunya Labs model with ct2  
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="ct2")

# Alternative backend: Use transformers with Shunya Labs model
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="transformers")

# Research/Latest models: Use transformers backend
transcriber = PingalaTranscriber(model_name="shunyalabs/pingala-v1-en-verbatim", backend="transformers")
```

### Hardware Recommendations

| Use Case | Model | Backend | Hardware |
|----------|-------|---------|----------|
| Real-time | shunyalabs/pingala-v1-en-verbatim | ct2 | GPU 4GB+ |
| Production | shunyalabs/pingala-v1-en-verbatim | ct2 | GPU 6GB+ |
| Maximum Quality | shunyalabs/pingala-v1-en-verbatim | ct2 | GPU 8GB+ |
| Alternative | shunyalabs/pingala-v1-en-verbatim | transformers | GPU 4GB+ |
| CPU-only | shunyalabs/pingala-v1-en-verbatim | any | 8GB+ RAM |

## Examples

See `example.py` for comprehensive examples:

```bash
# Run with default backend (auto-detected)
python example.py audio.wav

# Test specific backends with Shunya Labs model
python example.py audio.wav --backend ct2
python example.py audio.wav --backend transformers  

# Test Shunya Labs model with different backends
python example.py audio.wav shunyalabs/pingala-v1-en-verbatim
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built by [Shunya Labs](https://shunyalabs.ai) for superior transcription quality
- Powered by CTranslate2 for optimized inference
- Supports [Hugging Face transformers](https://github.com/huggingface/transformers) 
- Uses the Pingala model from [Shunya Labs](https://shunyalabs.ai)

## About Shunya Labs

Visit [Shunya Labs](https://shunyalabs.ai) to learn more about our AI research and products. 
Contact us at [0@shunyalabs.ai](mailto:0@shunyalabs.ai) for questions or collaboration opportunities. 