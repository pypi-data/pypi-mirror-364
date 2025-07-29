#!/bin/sh
set -o xtrace

free
cat /proc/loadavg
./sardetime.sh
