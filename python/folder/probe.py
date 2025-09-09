import os
import pandas as pd
import subprocess
import time
import re
import math

METRICS_CSV = 'metrics.csv' 
CSV_FILE = 'output.csv'
RESULTS_FILE = 'results.txt'
RESULTS_FILE_FORMAT = 'results_format.txt'


class Probe:
    
    def __init__(self, protocol, rate, amount, target, port):
        self.protocol = protocol
        self.rate = rate
        self.amount = amount
        self.target = target
        self.port = port

    '''toString method'''
    def __str__(self):
        return "========= Defined metrics =========\n\nProtocol: {}\nRate: {}\nAmount: {}\nTarget: {}\nPort:{}\n\n====================================".format(self.protocol, self.rate, self.amount, self.target, self.port)

    '''Formating port strings used in a nping command (multi value)'''
    def target_string(self):
        targets = ""
        for i in range(len(self.target)):
            if (i+1 == len(self.target)):
                targets += str(self.target[i])
            else:
                targets += str(self.target[i] + ", ")
        print(f"Specfied targets: {targets}")
        return targets
    
    '''Formating port strings used in a nping command (multi value)'''
    def port_string(self):
        ports = ""
        for i in range(len(self.port)):
            if (i+1 == len(self.port)):
                ports += str(self.port[i])
            else:
                ports += str(self.port[i] + ", ")
        print(f"Specfied ports: {ports}")
        return ports
    
    def to_csv(self):
        columns = ['SYN/SYN-ACK', 'TRAVEL-TIME', 'SOURCE-IP', 'DST-IP', 'SEQ']

        rows = self.handle_files()
        dataframe = pd.DataFrame(rows) 
        dataframe.to_csv(CSV_FILE, index=False)


    def handle_files(self):
        lines = []
        data = self.send_data()
        pattern = re.compile(r'^(SENT|RCVD)\s+\(([\d\.]+)s\).*?(\d+\.\d+\.\d+\.\d+):\d+\s*>\s*(\d+\.\d+\.\d+\.\d+):\d+.*?seq=(\d+)')

        if os.path.isfile(RESULTS_FILE) is not True:
            f = open(RESULTS_FILE, "x" )
            f.close()
        else:
            print("")

        if os.path.isfile(RESULTS_FILE) is not True:
            f = open(RESULTS_FILE, "x" )
            f.close()
        else:
            print("")

        with open(RESULTS_FILE, "w") as f:
                f.write(data)
        
        with open (RESULTS_FILE, 'r') as f:
            lines = f.readlines()
            [lines.pop(0) for _ in range(2)]
            lines.pop()
            with open(RESULTS_FILE_FORMAT, 'w') as f:
                for line in lines:
                    line.strip("\n")
                    f.write(line)

        with open(RESULTS_FILE_FORMAT, 'r') as f:
            lines = f.readlines()
        
        rows = []

        for line in lines:
            m = pattern.search(line)
            if m:
                rows.append({
                    "SYN/SYN-ACK": m.group(1),   #SENT or RCVD
                    "TRAVEL-TIME": float(m.group(2)),  #time in sec
                    "SOURCE-IP": m.group(3),
                    "DST-IP": m.group(4),
                    "SEQ": int(m.group(5))
                }) 
        return rows
    
    def avg_delay(self):
        sum = 0

        dataframe = pd.read_csv('output.csv')
        travel_time = dataframe['TRAVEL-TIME']
        travel_time = travel_time.tolist()

        for i in range(0, len(travel_time), 2):
            if (i + 1 > len(travel_time)):
                break
            sum+= (travel_time[i+1] - travel_time[i]) * 1000
        avg = (sum/(len(travel_time)/2))
        return avg

    def jitter(self):
        self.to_csv()
        sum = 0
        dataframe = pd.read_csv('output.csv')
        travel_time = dataframe['TRAVEL-TIME']
        travel_time = travel_time.tolist()
        
        avg_delay = self.avg_delay()
        #print(f"Average Delay: {avg_delay}")
        
        for i in range(0, len(travel_time), 2):
            delay_packet = (travel_time[i+1] - travel_time[i]) * 1000
            print(delay_packet)
            sum+=(delay_packet - avg_delay)**2
        
        jitter_value = math.sqrt(sum/(len(travel_time)/2)) 
        #print(f"Average Jitter: {jitter_value}")
        return jitter_value
    
    def metrics(self):
        row = []
        jitter_value = self.jitter()
        avg_delay = self.avg_delay()

        with open(RESULTS_FILE_FORMAT, 'r') as f:
            lines = f.read()

        match = re.search(r"Lost: \d+ \(([\d.]+)%\)", lines)
        packet_loss = float(match.group(1))

        row.append({
            "JITTER": jitter_value,
            "LATENCY": avg_delay,
            "PACKET-LOSS": packet_loss
        })

        dataframe = pd.DataFrame(row)
        dataframe.to_csv(METRICS_CSV, index=False)

        return dataframe.to_string()
 

    def send_data(self):
        results = []
        targets = self.target_string()
        ports = self.port_string()
        nping = f"nping --{self.protocol} -p {ports} {targets} --count {self.amount}"
        
        try:
            results = str(subprocess.check_output(nping, shell=True, text=True))
            return results
        except OSError:
            return os.error 
