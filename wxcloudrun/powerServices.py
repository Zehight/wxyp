import json

import requests

from datetime import datetime
class Snowflake:
    """
    实现雪花算法的类
    """
    def __init__(self, datacenter_id, machine_id, sequence=0, epoch=datetime(1970, 1, 1)):
        # 数据中心ID，占5位，取值范围为0-31
        self.datacenter_id = datacenter_id
        # 机器ID，占5位，取值范围为0-31
        self.machine_id = machine_id
        # 序列号，占12位，取值范围为0-4095
        self.sequence = sequence
        # 起始时间戳，单位为毫秒，默认为1970-01-01 00:00:00
        self.epoch = epoch
        # 当前时间戳，初始值为None
        self.timestamp = None

    def generate_id(self):
        """
        生成一个新的唯一ID
        """
        # 获取当前时间戳（以毫秒为单位）
        now = int((datetime.utcnow() - self.epoch).total_seconds() * 1000)

        # 检查时间戳是否回退
        if self.timestamp is not None and now < self.timestamp:
            raise ValueError("时钟倒退，请等待 %d 毫秒后再生成ID" % (self.timestamp - now))

        # 如果在同一毫秒内调用，递增序列号
        if self.timestamp == now:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                now = self.wait_for_next_millisecond()
        else:
            self.sequence = 0

        # 保存当前时间戳和其他参数，以便下一次调用
        self.timestamp = now
        datacenter_id = self.datacenter_id & 31
        machine_id = self.machine_id & 31

        # 生成并返回一个新ID
        return ((now << 22) | (datacenter_id << 17) | (machine_id << 12) | self.sequence)

    def wait_for_next_millisecond(self):
        """
        等待直到下一毫秒，然后返回新的时间戳
        """
        now = int((datetime.utcnow() - self.epoch).total_seconds() * 1000)
        while now <= self.timestamp:
            now = int((datetime.utcnow() - self.epoch).total_seconds() * 1000)
        return now
snowflake = Snowflake(0, 0, 0, datetime(2023, 1, 1))


def getAnswer(question):
    a = requests.post(url=f'https://api.miragari.com/fast/wxChat', json={'question': question})
    print(json.loads(a.text))
    return json.loads(a.text)['choices'][0]['message']['content']


answers = {}


def genStreamAnswer(question, id):
    answers[id] = ''
    response = requests.get(f"https://api.miragari.com/fast/streamChat?q={question}", stream=True)
    for chunk in response.iter_lines():
        chunkStr = chunk.decode('utf-8')
        if chunkStr.startswith('data: {'):
            chunkJson = json.loads(chunkStr[6:])
            print(chunkJson)
            if type(chunkJson) == dict:
                chunkRes = chunkJson['choices'][0]['delta']
                if chunkJson['choices'][0]['finish_reason'] == 'stop':
                    answers[id] = '完成：'+answers[id]
                if 'content' in chunkRes and 'role' not in chunkRes:
                    answers[id] += chunkRes['content']


import threading


def streamAnswer(question):
    id = str(snowflake.generate_id())
    threading.Thread(target=genStreamAnswer, args=(question, id)).start()
    # 返回结果
    return {'id': id}


def getStreamAnswer(id):
    # 返回结果
    if id not in answers:
        return {'result': ''}
    result = answers[id]
    if result.startswith('完成：'):
        del answers[id]
    return {'result': result}
