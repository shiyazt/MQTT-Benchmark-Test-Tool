import random
import paho.mqtt.client as mqtt
import json
import time
from multiprocessing import Process
import numpy as np
# from tqdm import tqdm


def getRandomNumber(min, max):
    return random.uniform(min, max)

def generateMsg(name):
    return {
        "name": name,
        "id": random.randint(10,100),
        "temperature": getRandomNumber(18,27),
        "humidity": getRandomNumber(50,61)
    }


class Publisher(Process):
    ps_start_time = 0
    clients = 0
    def __init__(self, name, pub_id, hostname, pub_buffer, port=1883, topic=None, timeout=60, max_count=10, qos=0, auth=False, uname=None, pwd=None):
        try:
            Process.__init__(self)
            self._buffer = pub_buffer
            self._pub_deltas = list()
            self._successMsgs = 0
            self._failureMsgs = 0
            self._name = name
            self._id = pub_id
            self._hostname = hostname
            self._port = port
            self._topic = topic
            self._timeout = timeout
            self._max_msg_count = max_count
            self._qos = qos
            self._msg = generateMsg,
            self._auth = False
            self._username = None
            self._password = None
            if auth:
                self._auth = True
                self._username = uname
                self._password = pwd

            self._client = None
            self._connected = False
            self._running = False

            # Timing Constant Fields
            self._start_ts = None
            self._end_ts = None
            self._pub_start_ts = time.time()
            self._pub_end_ts = None
            self._max_retry_attempts = 10
            self._retry_attempts = 0

            # self.lock = Lock()
        except Exception as error:
            self.print_debug('[ERROR] Publisher : {}' .format(error))

    def calculateSatistics(self):
        try:
            mean = round(np.mean(np.array(self._pub_deltas)) * 1000, 6) if len(self._pub_deltas) > 0 else 0
            max_duration = max(self._pub_deltas) * 1000 if len(self._pub_deltas) > 0 else 0
            min_duration = min(self._pub_deltas) * 1000 if len(self._pub_deltas) > 0 else 0
            average = round(np.average(np.array(self._pub_deltas)) * 1000, 6) if len(self._pub_deltas) > 0 else 0
            std = round(np.std(np.array(self._pub_deltas)) * 1000, 6) if len(self._pub_deltas) > 0 else 0
            bandwidth = round(1000 / (np.mean(np.array(self._pub_deltas)) * 1000), 4) if len(self._pub_deltas) > 0 else 0
            return {
                    'entity': 'publisher',
                    'name': self._name,
                    'id': self._id,
                    'type': 'info',
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
                    'total_duration': self._pub_end_ts,
            }
        except Exception as error:
            self.print_debug('[ERROR] calculateSatistics : {}' .format(error))

    def run(self):
        # self.print_debug('[DEBUG] Process : {}'.format(current_process().name))
        try:
            def on_connect(client, userdata, flags, rc):
                # self.print_debug('[INFO] client connection with rc : {}' .format(rc))
                if rc == 0:
                    self._connected = True
                    # self.print_debug('[INFO] client connection ...[OK]')
                    self._pub_start_ts = time.time()
                    Publisher.clients += 1
                else:
                    self._connected = False

            def on_message(client, userdata, msg):
                self.print_debug('[INFO] on_message : {}' .format(client))

            def on_publish(client, userdata, mid):
                # self.print_debug('[DEBUG] mid:{}' .format(mid))
                # self.print_debug('Msg took {} secs' .format(round((time.time() - self._start_ts), 6)))
                self._pub_deltas.append(round(time.time() - self._start_ts, 6))
                self._start_ts = time.time()

            if time.time() - Publisher.ps_start_time < self._timeout:
                self._running = True
                self._client = mqtt.Client()
                self._client.on_connect = on_connect
                self._client.on_message = on_message
                self._client.on_publish = on_publish
                if self._auth:
                    self._client.username_pw_set(username=self._username, password=self._password)
                # self.print_config()
                self._client.connect(self._hostname, self._port)
                self._client.loop_start()

                # self.lock.acquire()
                while not self._connected:
                    if self._retry_attempts <= self._max_retry_attempts and time.time() - Publisher.ps_start_time < self._timeout:
                        # self.print_debug('[INFO] Waiting for connection ...')
                        self._retry_attempts += 1
                        time.sleep(5)
                    else:
                        # self._buffer.put({
                        #     'entity': 'publisher',
                        #     'name': self._name,
                        #     'id': self._id,
                        #     'type': 'error',
                        #     'code': 430
                        # })
                        raise Exception('Retry time exceeded')

                # self.lock.release()

                for _ in range(self._max_msg_count):
                    if time.time() - Publisher.ps_start_time <= self._timeout:
                        msg = generateMsg(self._name)
                        # self.print_debug('[INFO] counter : {}, msg : {}' .format(i, msg))
                        # if not self._start_ts:
                        self._start_ts = time.time()
                        ret = self._client.publish(self._topic, json.dumps(msg), self._qos)
                        if ret[0] == 0:
                            self._successMsgs += 1
                        elif ret[0] == 1:
                            self._failureMsgs += 1
                            # raise Exception('MQTT No Connection')
                        time.sleep(0.1)
                        # self.print_debug('[DEBUG] publish_ret : {}' .format(ret))
                    else:
                        raise Exception('Publisher Timeout reached !')

                self._client.disconnect()
                self._pub_end_ts = round(time.time() - self._pub_start_ts, 3)
                # self.print_debug('[DEBUG] send {0} messages in {1} seconds' .format(self._max_msg_count, self._pub_end_ts))
                self._buffer.put(self.calculateSatistics())
                # self.print_debug('[INFO] Publisher Stopped ...[OK]')

        except (Exception, KeyboardInterrupt) as error:
            # self.print_debug('[ERROR] run {}' .format(error))
            if self._connected:
                self._client.disconnect()
                self._pub_end_ts = round(time.time() - self._pub_start_ts, 3)
                # self.print_debug('[DEBUG] send {0} messages in {1} seconds' .format(self._max_msg_count, self._end_time))
                self._buffer.put(self.calculateSatistics())
                # self._buffer.task_done()
            else:
                # self.print_debug('[ERROR] Connection Falied')
                self._buffer.put({
                        'entity': 'publisher',
                        'name': self._name,
                        'id': self._id,
                        'type': 'error',
                        'code': 430
                })

    def print_debug(self, msg):
        print('\r entity : {0}, client : {1}, msg : {2}' .format('publisher', self._id, msg))


    def print_config(self):
        self.print_debug('[DEBUG] hostname: {}, port: {}, qos: {}' .format(self._hostname, self._port, self._qos))

    @property
    def getClientName(self):
        return self._name