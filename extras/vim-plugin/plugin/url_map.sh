#!/bin/bash

threads_dir="$1"
urls="$2"

urls_tmp="$(mktemp)"
trap 'rm -rf -- "$urls_tmp"' EXIT

# Find all files first, removing index pages, they are handled later
find "$threads_dir" -type f | sed "s#$threads_dir## ; /index$/d" > "$urls_tmp"

# Find all index pages
find "$threads_dir" -type d | sed "s#$threads_dir## ; s#\$#/index#" >> "$urls_tmp"

# Strip assets dir
sed -i '/^\/assets\/.*/d' "$urls_tmp"

# Sort and remove duplicates
sort -u -o "$urls_tmp" "$urls_tmp"

# Use pagegen function to make url from path
{
python3 - << EOF
from pagegen.utility_no_deps import urlify

with open('$urls_tmp') as f:
    for l in f:
        path = l.strip()
        url = urlify(path)
        print(url + ';' + path)
EOF
} > "$urls"

