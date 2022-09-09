#!/bin/bash
costs=("1.0" "1.25" "1.5" "1.75" "2.0")

prefix_str=""
if [[ $1 ]]
then
    prefix_str="--prefix=$1"
fi

for i in ${costs[*]}; do
    python main.py --multipass --cost-exponent=$i --max-tasks=1000 --policy=batch_wait_tsp $prefix_str --service-time 1 --generator uniform  > /dev/null 2>&1 &
done
