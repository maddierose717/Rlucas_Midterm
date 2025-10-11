import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")


def test_calculator_init_with_load_history_failure():
    """Test calculator initialization when load_history fails."""
    from app.calculator import Calculator
    from app.calculator_config import CalculatorConfig
    from unittest.mock import patch
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = CalculatorConfig(base_dir=Path(tmpdir))
        
        # Make load_history raise an exception during init
        with patch.object(Calculator, 'load_history') as mock_load:
            mock_load.side_effect = Exception("Failed to load")
            
            # This should trigger lines 77-79
            calc = Calculator(config)
            
            # Calculator should still initialize despite load failure
            assert calc is not None
            assert calc.history == []

def test_calculator_logging_setup_failure():
    """Test calculator when logging setup fails."""
    from app.calculator import Calculator
    from app.calculator_config import CalculatorConfig
    from unittest.mock import patch
    from pathlib import Path
    import tempfile
    import pytest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = CalculatorConfig(base_dir=Path(tmpdir))
        
        # Make logging.basicConfig raise an exception
        with patch('logging.basicConfig') as mock_logging:
            mock_logging.side_effect = Exception("Logging setup failed")
            
            # This should trigger lines 103-106 and re-raise
            with pytest.raises(Exception) as exc_info:
                calc = Calculator(config)
            
            assert "Logging setup failed" in str(exc_info.value)



def test_calculator_history_max_size():
    """Test that history removes oldest entry when max size exceeded."""
    from app.calculator import Calculator
    from app.calculator_config import CalculatorConfig
    from app.operations import OperationFactory
    from pathlib import Path
    from decimal import Decimal
    import tempfile
    from unittest.mock import patch
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config with small max_history_size
        config = CalculatorConfig(base_dir=Path(tmpdir))
        config.max_history_size = 2  # Set small limit
        
        # Prevent loading existing history
        with patch.object(Calculator, 'load_history'):
            calc = Calculator(config)
        
        # Add operations to exceed limit
        operation = OperationFactory.create_operation('add')
        calc.set_operation(operation)
        
        calc.perform_operation("1", "1")  # First calculation
        calc.perform_operation("2", "2")  # Second calculation
        calc.perform_operation("3", "3")  # Third - should trigger pop
        
        # Should only have 2 items (oldest removed)
        assert len(calc.history) == 2
        # First calculation should be removed
        assert calc.history[0].operand1 == Decimal("2")
        assert calc.history[1].operand1 == Decimal("3")

def test_calculator_operation_unexpected_error():
    """Test calculator handles unexpected errors during operation."""
    from app.calculator import Calculator
    from app.calculator_config import CalculatorConfig
    from app.operations import OperationFactory
    from app.exceptions import OperationError
    from pathlib import Path
    from unittest.mock import patch
    import tempfile
    import pytest
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = CalculatorConfig(base_dir=Path(tmpdir))
        
        with patch.object(Calculator, 'load_history'):
            calc = Calculator(config)
        
        # Set up operation
        operation = OperationFactory.create_operation('add')
        
        # Make the operation's execute method raise unexpected error
        with patch.object(operation, 'execute') as mock_execute:
            mock_execute.side_effect = RuntimeError("Unexpected error")
            
            calc.set_operation(operation)
            
            # Should catch and re-raise as OperationError
            with pytest.raises(OperationError) as exc_info:
                calc.perform_operation("5", "3")
            
            assert "Operation failed: Unexpected error" in str(exc_info.value)


def test_calculator_load_empty_history_file():
    """Test loading an empty history CSV file."""
    from app.calculator import Calculator
    from app.calculator_config import CalculatorConfig
    from pathlib import Path
    import tempfile
    import pandas as pd
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = CalculatorConfig(base_dir=Path(tmpdir))
        
        # Create the history directory first
        config.history_dir.mkdir(parents=True, exist_ok=True)
        history_file = config.history_file
        
        # Create an empty CSV with just headers
        empty_df = pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp'])
        empty_df.to_csv(history_file, index=False)
        
        # This should trigger line 305
        calc = Calculator(config)
        
        # History should be empty
        assert calc.history == []

def test_calculator_undo_redo_empty_stacks():
    """Test undo/redo when stacks are empty."""
    from app.calculator import Calculator
    from app.calculator_config import CalculatorConfig
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = CalculatorConfig(base_dir=Path(tmpdir))
        calc = Calculator(config)
        
        # Test undo with empty stack - line 371
        assert calc.undo() is False
        
        # Test redo with empty stack - line 390
        assert calc.redo() is False
