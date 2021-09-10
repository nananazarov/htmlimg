## Preparing and configuring docker:
Create docker image:
```bash
docker build --pull --rm -f "Dockerfile" -t htmltoimg:latest "."
```

Run docker image:
```bash
docker run --entrypoint "/bin/bash" -it -d --rm  htmltoimg
```

Check is runned:
```bash
docker ps

Output:
=> CONTAINER ID   IMAGE       COMMAND       CREATED         STATUS         PORTS     NAMES
=> idididididid   htmltoimg   "/bin/bash"   2 minutes ago   Up 2 minutes             thirsty_torvalds
```

Connect to running container:
```bash
docker exec -ti {CONTAINER_ID} bash
```

Disconnect from running container:
```bash
Ctrl+d or exit
```

Save the changes from the running container to the image:
```bash
docker commit {CONTAINER_ID} htmltoimg
```

Stop running container:
```bash
docker stop {CONTAINER_ID}
```

## Without docker:
python >V3.8 and pip required
```bash
pip install requirements.txt
apt-get update
apt-get install xvfb
apt-get install xvfb libfontconfig wkhtmltopdf
```

## Scripts to run inside the docker container or directly without docker:
Init:
```bash
python3 init.py
```

Start (run script once):
```bash
python3 main.py
```

Run (run script every 30 minutes):
```bash
bash run.sh &
```

Stop:
```bash
pkill -9 -f run.sh
```

