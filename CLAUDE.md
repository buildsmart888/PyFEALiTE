# PyFEALiTE Development Guide

## Project Overview
การ port FEALiTE2D (C#) ไปเป็น Python version เพื่อ flexibility และ rapid development

## Development Environment Setup

### Prerequisites
```bash
# Python 3.9+ required
python --version

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Required Dependencies
```bash
pip install numpy>=1.20.0
pip install scipy>=1.7.0
pip install matplotlib>=3.4.0
pip install plotly>=5.0.0
pip install pandas>=1.3.0
pip install pytest>=6.0.0
pip install ezdxf>=0.16.0
pip install streamlit>=1.0.0
```

## Project Structure
```
pyFEALiTE/
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/
│   └── pyfealite/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── node.py         # Node2D class
│       │   ├── element.py      # Element classes
│       │   ├── structure.py    # Main structure class
│       │   └── solver.py       # Analysis solver
│       ├── materials/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── isotropic.py
│       ├── sections/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── rectangular.py
│       │   └── circular.py
│       ├── loads/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── point_load.py
│       │   └── distributed_load.py
│       ├── visualization/
│       │   ├── __init__.py
│       │   ├── plotter.py
│       │   └── exporters/
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── test_core/
│   ├── test_materials/
│   └── test_integration/
├── examples/
│   ├── basic_beam.py
│   ├── frame_analysis.py
│   └── notebooks/
└── docs/
```

## Development Phase Plan

### ✅ Phase 1: Core Foundation (COMPLETED)
1. ✅ Setup project structure
2. ✅ Port Node2D class with dataclasses
3. ✅ Port Material classes
4. ✅ Create first unit tests

### ✅ Phase 2: Elements & Sections (COMPLETED)
1. ✅ Port CrossSection classes (Rectangular, Circular, Hollow)
2. ✅ Port FrameElement2D with NumPy matrices
3. ✅ Implement transformation matrices
4. ✅ Test stiffness matrix calculations (24 tests passed)

### 🚧 Phase 3: Solver & Structure (IN PROGRESS)
1. 🚧 Port Structure class
2. 🚧 Implement sparse matrix solver with SciPy
3. 🚧 Create Load classes (Point, Distributed, Nodal)
4. 🚧 Assembly global stiffness matrix
5. 🚧 Port PostProcessor for results
6. 🚧 Validate against C# version

### 📋 Phase 4: Visualization & Export (PLANNED)
1. Create Matplotlib/Plotly visualizers
2. DXF export with ezdxf
3. Interactive web interface with Streamlit
4. Jupyter notebook examples

## Current Status (Phase 3)

### ✅ Working Components:
- Node2D with boundary conditions
- IsotropicMaterial with Steel/Concrete/Aluminum presets
- RectangularSection, CircularSection, HollowCircularSection
- FrameElement2D with end releases and stiffness matrices
- Coordinate transformations
- 24 comprehensive unit tests

### 🚧 Currently Implementing:
- Load classes (PointLoad, DistributedLoad, NodalLoad)
- Structure class for assembly and analysis
- Global stiffness matrix assembly
- Equation solver with SciPy sparse matrices
- PostProcessor for results extraction

## Key Design Decisions

### Modern Python Features
- Type hints for better code documentation
- Dataclasses for simple data containers
- Properties for computed values
- Context managers for resource management

### Performance Considerations
- NumPy for matrix operations
- SciPy sparse matrices for large systems
- Optional Numba JIT compilation for hot paths
- Memory-efficient data structures

### Code Examples

#### Node2D Implementation
```python
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np

@dataclass
class Node2D:
    x: float
    y: float
    label: str
    restraints: List[bool] = field(default_factory=lambda: [False, False, False])
    coord_numbers: List[int] = field(default_factory=list)
    
    def is_restrained(self, dof: int) -> bool:
        return self.restraints[dof]
    
    def distance_to(self, other: 'Node2D') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
```

#### Material Implementation
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Material(ABC):
    E: float  # Young's modulus
    label: str = ""
    
    def __post_init__(self):
        if self.E <= 0:
            raise ValueError("Young's modulus must be positive")

@dataclass
class IsotropicMaterial(Material):
    nu: float = 0.2  # Poisson's ratio
    density: float = 0.0
    alpha: float = 0.0  # Thermal expansion
```

## Testing Strategy

### Unit Tests
```python
import pytest
import numpy as np
from pyfealite.core.node import Node2D

def test_node_creation():
    node = Node2D(x=0.0, y=0.0, label="n1")
    assert node.x == 0.0
    assert node.label == "n1"
    assert not any(node.restraints)

def test_node_distance():
    n1 = Node2D(0, 0, "n1")
    n2 = Node2D(3, 4, "n2")
    assert n1.distance_to(n2) == 5.0
```

### Integration Tests
- Compare results with original C# implementation
- Validate against known analytical solutions
- Performance benchmarking

## Development Commands

### Setup Development Environment
```bash
# Clone and setup
git clone [repository]
cd pyFEALiTE
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/pyfealite

# Run specific test file
pytest tests/test_core/test_node.py
```

### Development Workflow
```bash
# Format code
black src/ tests/

# Type checking
mypy src/pyfealite

# Linting
flake8 src/ tests/

# Build package
python -m build
```

## Migration Mapping

### C# to Python Class Mapping
- `Node2D` → `pyfealite.core.node.Node2D`
- `FrameElement2D` → `pyfealite.core.element.FrameElement2D`
- `Structure` → `pyfealite.core.structure.Structure`
- `GenericIsotropicMaterial` → `pyfealite.materials.isotropic.IsotropicMaterial`
- `PostProcessor` → `pyfealite.core.postprocessor.PostProcessor`

### Matrix Operations
- `CSparse.Double.SparseMatrix` → `scipy.sparse matrices`
- `DenseMatrix` → `numpy.ndarray`
- Matrix operations use NumPy/SciPy equivalents

## Performance Targets
- Solve time within 2x of C# version for same problems
- Memory usage comparable or better
- Visualization generation < 1 second for typical models

## Future Enhancements
- GPU acceleration with CuPy
- Parallel processing for large models
- Machine learning integration
- Cloud deployment capabilities
- Advanced visualization features

## Getting Started
1. Follow setup instructions above
2. Run example: `python examples/basic_beam.py`
3. Explore Jupyter notebooks in `examples/notebooks/`
4. Check tests: `pytest tests/`

## Contributing Guidelines
- Follow PEP 8 style guide
- Add type hints to all functions
- Write tests for new features
- Update documentation
- Use descriptive commit messages