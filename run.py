
import argparse
import yaml
import pandas as pd
import numpy as np
import json
import logging
import time
import sys
import os
import io

def setup_logger(log_file):
    """Configures the Python logger to write to the specified file."""
    logger = logging.getLogger('MLOpsTask')
    logger.setLevel(logging.INFO)
    
    # Ensure we don't add multiple handlers if run multiple times in a notebook
    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

def write_metrics(output_path, metrics_data):
    """Writes the structured metrics dictionary to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(metrics_data, f, indent=4)

def main():
    # Start the timer for latency tracking
    start_time = time.time()
    
    # 1. Command Line Interface (CLI)
    parser = argparse.ArgumentParser(description="MLOps Batch Job - Signal Generator")
    parser.add_argument('--input', required=True, help="Path to input data.csv")
    parser.add_argument('--config', required=True, help="Path to config.yaml")
    parser.add_argument('--output', required=True, help="Path to output metrics.json")
    parser.add_argument('--log-file', required=True, dest='log_file', help="Path to run.log")
    args = parser.parse_args()
    
    # Initialize logger
    logger = setup_logger(args.log_file)
    logger.info("Job started.")
    
    version = "unknown" # Default fallback in case config loading fails
    
    try:
        # 2. Configuration Validation
        logger.info(f"Loading config from {args.config}...")
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file not found at {args.config}")
            
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            
        if not config:
            raise ValueError("Config file is empty or invalid.")
            
        required_keys = ['seed', 'window', 'version']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: '{key}'")
                
        seed = config['seed']
        window = config['window']
        version = config['version']
        
        logger.info(f"Config validated. Version: {version}, Window: {window}, Seed: {seed}")
        
        # Set deterministic mathematical seed
        np.random.seed(seed)
        
        # 3. Data Validation & Loading
        logger.info(f"Loading dataset from {args.input}...")
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found at {args.input}")
        with open(args.input, 'r') as file:
            raw_text = file.read()
        clean_text = raw_text.replace('"', '')
        
        try:
            df = pd.read_csv(io.StringIO(clean_text))
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {e}")
            
        if df.empty:
            raise ValueError("Input CSV is empty.")
            
        if 'close' not in df.columns:
            raise ValueError("Missing required column: 'close'")
            
        # Ensure 'close' is strictly numeric
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        if df['close'].isna().all():
            raise ValueError("Column 'close' contains no readable numeric data.")
            
        rows_loaded = len(df)
        logger.info(f"Dataset loaded successfully. Rows: {rows_loaded}")
        
        logger.info("Computing rolling mean and generating signals...")
        
        df['rolling_mean'] = df['close'].rolling(window=window).mean()
        
        rolling_mean_filled = df['rolling_mean'].fillna(float(0.0))
        
        df['signal'] = np.where(df['close'] > rolling_mean_filled, 1, 0)
        
        # 5. Metrics Calculation
        logger.info("Calculating metrics...")
        rows_processed = len(df)
        signal_rate = float(df['signal'].mean())
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Success Output Structure
        success_metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        
        write_metrics(args.output, success_metrics)
        logger.info(f"Metrics written to {args.output}. Job completed successfully.")
        
        # Exit cleanly (Required for Docker success)
        sys.exit(0)
        
    except Exception as e:
        # 6. Error Handling
        error_msg = str(e)
        logger.error(f"Job failed with error: {error_msg}")
        
        # Error Output Structure
        error_metrics = {
            "version": version,
            "status": "error",
            "error_message": error_msg
        }
        
        # Write error metrics even if the job fails
        write_metrics(args.output, error_metrics)
        
        # Exit with error code (Required for Docker failure)
        sys.exit(1)

if __name__ == "__main__":
    main()



