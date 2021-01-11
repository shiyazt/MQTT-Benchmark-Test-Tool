# MQTT Benchmark Test Tool

MQTT Protocol Benchmark Test Tool
Version 1.0
----------------------------------

[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/shiyazt/MQTT-Benchmark-Test-Tool/blob/main/LICENSE)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-386/)


### Usage
```
usage: main.py [-h] [--publishers PUBLISHERS] [--hostname HOSTNAME] [--port PORT] [--topic TOPIC] [--auth AUTH] [--username USERNAME] [--password PASSWORD]
               [--qos QOS] [--max_messages MAX_MESSAGES] [--timeout TIMEOUT]

MQTT Benchmark Tool

optional arguments:
  -h, --help            show this help message and exit
  --publishers PUBLISHERS
                        No of publishers for test
  --hostname HOSTNAME   MQTT Broker address
  --port PORT           MQTT Port
  --topic TOPIC         MQTT Topic
  --auth AUTH           MQTT Authentication
  --username USERNAME   MQTT Username
  --password PASSWORD   MQTT Password
  --qos QOS             MQTT QoS
  --max_messages MAX_MESSAGES
                        Max MQTT messages to be sent
  --timeout TIMEOUT     Test Timeout

```

#### Sample Usage
```
python main.py --host localhost --port 1883 --auth True --username <username> --password <password> --publishers 200 --max_messages 3 --timeout 60 --qos 2

        ========================================
                MQTT Benchmark Test Tool 
                            v1.0 
        ========================================
        
Number of cpu : 4
 entity : subscriber, client : 1, msg : [INFO] client connection ...[OK]                                                                       
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 600/600 [00:06<00:00, 99.79it/s]
 entity : subscriber, client : 1, msg : [INFO] Subscriber Stopping ...
 entity : subscriber, client : 1, msg : [INFO] Subscriber Stopped ...[OK]
+------------------------------------------+
|             Test Description             |
+--------------------+-----------+---------+
|       Fields       |   Value   |   Unit  |
+--------------------+-----------+---------+
|      Hostname      | localhost |         |
|        Port        |    1883   |   MQTT  |
|        QoS         |     2     |         |
|     Publishers     |    200    |   Nos   |
| Messages/Publisher |     3     |  Msg's  |
|     Total Msgs     |    600    |  Msg's  |
|    Test Timeout    |     60    | Seconds |
+--------------------+-----------+---------+
+---------------------------------------------+
|         Average Publisher Statistics        |
+-----------------------+-----------+---------+
|         Fields        |   Value   |   Unit  |
+-----------------------+-----------+---------+
|   Msg Duration Mean   |   1.0514  |    ms   |
|    Msg Duration Std   |   0.8124  |    ms   |
|    Msg Duration Max   |   10.367  |    ms   |
|    Msg Duration Min   |   0.187   |    ms   |
|    Total Publishers   |    200    |   No's  |
|   Active Publishers   |    200    |   No's  |
|  Inactive Publishers  |     0     |   No's  |
| Bandwidth (msg's/sec) | 1319.9177 | msg/sec |
+-----------------------+-----------+---------+
+-----------------------------------------------------+
|                    subscriber c1                    |
+--------------------------------+----------+---------+
|             Fields             |  Value   |   Unit  |
+--------------------------------+----------+---------+
|         Msgs Received          |   600    |   No's  |
|           Total Msgs           |   600    |   No's  |
|       Msg Duration Mean        |  9.356   |    ms   |
|      Msg Duration Average      |  9.356   |    ms   |
|        Msg Duration Std        | 181.044  |    ms   |
|        Msg Duration Max        | 4439.331 |    ms   |
|        Msg Duration Min        |  0.019   |    ms   |
|          Success Rate          |  100.0   |    %    |
|          Failure Rate          |   0.0    |    %    |
|           Bandwidth            | 106.885  | msg/sec |
| Avg Payload Size per publisher |  124.3   |  Bytes  |
|           Throughput           |   11.0   |   Kbps  |
|            Duration            |  6.621   | Seconds |
+--------------------------------+----------+---------+
[INFO] Test Completed in 6.637 seconds
[INFO] Exiting ...

```

### Screenshots
![alt text](https://github.com/shiyazt/MQTT_Benchmark_Test_Tool/blob/main/screenshots/1.png)
![alt text](https://github.com/shiyazt/MQTT_Benchmark_Test_Tool/blob/main/screenshots/2.png)


### Reference
[1]: https://pypi.org/project/pymqttbench
