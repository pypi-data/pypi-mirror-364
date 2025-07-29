# EEG Analysis Pipeline

A comprehensive Python package for EEG signal processing, trigger detection, and frequency-domain analysis.

## Overview

This package provides a complete pipeline for analyzing EEG data stored in European Data Format (EDF) files. It includes tools for signal loading, trigger detection, inter-trigger window analysis, and multi-band frequency-domain processing.

## Features

- **EDF File Loading**: Load and inspect EEG signals with flexible duration and channel selection
- **Trigger Detection**: Automated detection of trigger events with customizable thresholds
- **Window Analysis**: Generate and analyze inter-trigger intervals with multiple aggregation methods
- **Frequency-Domain Analysis**: Multi-band EEG analysis (Delta, Theta, Alpha, Beta, Gamma)
- **Visualization**: Comprehensive plotting and video generation capabilities
- **ML Integration**: Optional machine learning-based window quality filtering

## Installation

```bash
pip install yousif-raiyan-pip-package
```

## Quick Start

```python
from yousif_raiyan_pip_package import EDFLoader, TriggerDetector, Analyzer, EEGGraphProcessor

# Load EEG data
loader = EDFLoader("data", "subject_name")
loader.load_and_plot_signals(signal_indices=[15, 25], duration=1200.0)  # T6, T2

# Option 1: Spectral analysis
detector = TriggerDetector(loader, 'T2')
detector.detect_triggers()

analyzer = Analyzer(loader, detector)
analyzer.extract_signals()

# Option 2: Graph-based connectivity analysis
processor = EEGGraphProcessor(edf_loader=loader)

# Compute time-varying correlation
processor.compute_correlation(start_time=0, stop_time=300, interval_seconds=10)

# Compute coherence across frequency bands
processor.compute_coherence_bands(start_time=0, stop_time=300, interval_seconds=10)

# Generate full graph representations for machine learning
processor.generate_graphs_from_edf()
```

## Data Structure Requirements

### Input Data Format

Your EDF files should be organized as follows:

```
data/
└── subject_name/
    └── subject_name.edf
```

**Example:**
```
data/
└── Sebastian/
    └── Sebastian.edf
```

### EDF File Requirements

- **Format**: European Data Format (.edf)
- **Channels**: Standard EEG channel names (Fp1, F3, F4, C3, C4, P3, P4, O1, O2, F7, F8, T3, T4, T5, T6, Fz)
- **Sample Rate**: Typically 500 Hz (automatically detected)
- **Duration**: Minimum 10 minutes recommended for trigger detection

## Classes and Methods

### EDFLoader

Handles loading and inspection of EDF files.

#### Initialization
```python
loader = EDFLoader(folder_path, name)
```

**Parameters:**
- `folder_path` (str): Base directory containing subject folders
- `name` (str): Subject name (must match folder and file name)

#### Methods

##### `inspect_data()`
Displays comprehensive file information including:
- File header details
- Number of signals and their properties
- Sample rates and signal ranges
- First 10 samples of each channel

```python
loader.inspect_data()
```

##### `load_and_plot_signals(signal_indices=None, duration=None, save_plots=False, save_path=None)`
Loads and visualizes EEG signals with flexible options.

**Parameters:**
- `signal_indices` (list, optional): Specific channel indices to load (default: all channels)
- `duration` (float, optional): Duration in seconds to load (default: entire file)
- `save_plots` (bool): Save plots instead of displaying (default: False)
- `save_path` (str, optional): Custom save directory (default: `plots/{subject_name}`)

**Examples:**
```python
# Load T6 and T2 channels for 20 minutes
loader.load_and_plot_signals(signal_indices=[15, 25], duration=1200.0)

# Load all channels and save plots
loader.load_and_plot_signals(save_plots=True)

# Load specific duration with custom save path
loader.load_and_plot_signals(duration=1200.0, save_plots=True, save_path="custom_plots")
```

**Output:**
- Time-series plots with time axis in seconds
- Saved to `plots/{subject_name}/signals_plot.png` (if save_plots=True)

### TriggerDetector

Detects triggers and analyzes inter-trigger windows.

