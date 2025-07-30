"""
Tests for core models.

This module tests the core data models including DetectionConfig,
FrameworkMetadata, and related validation logic.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from php_framework_detector.core.models import (
    DetectionConfig,
    FrameworkMetadata,
    FrameworkInfo,
    DetectionResult,
    FrameworkType
)


class TestDetectionConfig:
    """Test DetectionConfig model."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DetectionConfig()
        
        assert config.check_composer is True
        assert config.check_files is True
        assert config.check_dependencies is True
        assert config.max_file_size == 1024 * 1024
        assert config.timeout == 30
        assert config.verbose is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = DetectionConfig(
            check_composer=False,
            check_files=False,
            check_dependencies=False,
            max_file_size=2048,
            timeout=60,
            verbose=True
        )
        
        assert config.check_composer is False
        assert config.check_files is False
        assert config.check_dependencies is False
        assert config.max_file_size == 2048
        assert config.timeout == 60
        assert config.verbose is True
    
    def test_max_file_size_validation(self):
        """Test max_file_size validation."""
        # Should accept valid values
        config = DetectionConfig(max_file_size=1024)
        assert config.max_file_size == 1024
        
        # Should reject values below minimum
        with pytest.raises(ValidationError):
            DetectionConfig(max_file_size=512)
        
        # Should accept values at minimum
        config = DetectionConfig(max_file_size=1024)
        assert config.max_file_size == 1024
    
    def test_timeout_validation(self):
        """Test timeout validation."""
        # Should accept valid values
        config = DetectionConfig(timeout=15)
        assert config.timeout == 15
        
        # Should reject values below minimum
        with pytest.raises(ValidationError):
            DetectionConfig(timeout=0)
        
        # Should reject values above maximum
        with pytest.raises(ValidationError):
            DetectionConfig(timeout=301)
        
        # Should accept boundary values
        config = DetectionConfig(timeout=1)
        assert config.timeout == 1
        
        config = DetectionConfig(timeout=300)
        assert config.timeout == 300


class TestFrameworkMetadata:
    """Test FrameworkMetadata model."""
    
    def test_framework_metadata_creation(self):
        """Test creating FrameworkMetadata."""
        metadata = FrameworkMetadata(
            framework_type=FrameworkType.LARAVEL,
            detection_methods=["file_patterns", "composer_packages"],
            file_patterns=["artisan", "app/"],
            composer_packages=["laravel/framework"],
            content_patterns=["Laravel Framework", "Illuminate\\"]
        )
        
        assert metadata.framework_type == FrameworkType.LARAVEL
        assert metadata.framework_code == "laravel"
        assert metadata.detection_methods == ["file_patterns", "composer_packages"]
        assert metadata.file_patterns == ["artisan", "app/"]
        assert metadata.composer_packages == ["laravel/framework"]
        assert metadata.content_patterns == ["Laravel Framework", "Illuminate\\"]
    
    def test_framework_metadata_defaults(self):
        """Test FrameworkMetadata with default values."""
        metadata = FrameworkMetadata(framework_type=FrameworkType.SYMFONY)
        
        assert metadata.framework_type == FrameworkType.SYMFONY
        assert metadata.framework_code == "symfony"
        assert metadata.detection_methods == []
        assert metadata.file_patterns == []
        assert metadata.composer_packages == []
        assert metadata.content_patterns == []
    
    def test_framework_code_property(self):
        """Test framework_code property for different frameworks."""
        laravel_metadata = FrameworkMetadata(framework_type=FrameworkType.LARAVEL)
        assert laravel_metadata.framework_code == "laravel"
        
        symfony_metadata = FrameworkMetadata(framework_type=FrameworkType.SYMFONY)
        assert symfony_metadata.framework_code == "symfony"
        
        na_metadata = FrameworkMetadata(framework_type=FrameworkType.NA)
        assert na_metadata.framework_code == "na"


