FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files  
COPY app.py .
COPY forecast.py .

# Copy models directory (unified model)
COPY model/ ./model/

# Expose the port that FastAPI will run on
EXPOSE 7860

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]

