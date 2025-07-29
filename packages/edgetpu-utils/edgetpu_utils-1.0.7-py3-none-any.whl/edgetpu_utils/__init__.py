"""EdgeTPU utilities for model partitioning, benchmarking, and TensorFlow Lite operations."""

__version__ = "1.0.7"

# Import main functions for easy access
from .partition import partition_with_num_ops, partition_with_layer_idxs
from .tflite_utils import (
    get_num_ops,
    calculate_first_output_node_exe_idx,
    get_total_input_tran_size,
    calculate_parameter_sizes,
    change_param_caching_token,
    get_caching_token_binary,
    read_buf,
    save_buf,
)
from .benchmark import benchmark_model, benchmark_models
from .path_utils import get_segment_num, generate_segments_names

__all__ = [
    # Partitioning functions
    "partition_with_num_ops",
    "partition_with_layer_idxs",
    # TensorFlow Lite utilities
    "get_num_ops",
    "calculate_first_output_node_exe_idx",
    "get_total_input_tran_size",
    "calculate_parameter_sizes",
    "change_param_caching_token",
    "get_caching_token_binary",
    "read_buf",
    "save_buf",
    # Benchmarking functions
    "benchmark_model",
    "benchmark_models",
    # Path utilities
    "get_segment_num",
    "generate_segments_names",
]
