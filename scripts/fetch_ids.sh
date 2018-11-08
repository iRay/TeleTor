#!/usr/bin/env bash
#
# fetch all torrents ids

transmission-remote -n username:password -l | awk '{print substr($1,index($1,$1))}'