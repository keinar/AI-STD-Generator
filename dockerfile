# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_SERVER_ADDRESS=0.0.0.0

# Run the app
CMD ["streamlit", "run", "ai_std_generator.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# To build and run:
# 1. docker build -t ai-std-generator:latest .
# 2. docker run -p 8501:8501 --env-file .env ai-std-generator:latest
