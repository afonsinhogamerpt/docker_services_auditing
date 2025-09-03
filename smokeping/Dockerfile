FROM lscr.io/linuxserver/smokeping
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add --no-cache python3 py3-pip
RUN apk add nano
RUN python -m venv my-venv 
RUN . /my-venv/bin/activate 
RUN my-venv/bin/pip install influxdb_client




