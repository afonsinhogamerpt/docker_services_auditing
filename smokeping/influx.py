import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "smokeping"
org = "admin"
token = "-slk3IEBCrEYq4KSV7utvIjxZ76c58q3lQS8nKLxSNtbMeBi1-PjQ6fyT0vJaD0KsUzThu29bPwTCUZAg87iiA=="

url="http://influx:8086"

try:

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("TCPPing").field("value", 99.0)
    write_api.write(bucket=bucket, org=org, record=p)
except:
    print("Não foi possível ligar ao influx :/ ")


