# smarthome: Simple IoT hub and web interface
(C) Tim Churchard tim.churchard at gmail.com


## Setup

1. Get the submodules
```bash
git submodule update --init --recursive
```

2. Install python deps. in virtualenv
```bash
sudo pip3 install virtualenv
mkdir venv
virtualenv venv
./venv/bin/pip3 install -r requirements.txt
./venv/bin/pip3 install -r subs/pyloopenergy/requirements.txt
```

