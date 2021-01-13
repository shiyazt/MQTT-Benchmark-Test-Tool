import random
import paho.mqtt.client as mqtt
import time
from multiprocessing import Process
import numpy as np
import sys
from tqdm import tqdm
import statistics
import json
from datetime import datetime

def getRandomNumber(min, max):
    return random.uniform(min, max)


class Subscriber(Process):
    def __init__(self, name, sub_id, hostname, sub_buffer, publishers_no, port=1883, topic=None, timeout=60,
                 qos=0, auth=False, uname=None, pwd=None, max_count=10):
        try:
            Process.__init__(self)
            self._buffer = sub_buffer
            self._sub_deltas = list()
            self._sub_msgSizes = list()
            self._successMsgs = 0
            self._failureMsgs = 0
            self._name = name
            self._id = sub_id
            self._hostname = hostname
            self._port = port
            self._topic = topic
            self._timeout = timeout
            self._qos = qos
            self._auth = False
            self._username = None
            self._password = None
            self._max_msg_count = max_count
            self._msg_count = 0
            if auth:
                self._auth = True
                self._username = uname
                self._password = pwd

            self._client = None
            self._connected = False
            self._running = False

            # Timing Fields
            # self._start_ts = None
            # self._end_ts = None
            self._sub_start_ts = None
            self._sub_end_ts = None

            self._publishers_no = publishers_no
            # self._total_msg_limit = self._max_msg_count * self._publishers_no

        except Exception as error:
            self.print_debug('[ERROR] Publisher : {}' .format(error))

    def calculateSatistics(self):
        try:
            mean = round(np.mean(np.array(self._sub_deltas)) * 1000, 6) if len(self._sub_deltas) > 0 else 0
            max_duration = max(self._sub_deltas) * 1000 if len(self._sub_deltas) > 0 else 0
            min_duration = min(self._sub_deltas) * 1000 if len(self._sub_deltas) > 0 else 0
            average = round(np.average(np.array(self._sub_deltas)) * 1000, 6) if len(self._sub_deltas) > 0 else 0
            std = round(np.std(np.array(self._sub_deltas)) * 1000, 6) if len(self._sub_deltas) > 0 else 0
            bandwidth = round(1000 / (np.mean(np.array(self._sub_deltas)) * 1000), 4) if len(self._sub_deltas) > 0 else 0
            return {
                    'entity': 'subscriber',
                    'name': self._name,
                    'id': self._id,
                    'msg_mean': mean,
                    'msg_average': average,
                    'msg_std': std,
                    'msg_max': max_duration,
                    'msg_min': min_duration,
                    'msg_received': self._successMsgs,
                    'max_msg_count': self._max_msg_count,
                    'success-rate': round(self._successMsgs / self._max_msg_count * 100, 3),
                    'failure-rate': round(self._failureMsgs / self._max_msg_count * 100, 3),
                    'bandwidth': bandwidth,
                    'recv_bytes_permsg' : round(statistics.mean(self._sub_msgSizes), 4),
                    'recv_bytes' : round((sum(self._sub_msgSizes)) / self._sub_end_ts, 4) / 1024,
                    'total_duration': self._sub_end_ts,
            }
        except Exception as error:
            self.print_debug('[ERROR] calculateSatistics : {}' .format(error))

    def run(self):
        # self.print_debug('[DEBUG] Process : {}' .format(current_process().name))
        try:
            self._sub_start_ts = time.time()
            progress_bar = tqdm(total=self._max_msg_count)
            def on_connect(client, userdata, flags, rc):
                # self.print_debug('[INFO] client connection with rc : {}' .format(rc))
                if rc == 0:
                    self._connected = True
                    self.print_debug('[INFO] client connection ...[OK]')
                    self._client.subscribe(self._topic, self._qos)
                else:
                    self._connected = False
                    raise Exception('Connection Problem')

            def on_message(client, userdata, msg):

                if msg.topic == self._topic:
                    # self.print_debug('[DEBUG] msg received, count : {0}, total: {1}' .format(self._msg_count, self._total_msg_limit))
                    if self._msg_count < self._max_msg_count:
                        progress_bar.update(1)
                        self._msg_count += 1
                        self._successMsgs += 1
                        delta = round(time.time() - json.loads(msg.payload)['timestamp'], 4)
                        self._sub_deltas.append(delta)
                        self._sub_msgSizes.append(sys.getsizeof(msg.payload))
                    else:
                        self.print_debug('[ERROR] Max Message Received Limit Exceeded')
                else:
                    self.print_debug('[ERROR] Unknown Message Topic : {}' .format(msg.topic))

            self._running = True
            self._client = mqtt.Client()
            self._client.on_connect = on_connect
            self._client.on_message = on_message
            if self._auth:
                self._client.username_pw_set(username=self._username, password=self._password)
            self._client.connect(self._hostname, self._port)
            self._client.loop_start()

            while not self._connected:
                # self.print_debug('[INFO] Waiting for connection ...')
                time.sleep(1)


            while True:
                # self.print_debug('[DEBUG] msg_count: {}, max: {}' .format(self._msg_count, self._max_msg_count))
                if self._msg_count >= self._max_msg_count:
                    self.print_debug('[INFO] Stopping ....')
                    break
                if time.time() - self._sub_start_ts > self._timeout:
                    # raise Exception('Subscriber Timeout Reached')
                    self.print_debug('[INFO] Subscriber Timeout Reached')
                    break
                time.sleep(0.5)

            progress_bar.close()
            self.print_debug('[INFO] Subscriber Stopping ...')
            self._client.loop_stop()
            self._client.disconnect()
            self._sub_end_ts = round(time.time() - self._sub_start_ts, 3)
            # self.print_debug(self.calculateSatistics())
            self._buffer.put(self.calculateSatistics())
            # self._buffer.task_done()
            self.print_debug('[INFO] Subscriber Stopped ...[OK]')

        except Exception as error:
            self.print_debug('[ERROR] run {}' .format(error))
            if self._connected:
                self._client.loop_stop()
                self._client.disconnect()
                self._sub_end_ts = round(time.time() - self._sub_start_ts, 3)
                # self.print_debug(self.calculateSatistics())
                self._buffer.put(self.calculateSatistics())
                # self._buffer.task_done()
            else:
                self.print_debug('[ERROR] Connection Failed')

    def print_debug(self, msg):
        print('\r {} entity : {}, client : {}, msg : {}' .format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'subscriber', self._id, msg))


