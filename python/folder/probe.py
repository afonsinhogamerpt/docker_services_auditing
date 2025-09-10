import os
import pandas as pd
import subprocess
import time
import re
import math

METRICS_CSV = '../csv_txt_files/metrics.csv' 
NPING_FORMATED_CSV = '../csv_txt_files/nping_formated.csv'
RESULTS_FILE = '../csv_txt_files/results.txt'
RESULTS_FILE_FORMAT = '../csv_txt_files/results_format.txt'

class Probe:
    
    def __init__(self, protocol, rate, amount, target, port):
        self.protocol = protocol
        self.rate = rate
        self.amount = amount
        self.target = target
        self.port = port
        metrics_csv = METRICS_CSV

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
        dataframe.to_csv(NPING_FORMATED_CSV, index=False)


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
        dataframe = pd.read_csv(NPING_FORMATED_CSV)
        travel_time = dataframe['TRAVEL-TIME'].tolist()
        direction = dataframe['SYN/SYN-ACK'].tolist()

        total = 0
        count_packets = 0
        i = 0

        while i < len(travel_time):
            if direction[i] == "SENT":
            
                j = i + 1
                last_rcvd_time = None
                while j < len(travel_time) and direction[j] != "SENT":
                    if direction[j] == "RCVD":
                        last_rcvd_time = travel_time[j]
                    j += 1
                if last_rcvd_time is not None:
                    total += (last_rcvd_time - travel_time[i]) * 1000
                    count_packets += 1
                i = j  
            else:
                i += 1

        avg = total / count_packets if count_packets else 0
        return avg

    def jitter(self):
        self.to_csv()
        dataframe = pd.read_csv(NPING_FORMATED_CSV)
        travel_time = dataframe['TRAVEL-TIME'].tolist()
        direction = dataframe['SYN/SYN-ACK'].tolist()
        
        avg_delay = self.avg_delay()  
        
        sum = 0
        count_packets = 0
        i = 0
        
        while i < len(travel_time):
            if direction[i] == "SENT":
                
                j = i + 1
                last_rcvd_time = None
                while j < len(travel_time) and direction[j] != "SENT":
                    if direction[j] == "RCVD":
                        last_rcvd_time = travel_time[j]
                    j += 1
                if last_rcvd_time is not None:
                    rtt = (last_rcvd_time - travel_time[i]) * 1000
                    sum += (rtt - avg_delay) ** 2
                    count_packets += 1
                i = j  
            else:
                i += 1
        
        jitter_value = math.sqrt(sum / count_packets) if count_packets else 0
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
