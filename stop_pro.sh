# !/bin/bash
if [ "$1" = "test" ]; then
    while IFS= read -r pid; do
        kill "$pid" || true # 尝试杀死进程，忽略错误
    done < test_pid_file.txt
elif [ "$1" = "product" ]; then

    # 读取PID文件并杀死进程
    while IFS= read -r pid; do
        kill "$pid" || true # 尝试杀死进程，忽略错误
    done < pro_pid_file.txt
else
    echo "第一个参数不是test也不是product"
fi