# staking_rewards
Streamlit app to visualize and calcultate the staking rewards received by kraken csv file over a chosen time.
How To:
1. Export your ledger.csv file from Kraken
2. Start app and drop the ledger.csv file to the upload field 


## Requirements
1. on Mac OS: Docker is mandatory
2. on Windows: Docker is optional
3. Only Kraken ledgers CSV fiel supported 
Only on Windows:
4. PdfKit installed: https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf
   * After installation and adding to PATH + restart of OS, verify if module can be found in cmd:
     * ```where wkhtmltopdf```


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
```docker run -p 8501:8501 staking_rewards```
5. Access the application in your web browser at `http://localhost:8501/`.


## Installation on Windows 10
To install the app using batch scripts on Windows 10, follow these steps:
1. Run install script by double click ```setup.bat```
2. Run app by double click ```start_app.bat```
3. App should appear in browser on local URL: ```http://localhost:8501```


## License
This project is licensed under the [MIT License](https://github.com/RaphaelBecker/staking_rewards/blob/main/LICENCE.md).


## Preview:

<img align="center" height="700px" src="https://github.com/RaphaelBecker/staking_rewards/blob/main/previews/preview.gif">  
