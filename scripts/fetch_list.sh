#!/usr/bin/env bash

transmission-remote -n username:password -l | awk '{print substr($1,index($1,$1)) "\t" substr($2,index($2,$2)) "\t" substr($0,index($0,$9))}'