"""
evlib: Event Camera Data Processing Library

A robust event camera processing library with Rust backend and Python bindings.

## Core Features

- **Universal Format Support**: Load data from H5, AEDAT, EVT2/3, AER, and text formats
- **Automatic Format Detection**: No need to specify format types manually
- **Polars DataFrame Support**: High-performance DataFrame operations
- **Stacked Histogram Representations**: Efficient event-to-representation conversion
- **Rust Performance**: Memory-safe, high-performance backend with Python bindings

## Quick Start

### Polars LazyFrames (High-Performance)
```python
import evlib
import polars as pl

# Load events as Polars LazyFrame
lf = evlib.load_events("path/to/your/data.h5")

# Fast filtering and analysis with Polars (lazy evaluation)
filtered = lf.filter(
    (pl.col("timestamp") > 0.1) &
    (pl.col("timestamp") < 0.2) &
    (pl.col("polarity") == 1)
)

# Or use high-level filtering functions
filtered = evlib.filter_by_time(lf, t_start=0.1, t_end=0.2)
filtered = evlib.filter_by_polarity(filtered, polarity=1)

# Complete preprocessing pipeline
processed = evlib.preprocess_events(
    "path/to/your/data.h5",
    t_start=0.1, t_end=0.5,
    roi=(100, 500, 100, 400),
    polarity=1,
    remove_hot_pixels=True,
    remove_noise=True
)

# Collect to DataFrame when needed
df = processed.collect()

# Direct access to Rust formats module if needed
# x, y, t, p = evlib.formats.load_events("path/to/your/data.h5")
```

### Direct Rust Access (Advanced)
```python
import evlib

# Direct access to Rust formats module (returns NumPy arrays)
x, y, t, p = evlib.formats.load_events("path/to/your/data.h5")

# Create stacked histogram representation
histogram = evlib.create_event_histogram(x, y, t, p, height=480, width=640)
```

### Event Filtering (New)
```python
import evlib

# Apply temporal and spatial filtering
filtered_events = evlib.filter_by_time("path/to/data.h5", t_start=0.1, t_end=1.0)
roi_events = evlib.filter_by_roi(filtered_events, x_min=100, x_max=500, y_min=100, y_max=400)

# Complete preprocessing pipeline
processed_events = evlib.preprocess_events(
    "path/to/data.h5",
    t_start=0.1, t_end=1.0,
    roi=(100, 500, 100, 400),
    polarity=1,
    remove_hot_pixels=True,
    remove_noise=True
)

# Use with representations
histogram = evlib.create_stacked_histogram(processed_events, height=480, width=640)
```

## Available Functions

### Data Loading Functions
- `load_events()`: Load events as Polars LazyFrame (main function)
- `formats.load_events()`: Direct Rust access returning NumPy arrays (advanced)
- `detect_format()`: Automatic format detection
- `save_events_to_hdf5()`: Save events in HDF5 format
- `save_events_to_text()`: Save events as text

### High-Performance Representation Functions
- `create_stacked_histogram()`: Create stacked histogram representations (Polars-based)
- `create_mixed_density_stack()`: Create mixed density event stacks (Polars-based)
- `create_voxel_grid()`: Create voxel grid representations (Polars-based)
- `preprocess_for_detection()`: High-level API for neural network preprocessing
- `benchmark_vs_rvt()`: Performance comparison with PyTorch approaches

### Event Filtering Functions
- `filter_by_time()`: Filter events by time range (start/end times)
- `filter_by_roi()`: Filter events by spatial region of interest
- `filter_by_polarity()`: Filter events by polarity (positive/negative)
- `filter_hot_pixels()`: Remove hot pixels using statistical detection
- `filter_noise()`: Apply noise filtering (refractory period, etc.)
- `preprocess_events()`: Complete preprocessing pipeline with all filters

"""

import os

# Import submodules (with graceful fallback)
try:
    from . import models  # noqa: F401

    _models_available = True
except ImportError:
    _models_available = False

try:
    from . import representations  # noqa: F401

    _representations_available = True

    # Import key representation functions directly
    from .representations import benchmark_vs_rvt  # noqa: F401
    from .representations import (
        create_mixed_density_stack,  # noqa: F401
        create_stacked_histogram,  # noqa: F401
        create_voxel_grid,  # noqa: F401
        preprocess_for_detection,  # noqa: F401
    )