#### Initialization
```python
detector = TriggerDetector(edf_loader, signal_choice)
```

**Parameters:**
- `edf_loader` (EDFLoader): Initialized EDFLoader instance
- `signal_choice` (str): Channel name for trigger detection (e.g., 'T2', 'O1')

#### Methods

##### `detect_triggers()`
Detects trigger events using amplitude thresholding.

**Algorithm:**
1. Rectifies and filters the signal (Butterworth low-pass, 30 Hz cutoff)
2. Applies amplitude threshold (60 µV)
3. Filters events by duration (52-65 seconds)

```python
detector.detect_triggers()
print(f"Found {len(detector.df_triggers)} triggers")
```

**Output:**
- `df_triggers` DataFrame with columns:
  - `start_index`, `end_index`: Sample indices
  - `start_time (s)`, `end_time (s)`: Time in seconds
  - `duration_time (s)`: Trigger duration

##### `plot_triggers()`
Visualizes detected triggers overlaid on the filtered signal.

```python
detector.plot_triggers()
```

##### `save_triggers()`
Saves trigger information to CSV file.

```python
detector.save_triggers()
```

**Output:** `{subject_folder}/triggers.csv`

##### `plot_windows()`
Generates individual plots for each inter-trigger window.

```python
detector.plot_windows()
```

**Output:** `{subject_folder}/window plots/plot_{i}.png`

##### `convert_to_video()`
Creates MP4 video from window plots for rapid review.

```python
detector.convert_to_video()
```

**Output:** `{subject_folder}/trigger.mp4`

##### `filter_bad_windows(clf_path=None, classes_path=None)`
ML-based filtering of poor-quality windows using ResNet-50 + logistic regression.

```python
# Use built-in models (recommended)
detector.filter_bad_windows()

# Or use custom models
detector.filter_bad_windows(
    clf_path="path/to/custom_classifier.pkl",
    classes_path="path/to/custom_classes.npy"
)
```

**Parameters:**
- `clf_path` (str, optional): Path to custom classifier (.pkl file). Uses built-in model if None.
- `classes_path` (str, optional): Path to custom class labels (.npy file). Uses built-in model if None.

### Analyzer

Performs frequency-domain analysis of inter-trigger windows.

#### Initialization
```python
analyzer = Analyzer(loader, trigger_detector, target_length=50)
```

**Parameters:**
- `loader` (EDFLoader): Initialized EDFLoader instance
- `trigger_detector` (TriggerDetector): Initialized TriggerDetector instance
- `target_length` (int): Resampled points per segment for aggregation

#### Methods

##### `plot_signal_window(window_index, lead)`
Plots raw signal for a specific inter-trigger window.

```python
analyzer.plot_signal_window(window_index=0, lead='T2')
```

##### `plot_average_window(channel, start_window=None, end_window=None, target_length=500, aggregation_method='mean', trim_ratio=0.1)`
Aggregates and plots multiple windows using various statistical methods.

**Parameters:**
- `channel` (str): Channel name to analyze
- `start_window`, `end_window` (int, optional): Window range
- `target_length` (int): Resampling length
- `aggregation_method` (str): 'mean', 'median', or 'trimmed'
- `trim_ratio` (float): Trimming ratio for 'trimmed' method

**Examples:**
```python
# Mean aggregation
analyzer.plot_average_window('T6', aggregation_method='mean')

# Robust median aggregation
analyzer.plot_average_window('T6', aggregation_method='median')

# Trimmed mean (removes 10% outliers)
analyzer.plot_average_window('T6', aggregation_method='trimmed', trim_ratio=0.1)
```

##### `extract_signals(channels_to_extract=None)`
Comprehensive frequency-domain analysis across all EEG bands.

**Parameters:**
- `channels_to_extract` (list, optional): Specific channels to process (default: all loaded)

**Processing Pipeline:**
1. **Band-pass filtering** for each EEG band:
   - Delta (0.5-4 Hz)
   - Theta (4-8 Hz)  
   - Alpha (8-12 Hz)
   - Beta (12-30 Hz)
   - Gamma (30-80 Hz)

2. **Signal rectification** (absolute value for power estimation)

