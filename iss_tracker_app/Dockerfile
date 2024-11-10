# 1. Use an official Python runtime as a parent image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app
#WORKDIR /app/iss_tracker_app

# 4. Install system dependencies for PostgreSQL and other necessary tools
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy the current project into the container
COPY .. /app/
#COPY ./iss_tracker_app /app/iss_tracker_app

# 7. Expose the port that the Django app will run on
EXPOSE 8000

# 8. Command to run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


