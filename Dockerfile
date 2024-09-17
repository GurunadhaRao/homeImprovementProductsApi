FROM python:3.9-slim

# Set up a virtual environment path
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Set the working directory
WORKDIR /app

# Copy the project files to the container
COPY . /app

# Install virtual environment, upgrade pip, and install dependencies
RUN python -m venv /env && \
pip install --upgrade pip && \
pip install -r requirements.txt

# Expose the port the app will run on
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]