# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./books_list_fetcher.py .
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV LITRES_BOOKS_COUNT_LIMIT=2000

# Run the Python script when the container launches
CMD ["python", "./books_list_fetcher.py"]
