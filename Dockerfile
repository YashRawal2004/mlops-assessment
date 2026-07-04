# Use the suggested base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the required application files into the container
COPY run.py config.yaml data.csv ./

# Command to execute the script, print the metrics, and preserve the exit code
# This strictly satisfies the requirement to output metrics to stdout on both success and failure
CMD python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log ; \
    EXIT_CODE=$? ; \
    if [ -f metrics.json ]; then cat metrics.json; fi ; \
    exit $EXIT_CODE