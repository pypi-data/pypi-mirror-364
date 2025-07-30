"""
Basic tests for School of Prompt core functionality.
"""

import pandas as pd
import pytest

from school_of_prompt import optimize
from school_of_prompt.core.config import FrameworkConfig
from school_of_prompt.data.registry import get_data_registry


class TestBasicFunctionality:
    """Test basic framework functionality."""

    def test_import(self):
        """Test that the package can be imported."""
        import school_of_prompt

        assert hasattr(school_of_prompt, "optimize")
        assert hasattr(school_of_prompt, "__version__")

    def test_version(self):
        """Test that version is accessible."""
        import school_of_prompt

        version = school_of_prompt.__version__
        assert isinstance(version, str)
        assert len(version.split(".")) >= 2  # At least major.minor

    def test_optimize_with_sample_data(self):
        """Test optimize function with sample data."""
        # Create sample data
        sample_data = [
            {"text": "This is great!", "label": "positive"},
            {"text": "This is bad!", "label": "negative"},
            {"text": "This is okay", "label": "neutral"},
        ]

        # Simple optimization test (without API calls)
        try:
            results = optimize(
                data=sample_data,
                task="classify sentiment",
                prompts=["Classify: {text}", "Sentiment: {text}"],
                api_key="test_key",  # Mock API key for testing
            )
            # If it runs without error, that's good enough for CI
            assert results is not None
        except Exception as e:
            # Expected to fail with mock API key, but should not crash
            assert "api" in str(e).lower() or "key" in str(e).lower()


class TestDataRegistry:
    """Test data source registry functionality."""

    def test_registry_creation(self):
        """Test that data registry can be created."""
        registry = get_data_registry()
        assert registry is not None

    def test_built_in_sources(self):
        """Test that built-in data sources are registered."""
        registry = get_data_registry()
        sources = registry.list_sources()

        expected_sources = ["csv", "jsonl", "pandas", "youtube", "reddit"]
        for source in expected_sources:
            assert source in sources

    def test_built_in_enrichers(self):
        """Test that built-in enrichers are registered."""
        registry = get_data_registry()
        enrichers = registry.list_enrichers()

        expected_enrichers = [
            "text_length",
            "word_count",
            "sentiment_features",
            "readability",
        ]
        for enricher in expected_enrichers:
            assert enricher in enrichers

    def test_csv_data_source(self):
        """Test CSV data source."""
        import os
        import tempfile

        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("text,label\n")
            f.write("Hello,positive\n")
            f.write("Goodbye,negative\n")
            temp_path = f.name

        try:
            registry = get_data_registry()
            csv_source = registry.get_source("csv", path=temp_path)
            data = csv_source.load()

            assert len(data) == 2
            assert data[0]["text"] == "Hello"
            assert data[0]["label"] == "positive"
        finally:
            os.unlink(temp_path)

    def test_pandas_data_source(self):
        """Test pandas DataFrame data source."""
        df = pd.DataFrame(
            {"text": ["Hello", "Goodbye"], "label": ["positive", "negative"]}
        )

        registry = get_data_registry()
        pandas_source = registry.get_source("pandas", dataframe=df)
        data = pandas_source.load()

        assert len(data) == 2
        assert data[0]["text"] == "Hello"
        assert data[0]["label"] == "positive"


class TestConfiguration:
    """Test configuration system."""

    def test_config_creation(self):
        """Test that configuration can be created."""
        config = FrameworkConfig()
        assert config is not None

    def test_config_with_dict(self):
        """Test configuration with dictionary input."""
        config_dict = {
            "task": {"name": "test_task", "type": "classification"},
            "evaluation": {"metrics": ["accuracy"]},
        }

        config = FrameworkConfig(config_dict=config_dict)
        assert config.task_name == "test_task"
        assert config.task_type == "classification"
        assert "accuracy" in config.evaluation_metrics


class TestCaching:
    """Test caching functionality."""

    def test_api_cache_creation(self):
        """Test that API cache can be created."""
        from school_of_prompt.production.cache import IntelligentCache

        cache = IntelligentCache(cache_dir="test_cache", enabled=True)
        assert cache is not None
        assert cache.enabled is True

    def test_cached_api_source(self):
        """Test cached API data source."""
        registry = get_data_registry()

        # Test YouTube source with caching disabled for testing
        youtube_source = registry.get_source(
            "youtube",
            api_key="test_key",
            query="test",
            max_results=2,
            cache_enabled=False,  # Disable for testing
        )

        data = youtube_source._fetch_from_api()  # Call internal method
        assert len(data) == 2
        assert all("title" in item for item in data)


class TestMetrics:
    """Test metrics system."""

    def test_metrics_import(self):
        """Test that metrics can be imported."""
        from school_of_prompt.metrics.auto_metrics import get_metric_function

        # Test that basic metrics are available
        accuracy_fn = get_metric_function("accuracy")
        assert accuracy_fn is not None

        mae_fn = get_metric_function("mae")
        assert mae_fn is not None

    def test_tolerance_metrics(self):
        """Test tolerance-based metrics."""
        from school_of_prompt.metrics.auto_metrics import get_metric_function

        within_1_fn = get_metric_function("within_1")
        assert within_1_fn is not None

        # Test the metric
        predictions = [1, 2, 3, 4, 5]
        actuals = [1, 3, 2, 4, 6]  # Within 1 for most

        score = within_1_fn(predictions, actuals)
        assert 0 <= score <= 1  # Should be a percentage


if __name__ == "__main__":
    pytest.main([__file__])
