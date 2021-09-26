#!/bin/bash
for((j=1; j<9; j++));do
    ./run.sh 100 10
done

notify-send finito
