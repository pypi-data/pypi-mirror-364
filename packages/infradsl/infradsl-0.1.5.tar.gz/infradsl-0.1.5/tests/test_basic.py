"""
Basic test to ensure deployment can proceed
"""

def test_basic_import():
    """Test that basic imports work"""
    from infradsl import AWS, GCP
    assert AWS is not None
    assert GCP is not None

def test_version_available():
    """Test that version is accessible"""
    from infradsl.cli.main import __version__
    assert __version__ == "0.1.5"

def test_math_works():
    """Basic sanity check"""
    assert 1 + 1 == 2