# CollectionFC

A simple collection forecasting library for Python.

## Features
- 7x7 transition matrix estimation
- 12-month cash-flow forecast
- Basic accuracy diagnostics
- CLI interface for easy use

## Usage

### Install (development mode)
```bash
pip install -e .
```

### Run simple mode
```bash
python -m collection_fc --mode simple --input ledger.csv
```

Optional output paths:
```bash
python -m collection_fc --mode simple \
    --input raw/ledger_may25.csv \
    --forecast_path out/fc.csv \
    --matrix_path out/P.csv \
    --validation_path out/val.json
```

See `simple_collection_forecasting_library.md` for full documentation.