except ImportError:
    _representations_available = False

# Import filtering module
try:
    from . import filtering  # noqa: F401

    _filtering_available = True

    # Import key filtering functions directly
    from .filtering import (  # noqa: F401
        filter_by_time,  # noqa: F401
        filter_by_roi,  # noqa: F401
        filter_by_polarity,  # noqa: F401
        filter_hot_pixels,  # noqa: F401
        filter_noise,  # noqa: F401
        preprocess_events,  # noqa: F401
    )
except ImportError:
    _filtering_available = False

# Import streaming utilities
try:
    from . import streaming_utils  # noqa: F401

    _streaming_utils_available = True
except ImportError:
    _streaming_utils_available = False

# Import filtering utilities
try:
    from . import filtering  # noqa: F401

    _filtering_available = True

    # Import key filtering functions directly
    from .filtering import (
        filter_by_time,  # noqa: F401
        filter_by_roi,  # noqa: F401
        filter_by_polarity,  # noqa: F401
        filter_hot_pixels,  # noqa: F401
        filter_noise,  # noqa: F401
        preprocess_events,  # noqa: F401
    )
except ImportError:
    _filtering_available = False

# Import high-performance Polars preprocessing (consolidated into representations module)
_representations_polars_available = False

# Configure Polars GPU acceleration if available
try:
    import polars as pl

    def _configure_polars_engine():
        """Configure Polars engine with GPU support and graceful fallback to streaming."""
        # Check if GPU is explicitly requested
        gpu_engine_requested = os.environ.get("POLARS_ENGINE_AFFINITY", "").lower() == "gpu"

        if gpu_engine_requested:
            try:
                # Try to set GPU engine if requested via environment variable
                pl.Config.set_engine_affinity("gpu")
                print("evlib: Polars GPU engine enabled via POLARS_ENGINE_AFFINITY environment variable")
                return "gpu"
            except Exception as e:
                print(f"evlib: Could not enable Polars GPU engine: {e}")
                print("evlib: Falling back to streaming engine")

        # Auto-detect and try GPU engine if available (only if not explicitly requested)
        if not gpu_engine_requested:
            # Only enable GPU mode for NVIDIA CUDA GPUs
            import subprocess

            try:
                # Check if nvidia-smi is available (indicates NVIDIA GPU)
                subprocess.run(["nvidia-smi"], capture_output=True, check=True)

                # Test if GPU operations work with Polars
                test_df = pl.DataFrame({"test": [1, 2, 3]})
                pl.Config.set_engine_affinity("gpu")
                _ = test_df.select(pl.col("test") * 2)
                print("evlib: NVIDIA GPU detected and enabled automatically")
                return "gpu"
            except (subprocess.CalledProcessError, FileNotFoundError, Exception):
                # NVIDIA GPU not available, set streaming engine
                pass

        # NVIDIA GPU not available, set streaming engine for optimal performance
        pl.Config.set_engine_affinity("streaming")
        print("evlib: Using streaming engine for optimal performance")
        return "streaming"

    # Configure the engine and store result
    _engine_type = _configure_polars_engine()
    _gpu_available = _engine_type == "gpu"

except ImportError:
    _gpu_available = False

# Import the compiled Rust extension module
# The .so file is the actual PyO3 module that contains all the functions and submodules
try:
    # Import the compiled Rust module

    # Check what submodules are available in the compiled module
    # The Rust code should have created 'core' and 'formats' submodules
    try:
        from .evlib import core, formats

        _core_available = True
        _formats_available = True

        # Make key functions directly accessible
        save_events_to_hdf5 = formats.save_events_to_hdf5
        save_events_to_text = formats.save_events_to_text
        detect_format = formats.detect_format
        get_format_description = formats.get_format_description
        _polars_available = True

    except ImportError:
        _core_available = False
        _formats_available = False
        _polars_available = False

except ImportError:
    _formats_available = False
    _core_available = False
    _polars_available = False
    _polars_utils_available = False

# Import version from Rust module
try:
    from .evlib import __version__
