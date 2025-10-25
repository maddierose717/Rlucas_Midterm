Madison Rose Lucas - Midterm
## Setup
1. Create virtual environment: `uv venv venv`
2. Activate: `source venv/bin/activate`
3. Install dependencies: `uv pip install -r requirements.txt`
4. Configure: Copy `.env.example` to `.env` (or use provided `.env`)
5. Run: `python main.py`

## Operations Supported
- Basic: Addition, Subtraction, Multiplication, Division
- Advanced: Power, Root, Modulus, IntegerDivision
- Special: Percentage, AbsoluteDifference

## Test Coverage
Run tests: `pytest tests/ --cov=app --cov-report=term-missing`
Current coverage: 96%
