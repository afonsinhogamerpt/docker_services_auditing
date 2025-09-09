import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from probe import Probe

BUCKET_INFO = "new_bucket"
TOKEN_INFO = "Oi5reXHe2VlQjk2nYZGQIA9dQ9kZPPcLVrS9IzGYAPyevaCQs8m39ikiT-G8nDiTzJy1XTk8ZQUZQbYt3t1zDA=="
ORG_INFO = "admin"
URL_INFO = "http://127.0.0.1:8086"


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
        print("zzzzzzzzzz...")
        time.sleep(2)
    print("Ligação efetuada com sucesso! :3")
    print(client.ping())
        
    #write_api = client.write_api(write_options=SYNCHRONOUS)
    #p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    #write_api.write(bucket=bucket, org=org, record=p)


object1 = Probe("tcp", 5, 10, ["google.com"], [80])
print(object1)
#print(object1.target)
#object1.send_data()
