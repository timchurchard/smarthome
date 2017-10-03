
# LIRC Setup Notes

### Lirc

Setting up lirc was fairly difficult.  After my raspberry pi memory card died I had to rebuild.  I found the latest raspbian lite lircd did not work with the old config.  I tried monthly raspbian released until one worked: https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-03-03/

My LIRC board: http://blog.energenie4u.co.uk/tech-gadgets/something-weekend-energenie-pi-board-extension-guide/

Follow user guide here: https://energenie4u.co.uk/res/pdfs/ENER314-IR_User_guide_V3.pdf
 

### Run on boot

Make a /home/pi/run_my_stuff.sh 
```#!/bin/bash
echo "run_my_stuff: Started $(date)"
cd /home/pi/smarthome.git
su - pi -c "/usr/bin/screen -d -m -S temp /home/pi/smarthome.git/run_iotictemp.sh"
```

And a run script for each service

```#!/bin/bash
cd /home/pi/smarthome.git
source venv/bin/activate
cd src/smarthome
python3 IoticTemp.py```

And modify /etc/rc.local to call the run_my_stuff

```
echo "run_my_stuff..."
sh -c "/home/pi/run_my_stuff.sh 2>&1 >> /home/pi/run_my_stuff.log" &
```