except ImportError:
    # Fallback to reading from Cargo.toml if Rust module not available
    import pathlib

    try:
        # Try tomllib first (Python 3.11+), then fallback to tomli or manual parsing
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                # Manual parsing fallback for Python 3.10
                import re

                _cargo_toml_path = pathlib.Path(__file__).parent.parent.parent / "Cargo.toml"
                with open(_cargo_toml_path, "r") as f:
                    content = f.read()
                version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
                if version_match:
                    __version__ = version_match.group(1)
                else:
                    __version__ = "unknown"
                raise ImportError  # Skip the tomllib parsing below

        _cargo_toml_path = pathlib.Path(__file__).parent.parent.parent / "Cargo.toml"
        with open(_cargo_toml_path, "rb") as f:
            _cargo_data = tomllib.load(f)
        __version__ = _cargo_data["package"]["version"]
    except (FileNotFoundError, KeyError, AttributeError):
        __version__ = "unknown"

# Export the available functionality
__all__ = ["__version__"]

if _models_available:
    __all__.append("models")
if _streaming_utils_available:
    __all__.append("streaming_utils")
if _filtering_available:
    __all__.extend(
        [
            "filtering",
            "filter_by_time",
            "filter_by_roi",
            "filter_by_polarity",
            "filter_hot_pixels",
            "filter_noise",
            "preprocess_events",
        ]
    )
if _representations_available:
    __all__.extend(
        [
            "representations",
            "create_stacked_histogram",
            "create_mixed_density_stack",
            "create_voxel_grid",
            "preprocess_for_detection",
            "benchmark_vs_rvt",
        ]
    )
if _filtering_available:
    __all__.extend(
        [
            "filtering",
            "filter_by_time",
            "filter_by_roi",
            "filter_by_polarity",
            "filter_hot_pixels",
            "filter_noise",
            "preprocess_events",
        ]
    )
if _formats_available:
    format_exports = [
        "formats",
        "load_events",
        "save_events_to_hdf5",
        "save_events_to_text",
        "detect_format",
        "get_format_description",
        "get_recommended_engine",
        "collect_with_optimal_engine",
    ]
    __all__.extend(format_exports)

if _core_available:
    __all__.append("core")


def get_recommended_engine():
    """
    Get the recommended Polars engine for evlib operations.

    Returns:
        str: 'gpu' if GPU is available, otherwise 'streaming' for large datasets
    """
    try:
        return _engine_type if _engine_type == "gpu" else "streaming"
    except NameError:
        return "streaming"  # Safe fallback for large event datasets


def collect_with_optimal_engine(lazy_frame):
    """
    Collect a Polars LazyFrame using the optimal engine for evlib operations.

    Args:
        lazy_frame: Polars LazyFrame to collect

    Returns:
        Polars DataFrame
    """
    engine = get_recommended_engine()
    return lazy_frame.collect(engine=engine)


# Main load_events function that returns a Polars LazyFrame
def load_events(path, **kwargs):
    """
    Load events as Polars LazyFrame.

    Args:
        path: Path to event file
        **kwargs: Additional arguments (t_start, t_end, min_x, max_x, min_y, max_y, polarity, sort, etc.)

    Returns:
        Polars LazyFrame with columns [x, y, timestamp, polarity]
        - timestamp is always converted to Duration type in microseconds

    Example:
        # For optimal performance with large datasets:
        events = evlib.load_events("data.h5")
        df = events.collect(engine=evlib.get_recommended_engine())

        # Or let evlib handle engine selection automatically:
        df = evlib.collect_with_optimal_engine(events)
    """
    if not _formats_available:
        raise ImportError("Formats module not available")

    # Use unified load_events function (now returns Polars data directly)
    data_dict = formats.load_events(path, **kwargs)

    # Convert the dictionary to Polars LazyFrame
    import polars as pl

    # Handle the duration column properly
    if "timestamp" in data_dict:
        df = pl.DataFrame(data_dict)
        # The timestamp is already converted to microseconds in Rust
        df = df.with_columns([pl.col("timestamp").cast(pl.Duration(time_unit="us"))])
        return df.lazy()
    else:
        # Empty case
        return pl.DataFrame(data_dict).lazy()
