import pytest


def test_simple_pass():
    """簡單的通過測試"""
    assert True


if __name__ == "__main__":
    pytest.main([__file__])