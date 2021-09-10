# docker run --entrypoint "/bin/bash" -it -d --rm  htmlemail

init
'python3 init.py'

start
'python3 main.py'

run
'bash run.sh &'

stop
'pkill -9 -f run.sh'

Запуск контейнера

# ps -ef | grep htmlemail | awk '{print $2}' | xargs kill -9 $2
Удаление процессов

