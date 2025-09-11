import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, WriteOptions
import time
from probe import Probe
import pandas as pd
from probe import METRICS_CSV as metrics_csv
import os

BUCKET_INFO = "new_bucket"
TOKEN_INFO = "Oi5reXHe2VlQjk2nYZGQIA9dQ9kZPPcLVrS9IzGYAPyevaCQs8m39ikiT-G8nDiTzJy1XTk8ZQUZQbYt3t1zDA=="
ORG_INFO = "admin"
URL_INFO = "http://influx:8086"
PROBE_INFO = "../csv_txt_files/probe_info"

def influx():
    bucket = BUCKET_INFO
    org = ORG_INFO
    token = TOKEN_INFO
    url=URL_INFO

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    #print(client.ping())

    while client.ping() is not True:
        print("Waiting...")
        time.sleep(2)
    print("Connected!")

    write = client.write_api(write_options=SYNCHRONOUS)

    dataframe = pd.read_csv(metrics_csv)
    try:
        write.write(
                    bucket=BUCKET_INFO, 
                    record=dataframe, 
                    data_frame_measurement_name="metrics", 
                    data_frame_tag_columns=["symbol"],
                    data_frame_timestamp_column="TIME" 
                    )
        print('Data written successfully')
    except Exception as e:
        print(e)

def add_targets():
    if os.path.isfile(PROBE_INFO) is not True:
        f = open(PROBE_INFO, "x" )
        f.close()
    else:
        print("")

    while True:
        print("Do you want to add targets?(Y/N)")
        r = input()
        if (str(r).upper() != "Y" and str(r).upper() !="N"):
            continue
        elif (str(r).upper() != "Y"):
            break
        else:
            print("Target: ")
            target = input()
            while True:

                print("Protocol(TCP/UDP): ")
                protocol = input()
                if (protocol.upper() != "UDP" and protocol.upper() != "TCP"):
                    continue 
                else:
                    break
            
            while True:
                print("Number of packets to send: ")
                num_packets = input()
                num_packets = int(num_packets)
                
                if (isinstance(num_packets, int)):
                    break
                else:
                    continue

            while True:
                print("Port number: ")
                port_number = input()
                port_number = int(port_number)

                if (isinstance(port_number, int)):
                    break
                else:
                    continue
            
            while True:
                print("Rate: ")
                rate = input()
                rate = int(rate)
                if (isinstance(rate, int)):
                    break
                else:
                    continue
            
            with open(PROBE_INFO, 'a') as f:
                #target:port rate num_packets protocol
                line = "{} {} {} {} {}".format(target, port_number, rate, num_packets, protocol)
                f.write(line)    

def create_objects():

    probes = []

    with open(PROBE_INFO,'r') as f:
        lines = f.readlines()
    
    for _ in lines:
        list = _.strip().split()
        
        address = str(list[0])
        port = list[1]
        rate = list[2]
        num_packets = list[3]
        protocol = list[4]

        probes.append(Probe(protocol, rate, num_packets, address, port))
    
    #print(probes[0])

    for i in range(0, len(probes)):
        probes[i].metrics()
        influx()
        time.sleep(2)


def main():
    add_targets()   
    
    while True:
        create_objects()
        time.sleep(30)

if __name__ == "__main__":
    main()


