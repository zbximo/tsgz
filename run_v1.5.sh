#/!bin/bash

#nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v2.py --name new --env test &
#nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v2.py --name post --env test &
#nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v2.py --name cluster --env test &

#if [ "$1" = "test" ]; then
#    nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v1.5.py --name new --env test &
#    nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v1.5.py --name post --env test &
#    nohup /opt/anaconda3/envs/tsgz/bin/python run_test_v1.5.py --name cluster --env test &
#    tail -f /dev/null
#elif [ "$1" = "product" ]; then
#    nohup /opt/anaconda3/envs/tsgz/bin/python run_product_v1.5.py --name new --env product &
#    nohup /opt/anaconda3/envs/tsgz/bin/python run_product_v1.5.py --name post --env product &
#    nohup /opt/anaconda3/envs/tsgz/bin/python run_product_v1.5.py --name cluster --env product &
#    tail -f /dev/null
#else
#    echo "第一个参数不是test也不是product"
#fi
if [ "$1" = "test" ]; then
    nohup python run_test_v1.5.py --name new --env test &
    nohup python run_test_v1.5.py --name post --env test &
    nohup python run_test_v1.5.py --name cluster --env test &
    tail -f /dev/null
elif [ "$1" = "product" ]; then
    nohup python run_product_v1.5.py --name new --env product &
    nohup python run_product_v1.5.py --name post --env product &
    nohup python run_product_v1.5.py --name cluster --env product &
    tail -f /dev/null
else
    echo "第一个参数不是test也不是product"
fi
