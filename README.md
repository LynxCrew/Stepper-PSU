# LynxCrew Stepper-PSU Plugin

## What does it do:
This plugin enables a stepper_psu config section in Kalico/Klipper if you are
using a relay to disconnect stepper/driver power when not in use.
If configured, it will enable a defined output pin when a stepper is to be enabled
and pause the gcode queue for a specified amount of time so the PSU can turn on fully.
To disable the PSU you need to use a command.

## Install:
SSH into you pi and run:
```
cd ~
wget -O - https://raw.githubusercontent.com/LynxCrew/Stepper-PSU/main/install.sh | bash
```

then add this to your moonraker.conf:
```
[update_manager stepper-psu]
type: git_repo
channel: dev
path: ~/stepper-psu
origin: https://github.com/LynxCrew/Stepper-PSU.git
managed_services: klipper
primary_branch: main
install_script: install.sh
```

## How to use:
!!This does only work if your drivers have an enable pin as it hooks directly
into the enable pin code!!
(on the other hand, drivers without an enable pin are always active and thus
should not need a psu, if you feel like you still need it, open an issue and
I will try to implement it)
just add
```
[stepper_psu my_stepper_psu]
pin: 
#   the pin to be switched when steppers turn on or off
wait_time: 0.0
#   The Time to block after enabling steppers so the psu has time to fully turn on
stepper:
#   the steppers that should cause the pin to switch.
#   If this parameter is not specified, the module will listen to all steppers
```

`DISABLE_STEPPER_PSU STEPPER_PSU=my_stepper_psu` will turn it off again