3. **Moving-average smoothing** with multiple window sizes:
   - 100 ms, 250 ms, 500 ms

4. **Median aggregation** across all windows for robustness

**Examples:**
```python
# Process all loaded channels
analyzer.extract_signals()

# Process specific channels only
analyzer.extract_signals(['T2', 'T6', 'O1'])
```

### EEGGraphProcessor

Converts EEG data to graph representations for network analysis and computes time-varying connectivity measures.

#### Initialization
```python
processor = EEGGraphProcessor(
    edf_loader=loader,
    output_dir="graph_output",  # Optional: custom output directory
    window_size=1000,           # Optional: analysis window size in samples
    adj_window_size=20000,      # Optional: adjacency matrix window size
    window_step_ratio=0.125     # Optional: window overlap ratio
)
```

#### Methods

##### `generate_graphs_from_edf()`
Creates comprehensive graph representations with adjacency matrices and node/edge features.

**Features Generated:**
- **Adjacency matrices**: Correlation, coherence, phase relationships
- **Node features**: Energy, band-specific energy across frequency bands
- **Edge features**: Connectivity measures across frequency bands
- **Memory efficient**: Streams directly from EDF files

```python
processor.generate_graphs_from_edf()
# Output: {filename}.pickle with graph representations
```

##### `compute_correlation(start_time, stop_time, interval_seconds, overlap_ratio=0.0)`
Computes time-varying correlation matrices over specified time segments.

**Parameters:**
- `start_time` (float): Start time in seconds
- `stop_time` (float): End time in seconds  
- `interval_seconds` (float): Window duration for each correlation matrix
- `overlap_ratio` (float): Overlap between windows (0.0 = no overlap, 0.5 = 50% overlap)

```python
# Compute correlation every 5 seconds from 10-60s with 50% overlap
path = processor.compute_correlation(
    start_time=10.0,
    stop_time=60.0, 
    interval_seconds=5.0,
    overlap_ratio=0.5
)
```

**Output:** `{filename}_{start}s-{stop}s_correlation.pickle` containing:
```python
{
    "starts": [10.0, 12.5, 15.0, ...],  # Window start times
    "corr_matrices": [matrix1, matrix2, ...]  # Correlation matrices
}
```

##### `compute_coherence_average(start_time, stop_time, interval_seconds, overlap_ratio=0.0)`
Computes time-varying coherence matrices averaged across all frequency bands.

```python
# Simple averaged coherence analysis
path = processor.compute_coherence_average(
    start_time=10.0,
    stop_time=60.0,
    interval_seconds=5.0
)
```

**Output:** `{filename}_{start}s-{stop}s_coherence_avg.pickle` containing:
```python
{
    "starts": [10.0, 15.0, 20.0, ...],
    "coherence_matrices": [matrix1, matrix2, ...]  # Averaged coherence
}
```

##### `compute_coherence_bands(start_time, stop_time, interval_seconds, overlap_ratio=0.0)`
Computes detailed frequency-specific coherence analysis across EEG bands.

```python
# Detailed frequency-band coherence analysis  
path = processor.compute_coherence_bands(
    start_time=10.0,
    stop_time=60.0,
    interval_seconds=5.0,
    overlap_ratio=0.25
)
```

**Output:** `{filename}_{start}s-{stop}s_coherence_bands.pickle` containing:
```python
{
    "starts": [10.0, 15.0, 20.0, ...],
    "coherence_by_band": {
        "delta": [matrix1, matrix2, ...],    # 1-4 Hz
        "theta": [matrix1, matrix2, ...],    # 4-8 Hz  
        "alpha": [matrix1, matrix2, ...],    # 8-13 Hz
        "beta": [matrix1, matrix2, ...],     # 13-30 Hz
        "gamma": [matrix1, matrix2, ...],    # 30-70 Hz
        "gammaHi": [matrix1, matrix2, ...],  # 70-100 Hz
        # Additional bands based on sampling frequency
    },
    "frequency_bands": {
        "delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), ...
    }
}
```

#### Graph Analysis Workflow

