#!/usr/bin/env bash
#
# fetch torrent name

transmission-remote -n username:password -t $1 -i | grep Name: