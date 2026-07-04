# MLOps Batch Job - Signal Generator

This repository contains a lightweight, production-ready MLOps batch job pipeline designed to process historical financial data, calculate rolling averages, generate trading signals, and export metrics for monitoring. It includes full input validation, configuration control, error handling, dockerization, and logging.

---

## Codebase Overview

Here is a guide to the project files:

*   **[run.py]**: The main execution script. Key functions include:
    *   `[setup_logger]`: Configures the execution logging behavior.
    *   `[write_metrics]`: Standardizes metrics output structure to JSON.
    *   `[main]`: Orchestrates the batch workflow (configuration loading, raw data cleaning, signal generation, metrics calculation, and robust error handling).
*   **[config.yaml]**: Controls parameters like random seed, rolling window size, and app version.
*   **[data.csv]**: Input CSV containing raw Bitcoin transaction/ohlc metrics.
*   **[Dockerfile]**: Docker container configuration for packaging and running the batch job.
*   **[requirements.txt]**: Python package dependencies (`numpy`, `pandas`, `PyYAML`).
*   **[main.ipynb]**: Jupyter notebook used for prototyping, exploration, and step-by-step logic development.
*   **[error_datasets]**: Collection of invalid/malformed datasets used to verify error handling and robust performance.

---

## Features

1.  **Configuration Management**: Centralized parameters via `config.yaml` with required-key checks.
2.  **Data Sanitization**: Automatically strips redundant double quotes from the raw CSV input before parsing.
3.  **Signal Generation**: Computes rolling mean of the asset's closing price and signals `1` when the closing price exceeds the rolling mean, or `0` otherwise.
4.  **Logging**: All steps, successes, warning parameters, and errors are recorded sequentially to a run log.
5.  **Metrics Export**: Generates structural JSON metrics (containing version, rows processed, latency, seed, status, etc.) on both successful executions and runtime failures.
6.  **Dockerized Execution**: Standardized runtime environment using Docker, with automated exit-code preservation and stdout outputting of execution metrics.

---

## Getting Started

### Local Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution

#### Running the Script Locally
Run the batch job command-line interface:
```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

#### Arguments
*   `--input`: Path to raw CSV input data file.
*   `--config`: Path to config YAML file.
*   `--output`: Output path for the generated metrics JSON.
*   `--log-file`: Output path for runtime logs.

---

## Docker Usage

The batch pipeline is fully dockerized to ensure clean, isolated runs.

### 1. Build the Docker Image
```bash
docker build -t mlops-signal-generator .
```

### 2. Run the Docker Container
```bash
docker run --rm mlops-signal-generator
```

*Note: The container runs the batch job, outputs the generated metrics JSON to stdout, and exits with code `0` on success or `1` on error.*

---

## Robust Error Validation

The script checks for common data failures and reports metrics with a `"status": "error"` indicator. You can test validation scenarios using files from the **[error_datasets]** directory:

*   **`empty.csv`**: Tests behavior with empty input files.
*   **`corrupted.csv`**: Tests behavior with malformed or un-parsable CSV records.
*   **`missing_close.csv`**: Tests behavior when the mandatory `close` price column is absent.

Example command for testing error handling:
```bash
python run.py --input error_datasets/missing_close.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Sample Outputs

### Success Case (`metrics.json`)
```json
{
    "version": "v2",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.4963,
    "latency_ms": 37,
    "seed": 101,
    "status": "success"
}
```

### Failure Case (`metrics.json`)
```json
{
    "version": "v2",
    "status": "error",
    "error_message": "Missing required column: 'close'"
}
```
