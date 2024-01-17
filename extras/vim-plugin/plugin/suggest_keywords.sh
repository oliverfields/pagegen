#!/bin/bash

report_error() {
  echo $*
  exit 1
}

stopwords="$1"
min_frequency=3
keywords=()

[ -f "$stopwords" ] || report_error "Unable to find $stopwords"

# Thanks John Red, https://stackoverflow.com/a/10552948
cat \
| tr '[:punct:]' ' ' \
| tr 'A-Z' 'a-z' \
| tr -s ' ' \
| tr ' ' '\n' \
| sed '/^$/d' \
| sort \
| uniq -c \
| sort -rn \
| while read -r line; do
  line="${line# *}"
  frequency="$(echo "$line" | cut -d ' ' -f 1)"
  keyword="$(echo "$line" | cut -d ' ' -f 2)"

  if ! grep "^$keyword$" "$stopwords" > /dev/null; then
    if [ $frequency -ge $min_frequency ]; then
      keywords+=($keyword)
    else
      # We are done here, only low frequency keywords remaining, lets wrap up
      if [ ${#keywords[@]} -eq 0 ]; then
        echo "No suggestions found"
      else
        # Add , and capitalize
        echo ${keywords[@]} | sed 's/\ /, /g ; s/\b\(.\)/\u\1/g'
      fi
      break
    fi
  fi
done

