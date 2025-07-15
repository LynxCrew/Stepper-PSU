#!/bin/bash

KLIPPER_PATH="${HOME}/klipper"
REPO_PATH="${HOME}/stepper-psu"
EXTENSIONS="stepper_psu"

set -eu
export LC_ALL=C


function preflight_checks {
    if [ "$EUID" -eq 0 ]; then
        echo "[PRE-CHECK] This script must not be run as root!"
        exit -1
    fi

    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F 'klipper.service')" ]; then
        printf "[PRE-CHECK] Klipper service found! Continuing...\n\n"
    else
        echo "[ERROR] Klipper service not found, please install Klipper first!"
        exit -1
    fi
}

function check_download {
    local stepperpsudirname stepperpsubasename
    stepperpsudirname="$(dirname ${REPO_PATH})"
    stepperpsubasename="$(basename ${REPO_PATH})"

    if [ ! -d "${REPO_PATH}" ]; then
        echo "[DOWNLOAD] Downloading Stepper-PSU repository..."
        if git -C $stepperpsudirname clone https://github.com/LynxCrew/Stepper-PSU.git $stepperpsubasename; then
            chmod +x ${REPO_PATH}/install.sh
            chmod +x ${REPO_PATH}/update.sh
            chmod +x ${REPO_PATH}/uninstall.sh
            printf "[DOWNLOAD] Download complete!\n\n"
        else
            echo "[ERROR] Download of Stepper-PSU git repository failed!"
            exit -1
        fi
    else
        printf "[DOWNLOAD] Stepper-PSU repository already found locally. Continuing...\n\n"
    fi
}

function link_extension {
    echo "[INSTALL] Linking extension to Klipper..."

    for extension in ${EXTENSIONS}; do
        if [ ! -f "${KLIPPER_PATH}/klippy/extras/${extension}.py" ]; then
            ln -sf "${REPO_PATH}/source/${extension}.py" "${KLIPPER_PATH}/klippy/extras/${extension}.py"
        fi
    done
}

function restart_klipper {
    echo "[POST-INSTALL] Restarting Klipper..."
    sudo systemctl restart klipper
}


printf "\n======================================\n"
echo "- Stepper-PSU install script -"
printf "======================================\n\n"


# Run steps
preflight_checks
check_download
link_extension
restart_klipper
