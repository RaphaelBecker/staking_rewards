# Use an official Python 3.9.7 image as the base image
FROM python:3.9.7

# Set the working directory in the container to /app
WORKDIR /app

# Copy the local requirements.txt file into the container at /app/requirements.txt
COPY requirements.txt /app/requirements.txt

# Install the dependencies listed in the requirements.txt file
RUN pip install -r requirements.txt

# Copy the local app.py and datarequester.py files into the container at /app
COPY app.py /app/app.py
COPY data_requester.py /app/data_requester.py

# Copy the local tests folder into the container at /app/tests
COPY tests /app/tests


# Run the command "python app.py" when the container starts
CMD ["streamlit", "run", "app.py"]

