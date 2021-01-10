from multiprocessing import cpu_count, JoinableQueue, Pool, Queue
import time
from mqtt_publisher import Publisher
from mqtt_subscriber import Subscriber
from prettytable import PrettyTable
import numpy as np
import statistics
import sys
from app_constants import Error

subscribers = []
publishers = []
publishers_mean_dur = []
publishers_max_dur = []
publishers_min_dur = []
publishers_bandwidth = []

publishers_success_msgs = []
publishers_error_msgs = []

subscribers_msgs = []

# pub_buffer = JoinableQueue()
pub_buffer = Queue()
sub_buffer = Queue()
# sub_buffer = JoinableQueue()

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
        print('{} {} stats: msg_mean: {}ms, msg_average: {}ms, '
              'msg_std: {}ms, msg_max: {}ms, msg_min:{}ms '
              'msg_success_rate : {} % ({}/{}), total_duration: {} seconds, '
              'bandwidth : {} msg/second'
              .format(msg['entity'], msg['name'], msg['msg_mean'], msg['msg_average'], msg['msg_std'],
                      msg['msg_max'], msg['msg_min'], msg['success-rate'], msg['msg_received'],
                      msg['max_msg_count'], msg['total_duration'], msg['bandwidth'])
              )
    except Exception as error:
        print('[ERROR] print_event ')
        print(error)




def print_config(hostname, port, max_publishers_no, QOS, max_messages, timeout):
    try:
        table = PrettyTable()
        table.title = "Test Description"
        table.field_names = ["Fields", "Value", "Unit"]
        total_msgs = max_publishers_no * max_messages
        table.add_rows([
            ["Hostname", hostname, ''],
            ["Port", port, 'MQTT'],
            ["QoS", QOS, ''],
            ["Publishers", max_publishers_no, 'Nos'],
            ["Messages/Publisher", max_messages, "Msg's"],
            ["Total Msgs", total_msgs, "Msg's"],
            ["Test Timeout", timeout, "Seconds"]
        ])
        print(table)
    except Exception as error:
        print('[ERROR] print_config ')
        print(error)



def print_subscriber_stats(msg):
    try:
        table = PrettyTable()
        table.title = msg['entity'] + ' ' + msg['name']
        table.field_names = ["Fields", "Value", "Unit"]
        table.add_rows([
            ["Msgs Received", msg['msg_received'], "No's"],
            ["Total Msgs", msg['max_msg_count'], "No's"],
            ["Msg Duration Mean", round(msg['msg_mean'], 3), "ms"],
            ["Msg Duration Average", round(msg['msg_average'], 3), "ms"],
            ["Msg Duration Std", round(msg['msg_std'], 3), "ms"],
            ["Msg Duration Max", round(msg['msg_max'], 3), "ms"],
            ["Msg Duration Min", round(msg['msg_min'], 3), "ms"],
            ["Success Rate", round(msg['success-rate'], 3), "%"],
            ["Failure Rate", round(msg['failure-rate'], 3), "%"],
            ["Bandwidth", round(msg['bandwidth'], 3), "msg/sec"],
            ["Avg Payload Size per publisher", round(msg['recv_bytes_permsg'], 3), "Bytes"],
            ["Throughput", round(msg['recv_bytes'], 3), "Kbps"],
            ["Duration", round(msg['total_duration'], 3), "Seconds"]
        ])
        print(table)
    except Exception as error:
        print(f'print_subscriber_stats: {error}')


def print_publisher_stats(msg):
    try:
        table = PrettyTable()
        table.title = 'Average Publisher Statistics'
        table.field_names = ["Fields", "Value", "Unit"]
        table.add_rows([
            ["Msg Duration Mean", round(msg['msg_mean'], 4), "ms"],
            ["Msg Duration Std", round(msg['msg_std'], 4), "ms"],
            ["Msg Duration Max", round(msg['msg_max'], 4), "ms"],
            ["Msg Duration Min", round(msg['msg_min'], 4), "ms"],
            ["Total Publishers", msg['total_publishers'], "No's"],
            ["Active Publishers", msg['active_publishers'], "No's"],
            ["Inactive Publishers", msg['inactive_publishers'], "No's"],
            ["Bandwidth (msg's/sec)", round(msg['bandwidth'], 4), "msg/sec"]
        ])
        print(table)
    except Exception as error:
        print(f'print_publisher_stats: {error}')

def parseDataFromPub(client):
    try:
        # print('[DEBUG] parseDataFromPub')
        if client.is_alive():
            # print('[DEBUG] Publisher: {} closing ....' .format(client.getClientName))
            client.join(timeout=5)
            # print('[DEBUG] Publisher: {} closed ...[OK]'.format(client.getClientName))
        try:
            ret = pub_buffer.get(timeout=5)
            print('[INFO] pub_buffer ret : {}'.format(ret))
            # print_event(ret)
            publishers_mean_dur.append(ret['msg_mean'])
            publishers_max_dur.append(ret['msg_max'])
            publishers_min_dur.append(ret['msg_min'])
            publishers_bandwidth.append(ret['bandwidth'])
            # print('[DEBUG] Publishers completed : {}' .format(len(publishers_mean_dur)))
            # print_table(ret)
        except (ValueError, Exception) as error:
            print('[ERROR] This Publisher is waste')

    except Exception as error:
        print(f'[ERROR] parseDataFromPub : {error}')


