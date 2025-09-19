FROM python
WORKDIR /etc/scripts
COPY requirements.txt .
RUN pip install -r requirements.txt 
COPY ./folder /etc/scripts
RUN apt-get update && apt-get install nmap -y && apt install iproute2 -y && apt-get upgrade -y
