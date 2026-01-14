#!/bin/bash

for i in $(seq 1 30); do
  host=$(printf "linux%02d" "$i")
  echo -n "$host: "
  ssh -o ConnectTimeout=1 $host who 2>/dev/null
done