def publisher_error_handler(pub_name, pub_id, msg_type, code):
    try:

        if code == Error.conn_timeout.value:
            # print(f'constant_value : {Error.conn_timeout}')
            publishers_error_msgs.append({
                'name': pub_name,
                'id': pub_id,
                'msg_type': msg_type,
                'code': code
            })
    except Exception as error:
        print(f'[ERROR] publisher_error_handler : {error}')


def publisher_data_parser(msg):
    try:
        if msg['entity'] == 'publisher':
            if msg['type'] == 'error':
                publisher_error_handler(pub_name=msg['name'], pub_id=msg['id'], msg_type=msg['type'], code=msg['code'])
            elif msg['type'] == 'info':
                publishers_success_msgs.append(msg)
                publishers_mean_dur.append(msg['msg_mean'])
                publishers_max_dur.append(msg['msg_max'])
                publishers_min_dur.append(msg['msg_min'])
                publishers_bandwidth.append(msg['bandwidth'])
    except Exception as error:
        print(f'[ERROR] publisher_data_parser : {error}')


def start(topic, auth, hostname='localhost', port=1883, max_publishers_no=10,
          username=None, password=None, QOS=0, max_messages=50, timeout=60):
    try:

        print('Number of cpu : {}' .format(cpu_count()))
        start_time = time.time()
        publisher_cnt = 0

        sub = Subscriber(name='c1', sub_id=1, hostname=hostname, port=port, sub_buffer=sub_buffer, publishers_no=max_publishers_no,
                         topic=topic, qos=QOS, auth=auth, uname=username, pwd=password, max_count=max_messages * max_publishers_no, timeout=timeout)
        sub.start()
        Publisher.ps_start_time = time.time()

        for i in range(max_publishers_no):
            # sub = Subscriber(name='c'+str(i+1), sub_id=i, hostname=hostname, port=port, sub_buffer=sub_buffer, topic=topic + '/' + str(i+1), qos=QOS, auth=True, uname=username, pwd=password, max_count=50)
            pub = Publisher(name='c'+str(i+1), pub_id=i, hostname=hostname, port=port, pub_buffer= pub_buffer, topic=topic, qos=QOS, auth=auth, uname=username, pwd=password, max_count=max_messages, timeout=timeout)
            # subscribers.append(sub)
            # sub.start()
            publishers.append(pub)
            pub.daemon = True
            pub.start()

        # print('[DEBUG] waiting in queue ...')
        pub_msg_cnt = 0
        while time.time() - start_time < timeout:
            if not pub_buffer.empty():
                ret = pub_buffer.get_nowait()
                # print(f"ret: {ret}")
                pub_msg_cnt += 1
                publisher_data_parser(ret)
            else:
                if pub_msg_cnt < max_publishers_no:
                    time.sleep(0.5)
                else:
                    break

        if sub.is_alive():
            # print('[DEBUG] Waiting for the subscription messages ...')
            sub.join(timeout=5)
        try:
            ret = sub_buffer.get(timeout=5)
            # print('[INFO] sub_buffer ret : {}'.format(ret))
        except ValueError as error:
            print('[ERROR] Queue : {}'.format(error))

        # print('[DEBUG] Mean Duration: {}, Bandwidth: {}' .format(mean, bandwidth))

        end = round(time.time() - start_time, 3)

        # print(f'[INFO] Total No of Publishers : {len(publishers)}')
        # print(f'[INFO] No of Active Publishers : {len(publishers_success_msgs)}')
        # print(f'[INFO] No of Inactive Publishers : {len(publishers_error_msgs)}')
        # print(f'[INFO] Mean Duration: {statistics.mean(publishers_mean_dur)}')
        # print(f'[INFO] Max Duration: {max(publishers_max_dur)}')
        # print(f'[INFO] Min Duration: {min(publishers_min_dur)}')
        # print(f'[INFO] Std Duration: {statistics.stdev(publishers_mean_dur)}')
        # print(f'[INFO] Bandwidth: {statistics.mean(publishers_bandwidth)}')
        # print(f'[INFO] Size of: {sys.getsizeof(publishers_success_msgs)} bytes')

        print_config(hostname=hostname, port=port, max_publishers_no=max_publishers_no, QOS=QOS, max_messages=max_messages, timeout=timeout)

        print_publisher_stats({
            'msg_mean': statistics.mean(publishers_mean_dur),
            'msg_std': statistics.stdev(publishers_mean_dur),
            'msg_max': max(publishers_max_dur),
            'msg_min': min(publishers_min_dur),
            'total_publishers': len(publishers),
            'active_publishers': len(publishers_success_msgs),
            'inactive_publishers': len(publishers_error_msgs),
            'bandwidth': statistics.mean(publishers_bandwidth)
        })
        print_subscriber_stats(ret)
        print('[INFO] Test Completed in {} seconds'.format(end))
        print('[INFO] Exiting ...')
        start = time.time()
        for client in publishers:
            if client.is_alive():
                client.join()
        if sub.is_alive():
            sub.join()
        # print(f'Cleaning took {time.time() - start} seconds')
    except KeyboardInterrupt:
        print('Exiting ...')

    except Exception as error:
        print('[ERROR] main : {}' .format(error))
        sys.exit()

