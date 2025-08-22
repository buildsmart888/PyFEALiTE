#!/usr/bin/env python3
"""
Development Environment Setup Script

This script sets up the development environment for PyFEALiTE plugin architecture.
It handles dependencies, creates necessary directories, and validates the setup.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a shell command with error handling."""
    print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️  {description} completed with warnings")
            if result.stderr.strip():
                print(f"   Warning: {result.stderr.strip()}")
        
        return result
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        if not check:
            return e
        raise


def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   PyFEALiTE requires Python 3.9+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
    return True


def check_virtual_environment():
    """Check if running in virtual environment."""
    print("🏠 Checking virtual environment...")
    
    in_venv = (hasattr(sys, 'real_prefix') or 
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    
    if in_venv:
        print(f"✅ Running in virtual environment: {sys.prefix}")
    else:
        print("⚠️  Not running in virtual environment")
        print("   Recommended: Create and activate a virtual environment")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate  # Windows")
        print("   source venv/bin/activate  # Linux/Mac")
    
    return in_venv


def install_core_dependencies():
    """Install core PyFEALiTE dependencies."""
    print("📦 Installing core dependencies...")
    
    core_deps = [
        "numpy>=1.20.0",
        "scipy>=1.7.0", 
        "matplotlib>=3.4.0",
        "pandas>=1.3.0"
    ]
    
    for dep in core_deps:
        cmd = f"pip install {dep}"
        run_command(cmd, f"Installing {dep}")


def install_development_dependencies():
    """Install development dependencies."""
    print("🛠️  Installing development dependencies...")
    
    dev_deps = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "mypy>=1.5.0",
        "ruff>=0.0.280"
    ]
    
    for dep in dev_deps:
        cmd = f"pip install {dep}"
        run_command(cmd, f"Installing {dep}")


def install_optional_dependencies():
    """Install optional dependencies if available."""
    print("🔧 Installing optional dependencies...")
    
    optional_deps = [
        ("PyNite>=1.0.15", "3D analysis capabilities"),
        ("plotly>=5.0.0", "Interactive visualization"),
        ("ezdxf>=1.0.0", "DXF export functionality"),
        ("streamlit>=1.25.0", "Web interface"),
        ("fastapi>=0.100.0", "API backend")
    ]
    
    for dep, description in optional_deps:
        cmd = f"pip install {dep}"
        result = run_command(cmd, f"Installing {dep} ({description})", check=False)
        
        if isinstance(result, subprocess.CalledProcessError):
            print(f"⚠️  Optional dependency {dep} not installed")


def create_directory_structure():
    """Create necessary directory structure."""
    print("📁 Creating directory structure...")
    
    directories = [
        "src/pyfealite/plugins",
        "src/pyfealite/analysis",
        "tests/test_plugins",
        "examples/plugins",
        "scripts",
        "docs/plugins"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")


def validate_plugin_system():
    """Validate that the plugin system is working."""
    print("🔍 Validating plugin system...")
    
    try:
        # Add current directory to Python path
        current_dir = Path.cwd()
        sys.path.insert(0, str(current_dir / "src"))
        
        # Try importing plugin system
        from pyfealite.plugins import plugin_registry, AnalysisCapability
        
        print("✅ Plugin system imports successful")
        
        # Check plugin discovery
        plugins = plugin_registry.get_available_plugins()
        print(f"📦 Discovered {len(plugins)} plugins")
        
        for name, plugin in plugins.items():
            print(f"   • {name} v{plugin.metadata.version}")
        
        # Check capabilities
        capabilities = plugin_registry.get_capabilities()
        print(f"🎯 Available capabilities: {len(capabilities)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Plugin system validation failed: {e}")
        print("   This is expected if core PyFEALiTE classes are not yet implemented")
        return False
    except Exception as e:
        print(f"❌ Plugin validation error: {e}")
        return False


def create_development_config():
    """Create development configuration files."""
    print("⚙️  Creating development configuration...")
    
    # pytest configuration
    pytest_config = """[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
markers = [
    "integration: marks tests as integration tests",
    "plugin: marks tests as plugin tests",
    "slow: marks tests as slow running"
]
"""
    
    # Create pyproject.toml if it doesn't exist
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("✅ Created pytest configuration in pyproject.toml")
        with open(pyproject_path, "w") as f:
            f.write(pytest_config)
    
    # Create .gitignore for development
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Plugin development
*.log
temp/
"""
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")


def run_test_suite():
    """Run the plugin framework test suite."""
    print("🧪 Running plugin framework tests...")
    
    # Run our custom test script
    test_script = Path("scripts/test_plugin_framework.py")
    if test_script.exists():
        cmd = f"python {test_script}"
        result = run_command(cmd, "Running plugin framework tests", check=False)
        
        if isinstance(result, subprocess.CalledProcessError):
            print("⚠️  Some tests failed - this is expected during initial setup")
            return False
        else:
            return True
    else:
        print("⚠️  Test script not found - skipping tests")
        return False


def main():
    """Main setup function."""
    print("🚀 PyFEALiTE Plugin Architecture Development Setup")
    print("=" * 55)
    print()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Check environment
    in_venv = check_virtual_environment()
    
    if not in_venv:
        response = input("\n❓ Continue without virtual environment? (y/N): ")
        if response.lower() != 'y':
            print("💡 Please create and activate a virtual environment first")
            return False
    
    print()
    
    try:
        # Setup steps
        install_core_dependencies()
        print()
        
        install_development_dependencies()
        print()
        
        install_optional_dependencies()
        print()
        
        create_directory_structure()
        print()
        
        create_development_config()
        print()
        
        # Validation
        plugin_valid = validate_plugin_system()
        print()
        
        if plugin_valid:
            test_success = run_test_suite()
        else:
            test_success = False
        
        # Summary
        print("=" * 55)
        print("🎉 Development Environment Setup Complete!")
        print()
        print("📊 Setup Summary:")
        print(f"   ✅ Python version: OK")
        print(f"   {'✅' if in_venv else '⚠️ '} Virtual environment: {'Active' if in_venv else 'Not active'}")
        print(f"   ✅ Core dependencies: Installed")
        print(f"   ✅ Development tools: Installed")
        print(f"   ✅ Directory structure: Created")
        print(f"   {'✅' if plugin_valid else '⚠️ '} Plugin system: {'Valid' if plugin_valid else 'Pending core implementation'}")
        print(f"   {'✅' if test_success else '⚠️ '} Tests: {'Passing' if test_success else 'Some issues (expected)'}")
        print()
        print("🚀 Next Steps:")
        print("   1. Run plugin demo: python examples/plugin_architecture_demo.py")
        print("   2. Run tests: python scripts/test_plugin_framework.py")
        print("   3. Start development: Edit src/pyfealite/plugins/")
        print("   4. Install 3D plugin: pip install PyNite")
        print("   5. Run full test suite: pytest tests/")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)