#/!bin/bash

nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v2.py --name new --env test &
nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v2.py --name post --env test &
nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v2.py --name cluster --env test &



