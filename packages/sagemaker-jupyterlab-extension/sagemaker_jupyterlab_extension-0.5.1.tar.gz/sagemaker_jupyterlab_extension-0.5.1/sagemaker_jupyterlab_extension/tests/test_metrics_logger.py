import pytest
import json
import os
from unittest.mock import patch, mock_open
from ..utils.metrics_logger import MetricsLogger


@pytest.fixture
def metrics_logger_instance():
    with patch("os.makedirs"):
        yield MetricsLogger("/tmp/test_metrics.log")


def test_metrics_logger_init():
    # Test default initialization
    with patch("os.makedirs") as mock_makedirs:
        logger = MetricsLogger()
        assert (
            logger.log_file_path
            == "/var/log/studio/jupyterlab/sm-jupyterlab-ext.ui.log"
        )
        mock_makedirs.assert_called_once_with(
            "/var/log/studio/jupyterlab", exist_ok=True
        )

    # Test custom path initialization
    with patch("os.makedirs") as mock_makedirs:
        custom_path = "/custom/path/metrics.log"
        logger = MetricsLogger(custom_path)
        assert logger.log_file_path == custom_path
        mock_makedirs.assert_called_once_with("/custom/path", exist_ok=True)

    # Test initialization with error (should not crash)
    with patch("os.makedirs", side_effect=Exception("Test error")):
        logger = MetricsLogger()  # Should complete without raising


def test_log_metric_success(metrics_logger_instance):
    valid_json = '{"metric": "test", "value": 1}'

    with patch("builtins.open", mock_open()) as mock_file:
        result = metrics_logger_instance.log_metric(valid_json)
        assert result is True
        mock_file.assert_called_once_with("/tmp/test_metrics.log", "a")
        mock_file().write.assert_called_once_with(f"{valid_json}\n")


def test_log_metric_invalid_json(metrics_logger_instance):
    invalid_json = "{metric: test, value: 1}"

    with patch("builtins.open", mock_open()) as mock_file:
        result = metrics_logger_instance.log_metric(invalid_json)
        assert result is True  # Still writes to file
        mock_file().write.assert_called_once_with(f"{invalid_json}\n")


def test_log_metric_non_string_input(metrics_logger_instance):
    non_string_input = {"metric": "test", "value": 1}

    with patch("builtins.open", mock_open()) as mock_file:
        result = metrics_logger_instance.log_metric(non_string_input)
        assert result is True
        mock_file().write.assert_called_once_with(f"{non_string_input}\n")


def test_log_metric_file_error(metrics_logger_instance):
    valid_json = '{"metric": "test", "value": 1}'

    with patch("builtins.open", side_effect=Exception("Test error")):
        result = metrics_logger_instance.log_metric(valid_json)
        assert result is False


def test_log_metric_json_decode_error():
    """Test JSON decode error path with string input"""
    with patch("os.makedirs"):
        logger = MetricsLogger("/tmp/test.log")

    invalid_json_string = "not valid json at all"
    with patch("builtins.open", mock_open()):
        with patch("json.loads", side_effect=json.JSONDecodeError("test", "doc", 0)):
            result = logger.log_metric(invalid_json_string)
            assert result is True


def test_makedirs_error_handling():
    """Test makedirs exception triggers error code path"""
    with patch("os.makedirs", side_effect=OSError("Permission denied")):
        logger = MetricsLogger("/restricted/path/test.log")
        assert logger.log_file_path == "/restricted/path/test.log"


def test_log_metric_empty_string():
    """Test logging empty string"""
    with patch("os.makedirs"):
        logger = MetricsLogger("/tmp/test.log")

    with patch("builtins.open", mock_open()) as mock_file:
        result = logger.log_metric("")
        assert result is True
        mock_file().write.assert_called_once_with("\n")


def test_log_metric_list_input():
    """Test logging list input"""
    with patch("os.makedirs"):
        logger = MetricsLogger("/tmp/test.log")

    test_list = [1, 2, 3]
    with patch("builtins.open", mock_open()) as mock_file:
        result = logger.log_metric(test_list)
        assert result is True
        mock_file().write.assert_called_once_with(f"{test_list}\n")


def test_log_metric_valid_json_array():
    """Test logging valid JSON array string"""
    with patch("os.makedirs"):
        logger = MetricsLogger("/tmp/test.log")

    valid_json_array = '[{"metric": "test1"}, {"metric": "test2"}]'
    with patch("builtins.open", mock_open()) as mock_file:
        result = logger.log_metric(valid_json_array)
        assert result is True
        mock_file().write.assert_called_once_with(f"{valid_json_array}\n")
