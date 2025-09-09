import os
import pandas as pd

class Probe:
    
    def __init__(self, protocol, rate, amount, target, port):
        self.protocol = protocol
        self.rate = rate
        self.amount = amount
        self.target = target
        self.port = port
    
    def __str__(self):
        return "========= Defined metrics =========\n\nProtocol: {}\nRate: {}\nAmount: {}\nTarget: {}\nPort:{}\n\n====================================".format(self.protocol, self.rate, self.amount, self.target, self.port)

    def target_string(self):
        targets = ""
        for i in range(len(self.target)):
            if (i+1 == len(self.target)):
                targets += str(self.target[i])
            else:
                targets += str(self.target[i] + ", ")
        print(f"Specfied targets: {targets}")
        return targets
    
    def port_string(self):
        ports = ""
        for i in range(len(self.port)):
            if (i+1 == len(self.port)):
                ports += str(self.port[i])
            else:
                ports += str(self.port[i] + ", ")
        print(f"Specfied ports: {ports}")
        return ports


    def send_data(self):
        targets = self.target_string()
        ports = self.port_string()
        try:
            results =  os.system(f"nping --{self.protocol} -p {ports} {targets} --count {self.amount}")
        except OSError:
            print(os.error)

#nping --udp -p 27017 94.132.98.154 --count 10 --rate 5
#df = pd.DataFrame(data, columns=columns)
#df.to_csv('output.csv', index=False)

influx/influx_config
influx/influx_data
smokeping/config
smokeping/data