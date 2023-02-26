# Use an official Python 3.9.7 image as the base image
FROM python:3.9.7

# Set the working directory in the container to /app
WORKDIR /app

# Copy the local requirements.txt file into the container at /app/requirements.txt
COPY requirements.txt /app/requirements.txt

# Install the dependencies listed in the requirements.txt file
RUN pip3 install -r requirements.txt

# Install html to pdf external library
Run apt-get install wkhtmltopdf

# Copy the local app.py and datarequester.py files into the container at /app
COPY app.py /app/app.py
COPY data_requests.py /app/data_requests.py

# Copy the local tests folder into the container at /app/tests
COPY tests /app/tests

# Expose the default Streamlit port 8501
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the command "python app.py" when the container starts
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

