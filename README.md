# Standstill station

The Standstill station is an art-science installation that challenges you to move as little as possible! Users put on a pair of headphones and are asked to stand as still as possible for 40 seconds while listening to music and silence. The movements are tracked by a small gyro placed inside the headphones, and the movement data is displayed to the user on screen in real-time. After each trial, users can see how well they perform compared to all previous participants.

The exhibit was originally developed by Joachim Poutaraud, Julius Jacoby-Pflug, and Alexander Jensenius in 2023, as part of a collaboration between [RITMO Centre of Excellence](https://www.uio.no/ritmo/english/) at the University of Oslo and the [Popsenteret museum](https://www.popsenteret.no/) in downtown Oslo. In 2026, after Popsenteret sadly closed down, the installation was updated and re-vitalized at the[ Department of Musicology](https://www.hf.uio.no/imv/english/), at the University of Oslo, by Aleksander Tidemann.

[PICTURES]

This repo contains all software and official documentation for the Standstill station.

# System overview

The system consists of a large physical structure, a touchscreen computer, and a pair of headphones with a gyroscope. The headphones and gyro are connected to a bridge adapter that is connected to the computer via USB-A and mini-jack (3.5mm).

Software-wise, the standstill station requires three programs to run:

1. The main Python script (./main.py) that handles the UI, data, calculations, and database storage, etc.
2. A bridge application (./Bridgehead.exe) that converts and sends the 3D head-tracking data (XYZ) from the gyro to the main Python script via OSC.
3. A local SQL database for handling data.

[PICTURES]

# Installation

1. Download Python v3.11
2. Download SQL and initialize a server-client database.
3. Download Bridgehead v1.19
4. Open Terminal and run:

```
> cd PATH_TO_STANDSTILL_STATION_FOLDER
> pip install -r requirements.txt
```

# How to Run

1.  Plug the headphone ethernet cable into the adapter, and the adapter and mini-jack (3.5mm) into the computer. (The adapter might need a driver.)
2. Select Headphones as the speaker source in Windows audio settings.
3. Run the bridge application (```./Bridgehead.exe```) and ensure that the “Quaternion (composite)” profile is selected under settings. This ensures that the gyro data is sent from the brighead app to the Python script over OSC (port 8000).
5. Make sure the SQL server is running in the background.
6. Open the Terminal and run:

```
> cd PATH_TO_STANDSTILL_STATION_FOLDER
> python main.py
```

# Development

In our case, the gyro adapter is stuck to the physical constructions and is therefore unattainable for development and testing elsewhere. However, you can use a simple script I made that simulates XYZ head-tracking movements over OSC for development. This is the ```simulate_head_tracking_for_dev.py``` script located in the root folder. With this, there is no need for the adapter (gyro and headphones) or the Bridgehead application. Just run the OSC script, then the main Python script. 

Also, to check the database connection and make basic test queries, see the ```sql-cheatsheet.py``` script in the root folder.

# Database

The SQL database stores and retrieves data from the Standstill users. The server must be configured so that it runs in the background of the machine from boot. I just use SQL Workbench to set everything up. 

The database uses two table structures to store userdata, _standstillUser_ and _standstillRealTime_. Their schemas are as follows:

```
TABLE standstillUser 
(
id INT unsigned NOT NULL AUTO_INCREMENT,
standstillUserID INT unsigned,
age INT unsigned, 
language VARCHAR(2),
musicScore FLOAT, 
silenceScore FLOAT,
feedbackMusic INT unsigned,
feedbackStandstill INT unsigned,
PRIMARY KEY (id)
)
```

```
CREATE TABLE standstillRealTime 
(
id INT unsigned NOT NULL AUTO_INCREMENT,
standstillUserID INT unsigned,
genre VARCHAR(50),
date TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
w FLOAT(7,6) NOT NULL, 
PRIMARY KEY (id)  
)
```

All sensitive database info (usernames, passwords, etc,) is stored in a separate `config.yml``` file locally. See the ```config.example.yml``` file for info about how to set this up. Also, to check the database connection and make basic test queries, see the ```sql-cheatsheet.py``` script in the root folder.

Good luck!
