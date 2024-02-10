# Use the specific Python version
FROM python:3.10.2

# Set the working directory in the container
WORKDIR /app

# Copy the backend application files into the container
COPY .. /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI application using main.py
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--reload"]
