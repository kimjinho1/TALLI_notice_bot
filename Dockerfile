# Use the official Python image as the base image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python packages
RUN pip install -r requirements.txt

# Copy your Python script into the container
COPY src .

# Run your Python script (replace "your_script.py" with your actual script name)
CMD ["python", "src/main.py"]