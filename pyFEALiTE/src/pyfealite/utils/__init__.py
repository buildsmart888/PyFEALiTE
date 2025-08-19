"""
Utility functions and classes for PyFEALiTE.
"""

from .export import ExportManager, export_to_json, export_to_csv, export_to_dxf
from .combinations import standard_load_combinations

# Optional benchmarking (requires psutil)
try:
    from .benchmarks import PerformanceBenchmark, benchmark_analysis
    BENCHMARKS_AVAILABLE = True
    __all__ = [
        "ExportManager",
        "export_to_json", 
        "export_to_csv",
        "export_to_dxf",
        "PerformanceBenchmark",
        "benchmark_analysis", 
        "standard_load_combinations"
    ]
except ImportError:
    BENCHMARKS_AVAILABLE = False
    __all__ = [
        "ExportManager",
        "export_to_json", 
        "export_to_csv",
        "export_to_dxf",
        "standard_load_combinations"
    ]