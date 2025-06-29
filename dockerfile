FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY backend/requirements.txt .

# Create a compatible requirements file
RUN echo "setuptools>=68.0.0" >> requirements.txt.compatible && \
    echo "wheel>=0.40.0" >> requirements.txt.compatible && \
    cat requirements.txt | sed 's/numpy==1.24.4/numpy>=1.25.0/g' | \
    sed 's/aiohttp==3.8.5/aiohttp>=3.8.6/g' | \
    sed 's/pydantic-ai==0.0.32/pydantic-ai>=0.0.32/g' | \
    sed 's/langchain==0.0.312/langchain>=0.0.312/g' >> requirements.txt.compatible

# Install dependencies from the compatible requirements file
RUN pip install --upgrade --prefer-binary --no-cache-dir -r requirements.txt -c constraints.txt

# Copy the rest of the application
COPY backend/ .

# Expose port for the application
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]