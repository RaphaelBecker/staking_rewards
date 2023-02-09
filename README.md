# staking_rewards
Streamlit app to visualize and calcultate the staking rewards received by kraken csv file over time



# Python App with SQLite Database

This is a sample Python application with a SQLite database, packaged as a Docker image.


## Installation with Docker

To install the app using Docker, follow these steps:

1. Clone the repository:
```git clone https://github.com/RaphaelBecker/staking_rewards.git```
2. Change to the project directory:
```cd staking_rewards```
3. Build the Docker image:
```docker build -t staking_rewards .```
    * Note the ```.``` at the end of the command - it specifies the build context, which is the current directory in this case.
4. Run the Docker image:
```docker run -p 5000:5000 staking_rewards```
5. Access the application in your web browser at `http://localhost:5000`.


## Installation on Windows 10
To install the app using batch scripts on Windows 10, follow these steps:
1. Run install script by double click ```setup.bat```
2. Run app by double click ```start_app.bat```
3. App should appear in browser on local URL: ```http://localhost:8501```

## License
This project is licensed under the [MIT License](LICENSE).

