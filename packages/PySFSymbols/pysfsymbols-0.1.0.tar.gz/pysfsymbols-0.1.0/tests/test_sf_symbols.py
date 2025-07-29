from src import pysfsymbols

def test_fetch_symbol():
    """Test fetching a specific SF Symbol."""
    symbol_name = "person"
    assert pysfsymbols.fetch_symbol(symbol_name) == "\U00100269"

def test_fetch_all_symbols():
    """Test fetching all SF Symbols."""
    symbols = pysfsymbols.fetch_all_symbols()
    assert isinstance(symbols, list)
    assert len(symbols) > 0
    assert all(isinstance(symbol, str) for symbol in symbols)

def test_fetch_all_names():
    """Test fetching all SF Symbol names."""
    names = pysfsymbols.fetch_all_names()
    assert isinstance(names, list)
    assert len(names) > 0
    assert all(isinstance(name, str) for name in names)

def test_fetch_all():
    """Test fetching all SF Symbols and their names."""
    all_symbols = pysfsymbols.fetch_all()
    assert isinstance(all_symbols, dict)
    assert len(all_symbols) > 0
    assert all(isinstance(name, str) for name in all_symbols.keys())
    assert all(isinstance(symbol, str) for symbol in all_symbols.values())
