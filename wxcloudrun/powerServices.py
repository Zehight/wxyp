import json

import requests

from datetime import datetime
from snowflake import Snowflake

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
                    answers[id] = 'stop'
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
    if result == 'stop':
        del answers[id]
    return {'result': result}