class TestFrameworkInfo:
    """Test FrameworkInfo model."""
    
    def test_framework_info_creation(self):
        """Test creating FrameworkInfo."""
        info = FrameworkInfo(
            framework_type=FrameworkType.LARAVEL,
            version="10.0.0",
            confidence=95
        )
        
        assert info.framework_type == FrameworkType.LARAVEL
        assert info.name == "Laravel"  # Auto-generated from enum
        assert info.description == "Modern PHP web application framework with elegant syntax"
        assert info.version == "10.0.0"
        assert info.confidence == 95
        assert info.code == "laravel"
    
    def test_framework_info_custom_values(self):
        """Test FrameworkInfo with custom name and description."""
        info = FrameworkInfo(
            framework_type=FrameworkType.SYMFONY,
            name="Custom Symfony",
            description="Custom description",
            version="6.0.0",
            confidence=88
        )
        
        assert info.framework_type == FrameworkType.SYMFONY
        assert info.name == "Custom Symfony"
        assert info.description == "Custom description"
        assert info.version == "6.0.0"
        assert info.confidence == 88
        assert info.code == "symfony"
    
    def test_confidence_validation(self):
        """Test confidence score validation."""
        # Should accept valid values
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=50)
        assert info.confidence == 50
        
        # Should reject values below 0
        with pytest.raises(ValidationError):
            FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=-1)
        
        # Should reject values above 100
        with pytest.raises(ValidationError):
            FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=101)
        
        # Should accept boundary values
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=0)
        assert info.confidence == 0
        
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=100)
        assert info.confidence == 100
    
    def test_auto_generated_values(self):
        """Test auto-generated name and description."""
        # Test with not available framework
        info = FrameworkInfo(framework_type=FrameworkType.NA)
        assert info.name == "Not Available"
        assert info.description == "No framework detected"
        assert info.code == "na"
        
        # Test with known framework
        info = FrameworkInfo(framework_type=FrameworkType.CODEIGNITER)
        assert info.name == "CodeIgniter"
        assert "Lightweight PHP framework" in info.description
        assert info.code == "codeigniter"


