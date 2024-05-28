# Use the official Python image as the base image
FROM mcr.microsoft.com/playwright:focal

RUN apt-get update && apt-get install -y python3-pip

# Set the working directory within the container
WORKDIR /srv

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the requirements file into the container
COPY . /srv





# Expose the port that the FastAPI app will run on
EXPOSE 8000

# Start the FastAPI app using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0","--workers","1", "--port", "8000"]
