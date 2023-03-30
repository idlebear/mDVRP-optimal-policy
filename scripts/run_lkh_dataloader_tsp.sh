#!/bin/bash
etas=("0.2")
# lambs=("0.5" "0.6" "0.7" "0.8" "0.9")
# given a 30 minute service time
# lambdas for single robot
# lambs=('0.0002777777777777778' '0.0003333333333333333' '0.00038888888888888887' '0.00044444444444444447' '0.0005')
# lambdas for six sectors: lambda = p * m / s
# lambs=(
#     '0.003'
#     '0.002666666666666667'
#     '0.002333333333333333'
#     '0.0019999999999999996'
#     '0.0016666666666666668'
#     )
# lambda to give max rho of 0.9 in largest (by count) cluster
# lambs=('0.002245519713261649')  # 0.9
# lambs=('0.002370270808442851') # 0.95
lambs=('0.007410215053763441') # 0.99max @ 10min service time
seeds=("6983" "42" "520" "97" "29348" "935567" "7")
tasks=5000
total_tasks=5500
initial_tasks=5
policy="lkh_batch_tsp_time"
cost_exponent=-7.0
data_source='data/montreal_nord-2017_2019-2500-6.clustered.csv'
max_initial_wait=500
service_time=600
tick_time=10

prefix_str=""
if [[ $1 ]]
then
    prefix_str="--prefix=$1"
    shift
fi


# while (( "$#" )); do
    # l=$1
    for l in ${lambs[*]}; do
        echo working on $l...
        for s in ${seeds[*]}; do
            echo ...seed $s
            # eta-batch, 0.2
            python main.py --multipass --tick-time $tick_time --cost-exponent=$cost_exponent --eta=0.2 --max-tasks=$tasks --total-tasks=$total_tasks --initial-tasks $initial_tasks --max-initial-wait $max_initial_wait  --lambd=$l --seed=$s --sectors=1 --policy=lkh_batch_tsp_time $prefix_str --service-time $service_time --generator data_loader --data-source $data_source > /dev/null 2>&1 &
            # batch
            python main.py --multipass --tick-time $tick_time --cost-exponent=$cost_exponent --eta=1.0 --max-tasks=$tasks --total-tasks=$total_tasks --initial-tasks $initial_tasks --max-initial-wait $max_initial_wait  --lambd=$l --seed=$s --sectors=1 --policy=lkh_batch_tsp_time $prefix_str --service-time $service_time --generator data_loader --data-source $data_source  > /dev/null 2>&1 &
            # dc-batch
            python main.py --multipass --tick-time $tick_time --cost-exponent=$cost_exponent --eta=1.0 --max-tasks=$tasks --total-tasks=$total_tasks --initial-tasks $initial_tasks --max-initial-wait $max_initial_wait  --lambd=$l --seed=$s --sectors=10 --policy=lkh_batch_tsp_time $prefix_str --service-time $service_time --generator data_loader --data-source $data_source  > /dev/null 2>&1 &
        done
        wait
    done
    # shift
# done
