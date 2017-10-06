#!/usr/bin/env gawk -f

BEGIN {
    FS=" "
}
{
    if ($0 ~ /^Plate/)
    {
        n = split($2, arr, "/")
        print arr[n]
    }
}
