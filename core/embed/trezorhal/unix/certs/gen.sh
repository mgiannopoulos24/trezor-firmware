#!/bin/sh

cd "$(dirname "$0")"
for file in *.der
do
    header_file="${file%.der}.h"
    xxd -i "$file" | sed 's/unsigned/static const unsigned/'> "$header_file"
done
