import time
from multiprocessing import Process, current_process, cpu_count, JoinableQueue
import multiprocessing

class Publisher(Process):
    def __init__(self, name, hostname, port, buffer):
        Process.__init__(self)
        self._hostname = hostname
        self._port = port
        self._name = name
        self._startTime = None
        self._delta = None
        self._buffer = buffer

    def run(self):
        try:
            self._startTime = time.time()
            print('[DEBUG] Process : {} started' .format(current_process().name))
            time.sleep(5)
            print('[DEBUG] {} Publisher Sent Finished' .format(self._name))
            self._delta = round(time.time() - self._startTime, 3)
            print('[DEBUG] {0} Publisher Delta : {1}'.format(self._name, self._delta))
            self._buffer.put({
                "name" : self._name,
                "delta" : self._delta
            })
        except Exception as error:
            print('[ERROR] run : {}' .format(error))

    @property
    def getJobDelta(self):
        print(self._delta)
        return self._name, self._delta


if __name__ == "__main__":
    start = time.time()
    publishers = []
    sub_buffer = JoinableQueue()
    for i in range(2000):
        p = Publisher(name='C'+str(i), hostname='10.02.01.15', port=1883, buffer=sub_buffer)
        publishers.append(p)
        p.start()
        # p.join()
        name, delta = p.getJobDelta
        print('Job : {}, completed in {} seconds' .format(name, delta))


    # Waiting for clients to finish job
    for client in publishers:
        client.join()
        # name, delta = client.getJobDelta
        # print('Job : {}, completed in {} seconds'.format(name, delta))
        try:
            ret = sub_buffer.get()
            print('[INFO] ret : {}'.format(ret))
        except ValueError as error:
            print('[ERROR] Queue : {}'.format(error))



    print('[INFO] Process exited in {:.4f} seconds' .format(time.time() - start))