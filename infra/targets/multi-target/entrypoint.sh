#!/bin/sh
set -e

/usr/sbin/vsftpd &
python3 /opt/custom_service.py &

exec /usr/sbin/xinetd -dontfork
