"""Tests for calculator REPL module."""

def test_repl_module_imports():
    """Test that the REPL module can be imported."""
    from app import calculator_repl
    assert calculator_repl is not None
    
def test_repl_function_exists():
    """Test that calculator_repl function exists."""
    from app.calculator_repl import calculator_repl
    assert callable(calculator_repl)

def test_repl_has_docstring():
    """Test that calculator_repl has proper documentation."""
    from app.calculator_repl import calculator_repl
    assert calculator_repl.__doc__ is not None
    assert "REPL" in calculator_repl.__doc__
