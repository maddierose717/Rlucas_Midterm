

def test_memento_with_actual_calculations():
    """Test memento to_dict and from_dict with real calculations."""
    from app.calculation import Calculation
    from app.calculator_memento import CalculatorMemento
    from decimal import Decimal
    
    # Create actual calculations with operation strings
    calc1 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("2"))
    
    # Create memento with history
    memento = CalculatorMemento(history=[calc1, calc2])
    
    # Test to_dict - this will execute line 34 (return {)
    dict_data = memento.to_dict()
    assert 'history' in dict_data
    assert 'timestamp' in dict_data
    assert len(dict_data['history']) == 2
    assert dict_data['history'][0]['operation'] == 'Addition'
    assert dict_data['history'][1]['operation'] == 'Multiplication'
    
    # Test from_dict - this will execute line 53 (return cls)
    restored_memento = CalculatorMemento.from_dict(dict_data)
    assert len(restored_memento.history) == 2
    assert restored_memento.history[0].operation == 'Addition'
    assert restored_memento.history[1].operation == 'Multiplication'
    assert restored_memento.history[0].operand1 == Decimal("5")
