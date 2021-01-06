import argparse
from multiprocessing import cpu_count, JoinableQueue
import time
from mqtt_publisher import Publisher
from mqtt_subscriber import Subscriber
from prettytable import PrettyTable
import numpy as np


def msg_publish(client):
    try:
        client.run()
        client.print_avgpubtime()
    except Exception as error:
        print('[ERROR] msg_publish : {}' .format(error))

def msg_subscribe(client):
    try:
        client.run()
        # client.print_avgpubtime()
    except Exception as error:
        print('[ERROR] msg_subscribe : {}' .format(error))

def print_event(msg):
    try:
        # print(msg)
        print('{0} {1} stats: msg_mean: {2}ms, msg_average: {3}ms, '
              'msg_std: {4}ms, msg_success_rate : {5} % ({6}/{7}), total_duration: {8} seconds, '
              'bandwidth : {9} msg/second'
              .format(msg['entity'], msg['name'], msg['msg_mean'], msg['msg_average'], msg['msg_std'],
                      msg['success-rate'], msg['msg_received'], msg['max_msg_count'], msg['total_duration'],
                      msg['bandwidth'])
              )
    except Exception as error:
        print('[ERROR] print_event ')
        print(error)

# Some Hardcore settings

max_publishers_no = 50
# hostname ='brightiotdev'
# hostname = 'broker.hivemq.com'
hostname = 'localhost'
port = 1883
topic = 'v1/device/telemetry'
# username='admin'
# password='admin1234'
username='dev'
password='dev1234'
auth = True
QOS = 1
max_messages = 50


def print_config(mean, bandwidth):
    try:
        table = PrettyTable()
        table.field_names = ["Config", "Value", "Unit"]
        total_msgs = max_publishers_no * max_messages
        table.add_rows([
            ["Hostname", hostname, ''],
            ["Port", port, 'MQTT'],
            ["QoS", QOS, ''],
            ["Publishers", max_publishers_no, 'Nos'],
            ["Messages/Publisher", max_messages, "Msg's"],
            ["Total Msgs", total_msgs, "Msg's"],
            ["Mean (ms)", round(mean, 3), "ms"],
            ["Bandwidth (msg/sec)", round(bandwidth, 3), "msg/sec"]
        ])
        print(table)
    except Exception as error:
        print('[ERROR] print_config ')
        print(error)


def print_table(msg):
    try:
        table = PrettyTable()
        table.title = msg['entity'] + ' ' + msg['name']
        table.field_names = ["Fields", "Value", "Unit"]
        table.add_rows([
            ["Message Mean (ms)", msg['msg_mean'], "ms"],
            ["Message Average (ms)", msg['msg_average'], "ms"],
            ["Message Std (ms)", msg['msg_std'], "ms"],
            ["Success Rate (%)", msg['success-rate'], "%"],
            ["Message Received (Nos)", msg['msg_received'], "Nos"],
            ["Total Message (Nos)", msg['max_msg_count'], "Nos"],
            ["Duration (s)", msg['total_duration'], "s"],
            ["Bandwidth (msg's/sec)", msg['bandwidth'], "msg/sec"],
        ])
        print(table)
    except Exception as error:
        print('[ERROR] print_table ')
        print(error)

def main():
    try:

        subscribers = []
        publishers = []
        publishers_mean_dur = []
        publishers_bandwidth = []

        pub_buffer = JoinableQueue()
        sub_buffer = JoinableQueue()
        print('Number of cpu : {}' .format(cpu_count()))

        start = time.time()

        sub = Subscriber(name='c1', sub_id=1, hostname=hostname, port=port, sub_buffer=sub_buffer, publishers_no=max_publishers_no,
                         topic=topic, qos=QOS, auth=auth, uname=username, pwd=password, max_count=max_messages)
        sub.start()

        for i in range(max_publishers_no):
            # sub = Subscriber(name='c'+str(i+1), sub_id=i, hostname=hostname, port=port, sub_buffer=sub_buffer, topic=topic + '/' + str(i+1), qos=QOS, auth=True, uname=username, pwd=password, max_count=50)
            pub = Publisher(name='c'+str(i+1), pub_id=i, hostname=hostname, port=port, pub_buffer= pub_buffer, topic=topic, qos=QOS, auth=auth, uname=username, pwd=password, max_count=max_messages)
            # subscribers.append(sub)
            # sub.start()
            publishers.append(pub)
            pub.start()

        for client in publishers:
            client.join()
            try:
                ret = pub_buffer.get()
                # print('[INFO] pub_buffer ret : {}'.format(ret))
                print_event(ret)
                publishers_mean_dur.append(ret['msg_mean'])
                publishers_bandwidth.append(ret['bandwidth'])
                print('[DEBUG] Publishers completed : {}' .format(len(publishers_mean_dur)))
                # print_table(ret)
            except ValueError as error:
                print('[ERROR] Queue : {}'.format(error))
        #
        # for client in subscribers:
        #     # print('[DEBUG] client alive : {}' .format(client.is_alive()))
        #     if client.is_alive():
        #         client.join()
        #     try:
        #         ret = sub_buffer.get()
        #         # print('[INFO] sub_buffer ret : {}'.format(ret))
        #         print_event(ret)
        #     except ValueError as error:
        #         print('[ERROR] Queue : {}'.format(error))



        if sub.is_alive():
            print('[DEBUG] Waiting for the subscription messages ...')
            sub.join()
        try:
            ret = sub_buffer.get()
            # print('[INFO] sub_buffer ret : {}'.format(ret))
            # print_event(ret)
            print_config(np.average(np.array(publishers_mean_dur)), np.average(np.array(publishers_bandwidth)))
            print_table(ret)
        except ValueError as error:
            print('[ERROR] Queue : {}'.format(error))

        # print('[DEBUG] Mean Duration: {}, Bandwidth: {}' .format(mean, bandwidth))

        end = round(time.time() - start, 3)
        print('[INFO] Test Completed in {} seconds' .format(end))
    except KeyboardInterrupt:
        print('Exiting ...')

    except Exception as error  :
        print('[ERROR] main {}' .format(error))

if __name__ == '__main__':
    main()