#!/bin/bash
clear

#            ▀█▀ █ █ █▀█ █▀▄▀█ ▄▀█ █▀
#             █  █▀█ █▄█ █ ▀ █ █▀█ ▄█  
#             https://t.me/netuzb
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

printf "\n╔╗─╔╦═╗╔═╦═══╦═══╦═╗╔═╗"
printf "\n║║─║║║╚╝║║╔═╗╠╗╔╗╠╗╚╝╔╝"
printf "\n║║─║║╔╗╔╗║║─║║║║║║╚╗╔╝"
printf "\n║║─║║║║║║║║─║║║║║║╔╝╚╗"
printf "\n║╚═╝║║║║║║╚═╝╠╝╚╝╠╝╔╗╚╗"
printf "\n╚═══╩╝╚╝╚╩═══╩═══╩═╝╚═╝"
printf "\n 𝘘𝘢𝘺𝘵𝘢 𝘪𝘴𝘩𝘨𝘢 𝘵𝘶𝘴𝘩𝘮𝘰𝘲𝘥𝘢...\n\n"

# Sozlash
apt update
apt upgrade

# Kerakli bibliotekalar
pkg install git
pkg install python3
pip install -r requirements.txt

# Asosiy boʻlim 
python3 -m umodx
