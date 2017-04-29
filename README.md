# smarthome: Simple IoT hub and web interface
(C) Tim Churchard tim.churchard at gmail.com


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
```

3. Switch to the new environment
```bash
source venv/bin/activate
```



## Hardware

0. Arduino Uno + TMP36 temperature sensor

1. Loop Electricity Monitor

Using a [Loop Electricity Monitor](https://www.loopenergysaver.com/) and [pavoni.pyloopenergy](https://github.com/pavoni/pyloopenergy) to record whole house energy usage.

2. RPI3 Sound Monitor + IR Remote for TV Volume


3. Energenie PiMote Socket + RPI2 RF Control


4.


## Software