```python
from yousif_raiyan_pip_package import EDFLoader, EEGGraphProcessor

# Load EEG data
loader = EDFLoader("data", "subject_name")
loader.load_and_plot_signals(duration=1200.0)

# Initialize graph processor
processor = EEGGraphProcessor(edf_loader=loader)

# Option 1: Full graph representation (for GNN analysis)
processor.generate_graphs_from_edf()

# Option 2: Time-varying connectivity analysis
# Simple correlation over time
corr_path = processor.compute_correlation(
    start_time=0, stop_time=300, interval_seconds=10
)

# Average coherence analysis
coh_avg_path = processor.compute_coherence_average(
    start_time=0, stop_time=300, interval_seconds=10
)

# Detailed frequency-band coherence
coh_bands_path = processor.compute_coherence_bands(
    start_time=0, stop_time=300, interval_seconds=10, overlap_ratio=0.5
)

# Load and analyze results
import pickle
with open(coh_bands_path, 'rb') as f:
    coherence_data = pickle.load(f)
    
# Access specific frequency band
alpha_coherence = coherence_data['coherence_by_band']['alpha']
time_points = coherence_data['starts']
```

## Output Structure

The package creates organized output directories:

```
data/
└── subject_name/
    ├── subject_name.edf                    # Input EDF file
    ├── triggers.csv                        # Detected triggers
    ├── window plots/                       # Inter-trigger window plots
    │   ├── plot_0.png
    │   ├── plot_1.png
    │   └── ...
    ├── trigger.mp4                         # Video compilation
    ├── Delta/                              # Frequency band results
    │   ├── csv/
    │   │   ├── T2_Delta_ma100ms_median.csv
    │   │   └── ...
    │   └── plots/
    │       ├── T2_Delta_ma_plot.png
    │       └── ...
    ├── Theta/
    ├── Alpha/
    ├── Beta/
    └── Gamma/
```

## Complete Workflow Example

```python
from yousif_raiyan_pip_package import EDFLoader, TriggerDetector, Analyzer

# Step 1: Load EEG data
loader = EDFLoader("data", "Sebastian")
loader.inspect_data()  # Review file structure

# Load temporal channels for analysis
loader.load_and_plot_signals(
    signal_indices=[15, 25],  # T6, T2 channels
    duration=1200.0,          # 20 minutes
    save_plots=True
)

# Step 2: Detect triggers
detector = TriggerDetector(loader, 'T2')
detector.detect_triggers()
print(f"Found {len(detector.df_triggers)} triggers")

# Visualize and save results
detector.plot_triggers()
detector.save_triggers()
detector.plot_windows()
detector.convert_to_video()

# Step 3: Frequency-domain analysis
analyzer = Analyzer(loader, detector, target_length=50)

# Test different aggregation methods
analyzer.plot_average_window('T2', aggregation_method='mean')
analyzer.plot_average_window('T2', aggregation_method='median')
analyzer.plot_average_window('T2', aggregation_method='trimmed', trim_ratio=0.1)

# Full multi-band analysis
analyzer.extract_signals(['T6', 'T2'])  # Process specific channels
```

## Advanced Usage

### Custom Trigger Detection Parameters

The trigger detection uses hardcoded parameters optimized for trigger detection:
- **Threshold**: 60 µV
- **Duration range**: 52-65 seconds
- **Filter**: 30 Hz low-pass Butterworth

### Memory Management

For large EDF files:
- Use `duration` parameter to limit data loading
- Use `signal_indices` to select specific channels
- Enable `save_plots=True` to avoid memory issues with display

### ML-Based Quality Control

For automated window quality assessment:
1. Train a ResNet-50 + logistic regression model on labeled window images
2. Save the classifier and class labels
3. Use `filter_bad_windows()` to automatically remove poor-quality segments

## Dependencies

- numpy
- scipy  
- mne
- pyedflib
- matplotlib
- pandas
- opencv-python
- torch
- torchvision
- joblib
- scikit-learn
- Pillow

## Requirements

- Python ≥ 3.7
- Sufficient RAM for EEG data (recommend 8GB+ for large files)
- GPU optional (for ML-based filtering)

## Citation

If you use this package in your research, please cite:

```
[Your citation information here]
```

## License

MIT License

## Support

For questions or issues, please contact the package maintainer.