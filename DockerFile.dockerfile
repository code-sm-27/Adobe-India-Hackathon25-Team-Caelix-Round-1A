# Use a slim, official Python image
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application script
COPY round-1a.py .

# Set the command to run when the container starts
CMD ["python", "round-1a.py"]