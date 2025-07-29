#!/bin/bash

jobid="test$(date +%s)"

: ${CUSTOM_ENV_CI_JOB_ID:=${jobid}}
: ${CUSTOM_ENV_CI_JOB_IMAGE:=registry.git.iem.at/devtools/sardinecake/windows:latest}

export CUSTOM_ENV_CI_JOB_ID
export CUSTOM_ENV_CI_JOB_IMAGE


date
time gitlab-sardinecake-executor prepare --clonedir /dev/shm/sardetime/ --prepare-script "${0%/*}/hi.sh" --timeout 1200
date
gitlab-sardinecake-executor cleanup
date

