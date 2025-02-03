#!/bin/bash

pg_dir="$PWD"
while true; do
  if ! [ -d "$pg_dir" ]; then
    exit 1
  elif [ -f "$pg_dir/site.conf" ]; then
    echo "$pg_dir"
    exit 0
  else
    pg_dir="${pg_dir%/*}"
  fi
done

