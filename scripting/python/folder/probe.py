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
MAC_FILE = '../csv_txt_files/mac.txt'

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

    
    def to_csv(self):
        columns = ['SENT/RCVD', 'TRAVEL-TIME', 'SOURCE-IP', 'DST-IP']

        rows = self.handle_files()
        dataframe = pd.DataFrame(rows) 
        dataframe.to_csv(NPING_FORMATED_CSV, index=False)


    def handle_files(self):
        lines = []
        data = self.send_data()
        pattern = re.compile(r'^(SENT|RCVD)\s+\(([\d\.]+)s\)\s+(TCP|UDP)\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s*>\s*(\d+\.\d+\.\d+\.\d+):(\d+)(?:.*?seq=(\d+))?')
        
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
            #print(lines)
            [lines.pop(0) for _ in range(2)]
            lines.pop()
            with open(RESULTS_FILE_FORMAT, 'w') as f:
                for line in lines:
                    line.strip("\n")
                    #print(line)
                    f.write(line)

        with open(RESULTS_FILE_FORMAT, 'r') as f:
            lines = f.readlines()
        
        rows = []

        for line in lines:
            m = pattern.search(line)
            if m:
                rows.append({
                    "SENT/RCVD": m.group(1),   #SENT or RCVD
                    "TRAVEL-TIME": float(m.group(2)),  #time in sec
                    "SOURCE-IP": m.group(4),
                    "DST-IP": m.group(6)
                }) 
        return rows
    
    
    def avg_delay(self):
        dataframe = pd.read_csv(NPING_FORMATED_CSV)
        travel_time = dataframe['TRAVEL-TIME'].tolist()
        direction = dataframe['SENT/RCVD'].tolist()

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
        return float(avg)

    def jitter(self):
        self.to_csv()
        dataframe = pd.read_csv(NPING_FORMATED_CSV)
        travel_time = dataframe['TRAVEL-TIME'].tolist()
        direction = dataframe['SENT/RCVD'].tolist()
        
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
        return float(jitter_value)
    
    def getmac(self):
        command = f"ip addr | grep link/ether | cut -c 16-32"

        with open(MAC_FILE, 'x') as f:    
            mac = str(subprocess.check_output(command, shell=True, text=True))
            f.write(mac)

        with open(MAC_FILE, 'r') as f:
            lines = f.readlines()
            
        mac = lines[0]
        os.remove(MAC_FILE)
        mac = mac.replace('\n','')
        return mac
    
    def metrics(self):
        row = []
        #mac = self.getmac()
        
        jitter_value = self.jitter()
        avg_delay = self.avg_delay()

        with open(RESULTS_FILE, 'r') as f:
            datetime = f.read()

        dt = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', datetime)
        time = str(dt.group(1))

        with open(RESULTS_FILE_FORMAT, 'r') as f:
            lines = f.read()

        match = re.search(r"Lost: \d+ \(([\d.]+)%\)", lines)
        packet_loss = float(match.group(1))

        dataframe = pd.read_csv(NPING_FORMATED_CSV)
        dataframe_src = dataframe["SOURCE-IP"].to_list()
        dataframe_dst = dataframe["DST-IP"].to_list()
        
        src_ip = dataframe_src[0]
        dst_ip = dataframe_dst[0]

        row.append({
            "JITTER": jitter_value,
            "LATENCY": avg_delay,
            "PACKET-LOSS": packet_loss,
            "TIME": time, 
            "PROTOCOL": str(self.protocol).upper(),
            "DST-IP": dst_ip,
            "SRC-IP": src_ip
        })

        dataframe = pd.DataFrame(row)
        dataframe.to_csv(METRICS_CSV, index=False)

        return dataframe.to_string()
 

    def send_data(self):
        results = []
        payload = "\\x00\\x00\\x01\\x00"
        if self.protocol == "tcp":
            nping = f"nping --{self.protocol} -p {self.port} {self.target} --count {self.amount} --rate {self.rate}"
        else:
            nping = f"nping --{self.protocol} -p {self.port} {self.target} --count {self.amount} --rate {self.rate} --data-string {payload}"
        try:
            results = str(subprocess.check_output(nping, shell=True, text=True))
            return results
        except OSError:
            return os.error 
