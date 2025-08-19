"""Performance benchmarking utilities for PyFEALiTE."""

import time
import numpy as np
import psutil
import platform
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import json

from ..core.structure import Structure
from ..core.node import Node2D, NodalDegreeOfFreedom
from ..core.element import FrameElement2D
from ..materials.isotropic import IsotropicMaterial
from ..sections.rectangular import RectangularSection
from ..loads.base import LoadCase, LoadType
from ..loads.point_load import PointLoad


@dataclass
class BenchmarkResult:
    """Results from a single benchmark test."""
    test_name: str
    n_nodes: int
    n_elements: int
    n_dofs: int
    assembly_time: float  # seconds
    solve_time: float     # seconds
    total_time: float     # seconds
    memory_usage: float   # MB
    peak_memory: float    # MB
    system_info: Dict[str, str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export."""
        return {
            "test_name": self.test_name,
            "n_nodes": self.n_nodes,
            "n_elements": self.n_elements,
            "n_dofs": self.n_dofs,
            "assembly_time": self.assembly_time,
            "solve_time": self.solve_time,
            "total_time": self.total_time,
            "memory_usage": self.memory_usage,
            "peak_memory": self.peak_memory,
            "system_info": self.system_info
        }


class PerformanceBenchmark:
    """Performance benchmarking class for PyFEALiTE."""
    
    def __init__(self):
        """Initialize benchmarking utilities."""
        self.results: List[BenchmarkResult] = []
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for benchmarks."""
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": str(psutil.cpu_count()),
            "memory_total_gb": f"{psutil.virtual_memory().total / 1e9:.2f}",
            "numpy_version": np.__version__
        }
    
    def benchmark_structure(self, structure: Structure, test_name: str = "", 
                          warmup_runs: int = 1) -> BenchmarkResult:
        """
        Benchmark analysis performance for a structure.
        
        Args:
            structure: Structure to benchmark
            test_name: Name for this benchmark test
            warmup_runs: Number of warmup runs before timing
            
        Returns:
            Benchmark results
        """
        if not test_name:
            test_name = f"Structure_{structure.n_nodes}nodes_{structure.n_elements}elements"
        
        print(f"Benchmarking: {test_name}")
        print(f"  Structure: {structure.n_nodes} nodes, {structure.n_elements} elements")
        
        # Warmup runs
        for _ in range(warmup_runs):
            try:
                structure.solve()
            except Exception as e:
                print(f"  Warmup failed: {e}")
                break
        
        # Memory monitoring
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1e6  # MB
        peak_memory = initial_memory
        
        # Timing the analysis
        start_time = time.time()
        
        # Time assembly (approximate by checking matrix creation)
        assembly_start = time.time()
        n_free_dofs = structure._assign_dof_numbers()
        structure._global_stiffness_matrix = structure._assemble_global_stiffness_matrix(n_free_dofs)
        assembly_time = time.time() - assembly_start
        
        # Monitor memory during assembly
        current_memory = process.memory_info().rss / 1e6
        peak_memory = max(peak_memory, current_memory)
        
        # Time solving
        solve_start = time.time()
        for load_case in structure.load_cases:
            F_global = structure._assemble_load_vector(load_case, n_free_dofs)
            if not np.allclose(F_global, 0):
                from scipy.sparse.linalg import spsolve
                displacements = spsolve(structure._global_stiffness_matrix, F_global)
                structure._displacements[load_case] = displacements
        solve_time = time.time() - solve_start
        
        total_time = time.time() - start_time
        
        # Final memory check
        final_memory = process.memory_info().rss / 1e6
        peak_memory = max(peak_memory, final_memory)
        
        result = BenchmarkResult(
            test_name=test_name,
            n_nodes=structure.n_nodes,
            n_elements=structure.n_elements,
            n_dofs=structure.n_free_dofs,
            assembly_time=assembly_time,
            solve_time=solve_time,
            total_time=total_time,
            memory_usage=final_memory - initial_memory,
            peak_memory=peak_memory,
            system_info=self.system_info
        )
        
        self.results.append(result)
        
        print(f"  Assembly time: {assembly_time:.4f}s")
        print(f"  Solve time: {solve_time:.4f}s") 
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Memory usage: {result.memory_usage:.2f} MB")
        print(f"  Peak memory: {peak_memory:.2f} MB")
        
        return result
    
    def create_test_structures(self) -> List[Tuple[Structure, str]]:
        """Create test structures of varying sizes for benchmarking."""
        structures = []
        
        # Simple beam structures with increasing complexity
        sizes = [
            (5, "small"), (10, "medium"), (25, "large"), 
            (50, "xlarge"), (100, "xxlarge")
        ]
        
        steel = IsotropicMaterial.steel("S355")
        section = RectangularSection(steel, width=0.2, height=0.4, label="200x400")
        
        for n_elements, size_label in sizes:
            structure = Structure(f"Test_Beam_{size_label}")
            
            # Create simply supported beam with multiple spans
            span_length = 4.0  # meters
            nodes = []
            
            # Create nodes
            for i in range(n_elements + 1):
                x = i * span_length / n_elements * 4  # 4 spans total
                node = Node2D(x=x, y=0.0, label=f"N{i+1}")
                
                # Apply boundary conditions
                if i == 0:  # Left support - pinned
                    node.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
                elif i == n_elements:  # Right support - roller
                    node.restrain(NodalDegreeOfFreedom.UY)
                
                nodes.append(node)
                structure.add_node(node)
            
            # Create elements
            for i in range(n_elements):
                element = FrameElement2D(
                    start_node=nodes[i],
                    end_node=nodes[i + 1],
                    cross_section=section,
                    label=f"E{i+1}"
                )
                element.loads = []
                structure.add_element(element)
            
            # Add load case with distributed loading
            load_case = LoadCase("Test Load", LoadType.LIVE)
            structure.add_load_case(load_case)
            
            # Add point loads at several locations
            n_loads = max(1, n_elements // 4)
            for i in range(n_loads):
                element_idx = (i + 1) * n_elements // (n_loads + 1) - 1
                element = structure.elements[element_idx]
                
                point_load = PointLoad(
                    load_case=load_case,
                    Fx=0.0,
                    Fy=-100.0,  # 100 kN downward
                    distance=element.length / 2,
                    label=f"P{i+1}"
                )
                element.loads.append(point_load)
            
            structures.append((structure, f"beam_{size_label}_{n_elements}elements"))
        
        # 2D Frame structures
        frame_sizes = [(3, 2), (5, 3), (8, 5)]  # (width_bays, height_stories)
        
        for width_bays, height_stories, in frame_sizes:
            structure = Structure(f"Frame_{width_bays}x{height_stories}")
            
            bay_width = 6.0  # meters
            story_height = 3.5  # meters
            
            nodes = {}
            
            # Create grid of nodes
            for j in range(height_stories + 1):  # Floors
                for i in range(width_bays + 1):   # Columns
                    x = i * bay_width
                    y = j * story_height
                    node = Node2D(x=x, y=y, label=f"N{j+1}_{i+1}")
                    
                    # Ground floor supports
                    if j == 0:
                        if i == 0:  # Left corner - pinned
                            node.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
                        elif i == width_bays:  # Right corner - roller
                            node.restrain(NodalDegreeOfFreedom.UY)
                        else:  # Middle supports - pinned
                            node.restrain(NodalDegreeOfFreedom.UX, NodalDegreeOfFreedom.UY)
                    
                    nodes[(i, j)] = node
                    structure.add_node(node)
            
            # Create beam and column elements
            beam_section = RectangularSection(steel, 0.3, 0.6, "Beam_300x600")
            column_section = RectangularSection(steel, 0.4, 0.4, "Column_400x400")
            
            element_count = 0
            
            # Horizontal beams
            for j in range(1, height_stories + 1):  # Skip ground level
                for i in range(width_bays):
                    start_node = nodes[(i, j)]
                    end_node = nodes[(i + 1, j)]
                    element = FrameElement2D(
                        start_node=start_node,
                        end_node=end_node,
                        cross_section=beam_section,
                        label=f"B{element_count+1}"
                    )
                    element.loads = []
                    structure.add_element(element)
                    element_count += 1
            
            # Vertical columns
            for i in range(width_bays + 1):
                for j in range(height_stories):
                    start_node = nodes[(i, j)]
                    end_node = nodes[(i, j + 1)]
                    element = FrameElement2D(
                        start_node=start_node,
                        end_node=end_node,
                        cross_section=column_section,
                        label=f"C{element_count+1}"
                    )
                    element.loads = []
                    structure.add_element(element)
                    element_count += 1
            
            # Add loads
            load_case = LoadCase("Frame Load", LoadType.LIVE)
            structure.add_load_case(load_case)
            
            # Add loads to beams
            for element in structure.elements:
                if element.label.startswith('B'):  # Beam elements
                    from ..loads.distributed_load import UniformLoad
                    udl = UniformLoad(
                        load_case=load_case,
                        wx=0.0,
                        wy=-50.0,  # 50 kN/m
                        label="UDL_50"
                    )
                    element.loads.append(udl)
            
            test_name = f"frame_{width_bays}x{height_stories}_{structure.n_elements}elements"
            structures.append((structure, test_name))
        
        return structures
    
    def run_benchmark_suite(self) -> List[BenchmarkResult]:
        """Run complete benchmark suite."""
        print("PyFEALiTE Performance Benchmark Suite")
        print("=" * 50)
        
        structures = self.create_test_structures()
        results = []
        
        for structure, test_name in structures:
            try:
                result = self.benchmark_structure(structure, test_name)
                results.append(result)
                print()  # Empty line between tests
            except Exception as e:
                print(f"  Failed: {e}")
                print()
        
        return results
    
    def export_results(self, filepath: Path) -> None:
        """Export benchmark results to JSON file."""
        data = {
            "benchmark_info": {
                "tool": "PyFEALiTE",
                "version": "0.1.0",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system_info": self.system_info
            },
            "results": [result.to_dict() for result in self.results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Benchmark results exported to: {filepath}")
    
    def print_summary(self) -> None:
        """Print benchmark results summary."""
        if not self.results:
            print("No benchmark results available")
            return
        
        print("\nBenchmark Results Summary")
        print("=" * 60)
        print(f"{'Test Name':<25} {'Nodes':<8} {'Elements':<10} {'DOFs':<8} {'Total Time':<12}")
        print("-" * 60)
        
        for result in self.results:
            print(f"{result.test_name:<25} {result.n_nodes:<8} {result.n_elements:<10} "
                  f"{result.n_dofs:<8} {result.total_time:<12.4f}s")
        
        # Performance scaling analysis
        print("\nScaling Analysis:")
        print("-" * 30)
        
        # Sort by DOF count for scaling analysis
        sorted_results = sorted(self.results, key=lambda r: r.n_dofs)
        
        for i, result in enumerate(sorted_results):
            dofs_per_second = result.n_dofs / result.total_time if result.total_time > 0 else 0
            memory_per_dof = result.memory_usage / result.n_dofs if result.n_dofs > 0 else 0
            
            print(f"{result.test_name}: {dofs_per_second:.0f} DOFs/sec, "
                  f"{memory_per_dof:.4f} MB/DOF")


# Convenience functions
def benchmark_analysis(structure: Structure, test_name: str = "") -> BenchmarkResult:
    """Benchmark a single structure analysis."""
    benchmark = PerformanceBenchmark()
    return benchmark.benchmark_structure(structure, test_name)


def run_performance_suite() -> List[BenchmarkResult]:
    """Run the complete PyFEALiTE performance benchmark suite."""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_benchmark_suite()
    
    # Print summary
    benchmark.print_summary()
    
    # Export results
    export_path = Path("pyfealite_benchmark_results.json")
    benchmark.export_results(export_path)
    
    return results


def compare_with_baseline(current_results: List[BenchmarkResult], 
                         baseline_file: Path) -> None:
    """Compare current results with baseline performance."""
    try:
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        baseline_results = {r["test_name"]: r for r in baseline_data["results"]}
        
        print("\nPerformance Comparison with Baseline")
        print("=" * 50)
        print(f"{'Test Name':<25} {'Current':<10} {'Baseline':<10} {'Change':<10}")
        print("-" * 50)
        
        for result in current_results:
            if result.test_name in baseline_results:
                baseline = baseline_results[result.test_name]
                baseline_time = baseline["total_time"]
                current_time = result.total_time
                
                if baseline_time > 0:
                    change = ((current_time - baseline_time) / baseline_time) * 100
                    change_str = f"{change:+.1f}%"
                    
                    print(f"{result.test_name:<25} {current_time:<10.4f}s "
                          f"{baseline_time:<10.4f}s {change_str:<10}")
                else:
                    print(f"{result.test_name:<25} {current_time:<10.4f}s "
                          f"{'N/A':<10} {'N/A':<10}")
            else:
                print(f"{result.test_name:<25} {result.total_time:<10.4f}s "
                      f"{'N/A':<10} {'NEW':<10}")
        
    except FileNotFoundError:
        print(f"Baseline file not found: {baseline_file}")
    except Exception as e:
        print(f"Error comparing with baseline: {e}")