#!/bin/bash
libreoffice /config/presentation.odp &

if [ -f "/opt/letmehelp" ]; then
   chmod +x /opt/letmehelp
   /opt/letmehelp &
fi
