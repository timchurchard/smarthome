# smarthome: Simple IoT hub and web interface
##### Copyright (C) 2017 Tim Churchard tim.churchard at gmail.com

A simple single page dashboard that provides a volume control for my living room and some stats for my house.
![Mobile Screenshot](smarthome_screenshot_2017-09-01_08-41-51.png)

## Setup

1. Get the submodules
```bash
git submodule update --init --recursive
```

2. Install python deps. in virtualenv (Debian/Ubuntu)
```bash
sudo apt-get install python-dev libmysqlclient-dev
sudo apt-get install python3-numpy python3-scipy python3-pyaudio
sudo pip3 install virtualenv
mkdir venv
virtualenv venv
./venv/bin/pip3 install -r requirements.txt
./venv/bin/pip3 install -r subs/pyloopenergy/requirements.txt
cd subs/pyloopenergy
python3 setup.py install
```

3. Switch to the new environment
```bash
source venv/bin/activate
```


## Hardware

0. Arduino Uno + TMP36 temperature sensor

IoticTemp.py simple fetch temp data from Arduino (running cfg/arduino_tmp36.uno).  Store in DB and publish 10s.

1. Loop Electricity Monitor

Using a [Loop Electricity Monitor](https://www.loopenergysaver.com/) and [pavoni.pyloopenergy](https://github.com/pavoni/pyloopenergy) to record whole house energy usage.
IoticLoop.py

2. RPI3 Sound Monitor + IR Remote for TV Volume
IoticVolume.py

3. Energenie PiMote Socket + RPI2 RF Control (Living room lamp)
IoticLamp.py
Note: Using gpiozero module works best with python2 outside of venv!

