# Use the official Python 3.9 slim image as the base
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code into the container
COPY . .

# Set the default command to run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]