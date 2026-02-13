# Standstill station

Orginally developed by Joachim Poutaraud, Julius Jacoby-Pflug and Alexander Jensenius
Revitalized and updated in 2026 by Aleksander Tidemann

The Standstill station is an art-science installation that tests who can move the least! Users put on a pair of headphones and are asked to stand as still as possible while listening to 20 seconds of music and 20 seconds of silence. The user's movements are tracked through a small gyro placed inside the headphones and the movement data is displayed in real-time, for the user to see, and stored on a local SQL server. In the end, the user can see how well they perform compared to all previous participants. 

This repo contains the software and official documentation for the Standstill station.

Picture...


# System overview

Two software programs... Python and bridgehead 

Python.. That generate the UI tpand collects, stores and displays tthe 

Picture of overgang og headphones. Inside is a gyro

Brigdehead -> OSC -> python
Converts the 3-dimensional movement gyro data (XYZ). to OSC.
Its important that the bidgdehead Profile is set to "Quaternion (composite)" under settings. This enable bridgehead to send the OSC data to the Python script over port 8000. 


# Installation

Download Python v3.11

Bridgehead v.1.19

Does the gyro need a driveR??

Navigate to root (standstill-2026) and:
```
pip install -r requirements.txt
```

# How to Run

Run the brigdehead in the root. Make sure the correct setting is used. 
Python standstill-2026.py

open command promt.
run "C:\RITMO\stillstanding-2026>python main.py"


# Development with dummy head-tracking data
For dev..
its not always possible to be on site...


# Database

Something.. How to access it.

List the format.. and tables..

