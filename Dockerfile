# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to prevent generating .pyc files and to run Python unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Specify the command to run on container start using gunicorn
CMD ["gunicorn", "alemethod.wsgi:application", "--bind", "0.0.0.0:8000"]