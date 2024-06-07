#/!bin/bash
source activate tsgz


if [ "$1" = "test" ]; then
    > test_pid_file.txt
    nohup /opt/anaconda3/envs/tsgz/bin/python test_pro.py --name new --env test &
    PID=$!
    echo $PID >> test_pid_file.txt
    nohup /opt/anaconda3/envs/tsgz/bin/python test_pro.py --name post --env test &
    PID=$!
    echo $PID >> test_pid_file.txt
    nohup /opt/anaconda3/envs/tsgz/bin/python test_pro.py --name cluster --env test &
    PID=$!
    echo $PID >> test_pid_file.txt
elif [ "$1" = "product" ]; then
    > pro_pid_file.txt
    nohup /opt/anaconda3/envs/tsgz/bin/python test_pro.py --name new --env product &
    PID=$!
    echo $PID >> pro_pid_file.txt
    nohup /opt/anaconda3/envs/tsgz/bin/python test_pro.py --name post --env product &
    PID=$!
    echo $PID >> pro_pid_file.txt
    nohup /opt/anaconda3/envs/tsgz/bin/python test_pro.py --name cluster --env product &
    PID=$!
    echo $PID >> pro_pid_file.txt
else
    echo "第一个参数不是test也不是product"
fi
