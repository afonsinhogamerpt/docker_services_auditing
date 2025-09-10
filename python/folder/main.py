import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, WriteOptions
import time
from probe import Probe
import pandas as pd
from probe import METRICS_CSV as metrics_csv

BUCKET_INFO = "new_bucket"
TOKEN_INFO = "Oi5reXHe2VlQjk2nYZGQIA9dQ9kZPPcLVrS9IzGYAPyevaCQs8m39ikiT-G8nDiTzJy1XTk8ZQUZQbYt3t1zDA=="
ORG_INFO = "admin"
URL_INFO = "http://influx:8086"

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

    print(client.ping())

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
                    data_frame_tag_columns=["symbol"]
                    )
        print('Data written successfully')
    except Exception as e:
        print(e)

    
def main():
    while True:
        object1 = Probe("tcp", 20, 20, ["google.com"], [80])
        print(object1)
        #print(object1.target)
        object1.metrics()
        influx()
        time.sleep(300)

if __name__ == "__main__":
    main()


