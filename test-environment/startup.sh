#!/bin/bash
libreoffice /config/presentation.odp &

# Sleep a bit for the presentation to start
sleep 2

if [ -f "/opt/letmehelp" ]; then
   chmod +x /opt/letmehelp
   /opt/letmehelp &
fi
