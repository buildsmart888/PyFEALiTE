"""
Test Plugin System Core Functionality

Tests for the plugin architecture base classes and registry.
"""

import pytest
from typing import List
from unittest.mock import Mock

from pyfealite.plugins.base import (
    AnalysisPlugin,
    PluginMetadata, 
    AnalysisCapability,
    PluginRegistry,
    PluginError
)


class MockPlugin(AnalysisPlugin):
    """Mock plugin for testing."""
    
    def __init__(self, name: str = "Mock Plugin", 
                 capabilities: List[AnalysisCapability] = None,
                 priority: int = 50,
                 dependencies: List[str] = None):
        self._metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            description="Mock plugin for testing",
            author="Test Author",
            capabilities=capabilities or [AnalysisCapability.STATIC_2D],
            dependencies=dependencies or [],
            min_pyfealite_version="2.0.0",
            priority=priority
        )
        self._can_analyze_result = True
        self._validation_issues = []
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def can_analyze(self, structure, analysis_type: AnalysisCapability) -> bool:
        return analysis_type in self._metadata.capabilities and self._can_analyze_result
    
    def validate_structure(self, structure) -> List[str]:
        return self._validation_issues.copy()
    
    def analyze(self, structure, analysis_type: AnalysisCapability, **kwargs):
        # Mock analysis result
        return Mock(
            analysis_type=analysis_type.value,
            status="success",
            engine=self._metadata.name
        )
    
    def set_can_analyze(self, result: bool):
        """Set can_analyze result for testing."""
        self._can_analyze_result = result
    
    def add_validation_issue(self, issue: str):
        """Add validation issue for testing."""
        self._validation_issues.append(issue)


class TestPluginMetadata:
    """Test PluginMetadata class."""
    
    def test_valid_metadata(self):
        """Test valid metadata creation."""
        metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0", 
            description="Test description",
            author="Test Author",
            capabilities=[AnalysisCapability.STATIC_2D],
            dependencies=["numpy"],
            min_pyfealite_version="2.0.0"
        )
        
        assert metadata.name == "Test Plugin"
        assert metadata.priority == 50  # default
        assert AnalysisCapability.STATIC_2D in metadata.capabilities
    
    def test_empty_name_validation(self):
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="Plugin name cannot be empty"):
            PluginMetadata(
                name="",
                version="1.0.0",
                description="Test",
                author="Author",
                capabilities=[AnalysisCapability.STATIC_2D],
                dependencies=[],
                min_pyfealite_version="2.0.0"
            )
    
    def test_empty_capabilities_validation(self):
        """Test that empty capabilities raises error."""
        with pytest.raises(ValueError, match="Plugin must declare at least one capability"):
            PluginMetadata(
                name="Test",
                version="1.0.0",
                description="Test",
                author="Author", 
                capabilities=[],
                dependencies=[],
                min_pyfealite_version="2.0.0"
            )
    
    def test_priority_validation(self):
        """Test priority validation."""
        with pytest.raises(ValueError, match="Priority must be between 0 and 100"):
            PluginMetadata(
                name="Test",
                version="1.0.0",
                description="Test",
                author="Author",
                capabilities=[AnalysisCapability.STATIC_2D],
                dependencies=[],
                min_pyfealite_version="2.0.0",
                priority=150  # Invalid priority
            )


