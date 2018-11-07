#!/usr/bin/env bash

transmission-remote -n username:password -l | awk '{print substr($1,index($1,$1))}'