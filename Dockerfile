# Use official Python 3.11 image
FROM python:3.11-slim

# Set environment variable for microservice path
ENV MICRO_SERVICE=/home/app/powercore-diagram-parser

# Create application directory
RUN mkdir -p $MICRO_SERVICE

# Set working directory
WORKDIR $MICRO_SERVICE

# Copy requirements file to container
COPY requirements.txt $MICRO_SERVICE

# Set environment variables for Python behavior
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update and upgrade system packages
RUN apt-get -y update
RUN apt-get -y upgrade
RUN pip install --upgrade pip

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . $MICRO_SERVICE