class TestDetectionResult:
    """Test DetectionResult model."""
    
    def test_detection_result_creation(self):
        """Test creating DetectionResult."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.NA: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        assert result.detected_framework == FrameworkType.LARAVEL
        assert result.detected_name == "Laravel"
        assert result.detected_framework_code == "laravel"
        assert result.scores == scores
        assert result.project_path == "/path/to/project"
        assert result.is_framework_detected is True
        assert result.confidence_score == 95
        assert isinstance(result.detection_time, datetime)
        assert result.total_frameworks is None
    
    def test_detection_result_not_available(self):
        """Test DetectionResult with not available framework."""
        scores = {FrameworkType.NA: 0}
        
        result = DetectionResult(
            detected_framework=FrameworkType.NA,
            scores=scores,
            project_path="/path/to/project"
        )
        
        assert result.detected_framework == FrameworkType.NA
        assert result.detected_name == "Not Available"
        assert result.detected_framework_code == "na"
        assert result.is_framework_detected is False
        assert result.confidence_score == 0
    
    def test_top_frameworks_property(self):
        """Test top_frameworks property."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.CODEIGNITER: 5,
            FrameworkType.CAKEPHP: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        top_frameworks = result.top_frameworks
        # Should return all frameworks sorted by score (descending)
        assert len(top_frameworks) == 4
        framework_list = list(top_frameworks.keys())
        assert framework_list[0] == FrameworkType.LARAVEL
        assert framework_list[1] == FrameworkType.SYMFONY
        assert framework_list[2] == FrameworkType.CODEIGNITER
        assert framework_list[3] == FrameworkType.CAKEPHP
        
        assert top_frameworks[FrameworkType.LARAVEL] == 95
        assert top_frameworks[FrameworkType.SYMFONY] == 20
        assert top_frameworks[FrameworkType.CODEIGNITER] == 5
        assert top_frameworks[FrameworkType.CAKEPHP] == 0
    
    def test_top_frameworks_with_limit(self):
        """Test top_frameworks property with custom limit."""
        scores = {
            FrameworkType.LARAVEL: 95,
            FrameworkType.SYMFONY: 20,
            FrameworkType.CODEIGNITER: 5,
            FrameworkType.CAKEPHP: 0
        }
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        # Test with limit=2
        top_frameworks = result.top_frameworks(limit=2)
        assert len(top_frameworks) == 2
        framework_list = list(top_frameworks.keys())
        assert framework_list[0] == FrameworkType.LARAVEL
        assert framework_list[1] == FrameworkType.SYMFONY
    
    def test_custom_detection_time(self):
        """Test DetectionResult with custom detection time."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        scores = {FrameworkType.LARAVEL: 95}
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project",
            detection_time=custom_time
        )
        
        assert result.detection_time == custom_time
    
    def test_total_frameworks(self):
        """Test DetectionResult with total_frameworks."""
        scores = {FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20}
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project",
            total_frameworks=15
        )
        
        assert result.total_frameworks == 15


class TestModelIntegration:
    """Test integration between different models."""
    
    def test_framework_info_from_detection_result(self):
        """Test creating FrameworkInfo from DetectionResult."""
        scores = {FrameworkType.LARAVEL: 95}
        
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores=scores,
            project_path="/path/to/project"
        )
        
        info = FrameworkInfo(
            framework_type=result.detected_framework,
            confidence=result.confidence_score
        )
        
        assert info.framework_type == FrameworkType.LARAVEL
        assert info.confidence == 95
        assert info.name == "Laravel"
    
    def test_metadata_from_framework_info(self):
        """Test creating FrameworkMetadata from FrameworkInfo."""
        info = FrameworkInfo(
            framework_type=FrameworkType.LARAVEL,
            version="10.0.0",
            confidence=95
        )
        
        metadata = FrameworkMetadata(
            framework_type=info.framework_type,
            detection_methods=["file_patterns"],
            file_patterns=["artisan"]
        )
        
        assert metadata.framework_type == info.framework_type
        assert metadata.framework_code == info.code 


class TestPydanticV2Migration:
    """Test Pydantic V2 migration - field validators and model validators."""
    
    def test_framework_info_field_validator(self):
        """Test FrameworkInfo field validators work correctly."""
        # Test confidence validation
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=95)
        assert info.confidence == 95
        
        # Test confidence validation boundary values
        info_min = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=0)
        assert info_min.confidence == 0
        
        info_max = FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=100)
        assert info_max.confidence == 100
    
    def test_framework_info_confidence_validation_errors(self):
        """Test FrameworkInfo confidence validation raises appropriate errors."""
        # Test confidence below minimum
        with pytest.raises(ValidationError) as exc_info:
            FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
        
        # Test confidence above maximum  
        with pytest.raises(ValidationError) as exc_info:
            FrameworkInfo(framework_type=FrameworkType.LARAVEL, confidence=101)
        assert "Input should be less than or equal to 100" in str(exc_info.value)
    
    def test_framework_info_model_validator_auto_fields(self):
        """Test FrameworkInfo model validator automatically sets name and description."""
        # Test with only framework_type provided
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL)
        assert info.name == "Laravel"
        assert info.description == "Modern PHP web application framework with elegant syntax"
        
        # Test with different framework types
        info_symfony = FrameworkInfo(framework_type=FrameworkType.SYMFONY)
        assert info_symfony.name == "Symfony"
        assert info_symfony.description == "High-performance PHP framework for web development"
        
        info_na = FrameworkInfo(framework_type=FrameworkType.NA)
        assert info_na.name == "Not Available"
        assert info_na.description == "No framework detected or not available"
    
    def test_framework_info_manual_name_description_override(self):
        """Test FrameworkInfo respects manually provided name and description."""
        # Test custom name and description override automatic values
        info = FrameworkInfo(
            framework_type=FrameworkType.LARAVEL,
            name="Custom Laravel",
            description="Custom Laravel description"
        )
        assert info.name == "Custom Laravel"
        assert info.description == "Custom Laravel description"
    
    def test_detection_result_model_validator_auto_name(self):
        """Test DetectionResult model validator automatically sets detected_name."""
        # Test with only detected_framework provided
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            scores={FrameworkType.LARAVEL: 95, FrameworkType.SYMFONY: 20},
            project_path="/test/path"
        )
        assert result.detected_name == "Laravel"
        
        # Test with different framework types
        result_symfony = DetectionResult(
            detected_framework=FrameworkType.SYMFONY,
            scores={FrameworkType.SYMFONY: 85},
            project_path="/test/path"
        )
        assert result_symfony.detected_name == "Symfony"
        
        # Test with NA framework
        result_na = DetectionResult(
            detected_framework=FrameworkType.NA,
            scores={FrameworkType.NA: 0},
            project_path="/test/path"
        )
        assert result_na.detected_name == "Not Available"
    
    def test_detection_result_manual_detected_name_override(self):
        """Test DetectionResult respects manually provided detected_name."""
        result = DetectionResult(
            detected_framework=FrameworkType.LARAVEL,
            detected_name="Custom Laravel Name",
            scores={FrameworkType.LARAVEL: 95},
            project_path="/test/path"
        )
        assert result.detected_name == "Custom Laravel Name"
    
    def test_detection_config_max_file_size_validator(self):
        """Test DetectionConfig max_file_size field validator."""
        # Test valid file size
        config = DetectionConfig(max_file_size=2048000)
        assert config.max_file_size == 2048000
        
        # Test minimum boundary
        config_min = DetectionConfig(max_file_size=1024)
        assert config_min.max_file_size == 1024
        
        # Test maximum boundary (100MB)
        config_max = DetectionConfig(max_file_size=100 * 1024 * 1024)
        assert config_max.max_file_size == 100 * 1024 * 1024
    
    def test_detection_config_max_file_size_validation_errors(self):
        """Test DetectionConfig max_file_size validation raises appropriate errors."""
        # Test file size below minimum
        with pytest.raises(ValidationError) as exc_info:
            DetectionConfig(max_file_size=512)
        assert "Input should be greater than or equal to 1024" in str(exc_info.value)
        
        # Test file size above maximum
        with pytest.raises(ValidationError) as exc_info:
            DetectionConfig(max_file_size=101 * 1024 * 1024)  # 101MB
        assert "Max file size cannot exceed 100MB" in str(exc_info.value)
    
    def test_multiple_framework_types_auto_fields(self):
        """Test model validators work correctly with multiple framework types."""
        framework_types = [
            FrameworkType.LARAVEL,
            FrameworkType.SYMFONY,
            FrameworkType.CODEIGNITER,
            FrameworkType.SLIM,
            FrameworkType.DRUPAL,
            FrameworkType.NA
        ]
        
        for ft in framework_types:
            # Test FrameworkInfo
            info = FrameworkInfo(framework_type=ft)
            assert info.name == ft.display_name
            assert info.description == ft.description
            
            # Test DetectionResult
            result = DetectionResult(
                detected_framework=ft,
                scores={ft: 85},
                project_path="/test/path"
            )
            assert result.detected_name == ft.display_name
    
    def test_backward_compatibility_properties(self):
        """Test that backward compatibility properties still work after migration."""
        # Test FrameworkInfo.code property
        info = FrameworkInfo(framework_type=FrameworkType.LARAVEL)
        assert info.code == "laravel"
        
        # Test DetectionResult.detected_framework_code property
        result = DetectionResult(
            detected_framework=FrameworkType.SYMFONY,
            scores={FrameworkType.SYMFONY: 90},
            project_path="/test/path"
        )
        assert result.detected_framework_code == "symfony" 