class TestPluginRegistry:
    """Test PluginRegistry class."""
    
    def test_register_plugin(self):
        """Test plugin registration."""
        registry = PluginRegistry()
        plugin = MockPlugin(name="Test Plugin")
        
        registry.register_plugin(plugin)
        
        assert "Test Plugin" in registry._plugins
        assert registry.get_plugin("Test Plugin") == plugin
    
    def test_get_available_plugins(self):
        """Test getting available plugins."""
        registry = PluginRegistry()
        plugin1 = MockPlugin(name="Plugin 1")
        plugin2 = MockPlugin(name="Plugin 2")
        
        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)
        
        available = registry.get_available_plugins()
        assert len(available) == 2
        assert "Plugin 1" in available
        assert "Plugin 2" in available
    
    def test_get_capabilities(self):
        """Test getting available capabilities."""
        registry = PluginRegistry()
        plugin1 = MockPlugin(capabilities=[AnalysisCapability.STATIC_2D])
        plugin2 = MockPlugin(capabilities=[AnalysisCapability.STATIC_3D, AnalysisCapability.MODAL_3D])
        
        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)
        
        capabilities = registry.get_capabilities()
        assert AnalysisCapability.STATIC_2D in capabilities
        assert AnalysisCapability.STATIC_3D in capabilities
        assert AnalysisCapability.MODAL_3D in capabilities
    
    def test_get_capable_plugins(self):
        """Test getting plugins capable of analysis."""
        registry = PluginRegistry()
        
        # Plugin that can do static 2D
        plugin1 = MockPlugin(name="2D Plugin", capabilities=[AnalysisCapability.STATIC_2D])
        
        # Plugin that can do static 3D
        plugin2 = MockPlugin(name="3D Plugin", capabilities=[AnalysisCapability.STATIC_3D])
        
        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)
        
        # Mock structure
        structure = Mock()
        
        # Test getting plugins for 2D analysis
        capable_2d = registry.get_capable_plugins(structure, AnalysisCapability.STATIC_2D)
        assert len(capable_2d) == 1
        assert capable_2d[0] == plugin1
        
        # Test getting plugins for 3D analysis
        capable_3d = registry.get_capable_plugins(structure, AnalysisCapability.STATIC_3D)
        assert len(capable_3d) == 1
        assert capable_3d[0] == plugin2
    
    def test_plugin_priority_sorting(self):
        """Test that plugins are sorted by priority."""
        registry = PluginRegistry()
        
        # Lower priority plugin
        low_priority = MockPlugin(name="Low Priority", priority=30,
                                capabilities=[AnalysisCapability.STATIC_2D])
        
        # Higher priority plugin
        high_priority = MockPlugin(name="High Priority", priority=80,
                                 capabilities=[AnalysisCapability.STATIC_2D])
        
        registry.register_plugin(low_priority)
        registry.register_plugin(high_priority)
        
        structure = Mock()
        capable = registry.get_capable_plugins(structure, AnalysisCapability.STATIC_2D)
        
        # Should be sorted by priority (higher first)
        assert len(capable) == 2
        assert capable[0] == high_priority  # Higher priority first
        assert capable[1] == low_priority
    
    def test_select_best_plugin(self):
        """Test selecting best plugin for analysis."""
        registry = PluginRegistry()
        
        plugin = MockPlugin(name="Best Plugin", capabilities=[AnalysisCapability.STATIC_2D])
        registry.register_plugin(plugin)
        
        structure = Mock()
        
        best = registry.select_best_plugin(structure, AnalysisCapability.STATIC_2D)
        assert best == plugin
    
    def test_select_preferred_plugin(self):
        """Test selecting preferred plugin."""
        registry = PluginRegistry()
        
        plugin1 = MockPlugin(name="Plugin 1", priority=90,
                           capabilities=[AnalysisCapability.STATIC_2D])
        plugin2 = MockPlugin(name="Plugin 2", priority=50,
                           capabilities=[AnalysisCapability.STATIC_2D])
        
        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)
        
        structure = Mock()
        
        # Select preferred plugin (lower priority)
        selected = registry.select_best_plugin(
            structure, AnalysisCapability.STATIC_2D, 
            preferred_plugin="Plugin 2"
        )
        assert selected == plugin2
    
    def test_no_capable_plugin_error(self):
        """Test error when no plugin can handle analysis."""
        registry = PluginRegistry()
        
        # Plugin that only does 2D
        plugin = MockPlugin(capabilities=[AnalysisCapability.STATIC_2D])
        registry.register_plugin(plugin)
        
        structure = Mock()
        
        # Request 3D analysis - should fail
        with pytest.raises(PluginError, match="No plugin available for static_3d"):
            registry.select_best_plugin(structure, AnalysisCapability.STATIC_3D)
    
    def test_plugin_validation_failure(self):
        """Test plugin validation failure."""
        registry = PluginRegistry()
        
        plugin = MockPlugin(capabilities=[AnalysisCapability.STATIC_2D])
        plugin.add_validation_issue("Test validation issue")
        
        registry.register_plugin(plugin)
        
        structure = Mock()
        
        # Should get no capable plugins due to validation failure
        capable = registry.get_capable_plugins(structure, AnalysisCapability.STATIC_2D)
        assert len(capable) == 0
    
    def test_get_plugin_info(self):
        """Test getting plugin information."""
        registry = PluginRegistry()
        
        plugin = MockPlugin(
            name="Info Plugin",
            capabilities=[AnalysisCapability.STATIC_2D, AnalysisCapability.MODAL_2D]
        )
        registry.register_plugin(plugin)
        
        info = registry.get_plugin_info()
        assert "Info Plugin" in info
        
        plugin_info = info["Info Plugin"]
        assert plugin_info["version"] == "1.0.0"
        assert plugin_info["description"] == "Mock plugin for testing"
        assert "static_2d" in plugin_info["capabilities"]
        assert "modal_2d" in plugin_info["capabilities"]
    
    def test_get_installation_help(self):
        """Test getting installation help."""
        registry = PluginRegistry()
        
        # Plugin with PyNite dependency
        plugin = MockPlugin(
            name="3D Plugin",
            capabilities=[AnalysisCapability.STATIC_3D],
            dependencies=["PyNite>=1.0.15"]
        )
        registry.register_plugin(plugin)
        
        help_text = registry.get_installation_help(AnalysisCapability.STATIC_3D)
        assert "pip install pyfealite[3d]" in help_text


class TestMockPlugin:
    """Test MockPlugin functionality."""
    
    def test_mock_plugin_creation(self):
        """Test creating mock plugin."""
        plugin = MockPlugin(
            name="Test Mock",
            capabilities=[AnalysisCapability.STATIC_2D, AnalysisCapability.MODAL_2D],
            priority=75
        )
        
        assert plugin.metadata.name == "Test Mock"
        assert plugin.metadata.priority == 75
        assert len(plugin.metadata.capabilities) == 2
    
    def test_can_analyze_control(self):
        """Test controlling can_analyze result."""
        plugin = MockPlugin()
        structure = Mock()
        
        # Initially should return True
        assert plugin.can_analyze(structure, AnalysisCapability.STATIC_2D)
        
        # Set to False
        plugin.set_can_analyze(False)
        assert not plugin.can_analyze(structure, AnalysisCapability.STATIC_2D)
    
    def test_validation_issues(self):
        """Test adding validation issues."""
        plugin = MockPlugin()
        structure = Mock()
        
        # Initially no issues
        assert len(plugin.validate_structure(structure)) == 0
        
        # Add issues
        plugin.add_validation_issue("Issue 1")
        plugin.add_validation_issue("Issue 2")
        
        issues = plugin.validate_structure(structure)
        assert len(issues) == 2
        assert "Issue 1" in issues
        assert "Issue 2" in issues
    
    def test_analyze_method(self):
        """Test analyze method."""
        plugin = MockPlugin(name="Analyzer")
        structure = Mock()
        
        result = plugin.analyze(structure, AnalysisCapability.STATIC_2D)
        
        assert result.analysis_type == "static_2d"
        assert result.status == "success"
        assert result.engine == "Analyzer"


if __name__ == "__main__":
    pytest.main([__file__])