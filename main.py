import argparse
import sys
from datetime import datetime
from start import start

# Some Hardcore settings

# max_publishers_no = 50
# hostname ='brightiotdev'
# hostname = 'broker.hivemq.com'
# hostname = 'localhost'
# port = 1883
# topic = 'v1/device/telemetry'
# username='admin'
# password='admin1234'
# username='dev'
# password='dev1234'
# auth = True
# QOS = 1
# max_messages = 50


def main():
    try:
        parser = argparse.ArgumentParser(description='MQTT Benchmark Tool')
        parser.add_argument('--publishers', type=int, default=10, help='No of publishers for test')
        parser.add_argument('--hostname', type=str, default='localhost', help='MQTT Broker address')
        parser.add_argument('--port', type=int, default=1883, help='MQTT Port')
        parser.add_argument('--topic', type=str, default='v1/device/telemetry', help='MQTT Topic')
        parser.add_argument('--auth', type=bool, default=False, help='MQTT Authentication')
        parser.add_argument('--username', type=str, help='MQTT Username')
        parser.add_argument('--password', type=str, help='MQTT Password')
        parser.add_argument('--qos', type=int, default=0, help='MQTT QoS')
        parser.add_argument('--max_messages', type=int, default=10, help='Max MQTT messages to be sent')
        parser.add_argument('--timeout', type=int, default=60, help='Test Timeout')
        args = parser.parse_args()
        if args.auth is True and args.username is None:
                raise Exception('Authenication Credentials reqquired')

        print(f"""
        {'='*40}
                MQTT Benchmark Test Tool 
                            v1.0 
        {'='*40}
        """)
        start(hostname=args.hostname, port=args.port, max_publishers_no=args.publishers,
                  topic=args.topic, auth=args.auth, username=args.username, password=args.password,
                  QOS=args.qos, max_messages=args.max_messages, timeout=args.timeout)

    except Exception as error:
        print('[ERROR] main : {}' .format(error))
        sys.exit()

if __name__ == '__main__':
    main()