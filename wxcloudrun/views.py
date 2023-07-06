import json
from datetime import datetime
from flask import render_template, request, jsonify, Response, stream_with_context
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests
from sse_starlette.sse import ServerSentEvent, EventSourceResponse


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

@app.route('/getAnswer', methods=['POST'])
def answer():
    requestData = json.loads(request.data)
    a = requests.post(url='https://api.miragari.com/fast/wxChat',json={'question':requestData['question']})
    return jsonify({"answer": json.loads(a.text)['choices'][0]['message']['content']})

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


def event_stream():
    count = 0
    while True:
        count += 1
        yield f"data: {count}\n\n"


def generate(q):
    response = requests.get(f"https://api.miragari.com/fast/streamChat?q={q}", stream=True)
    for chunk in response.iter_lines():
        chunkStr = chunk.decode('utf-8')
        if chunkStr.startswith('data'):
            chunkJson = json.loads(chunkStr[6:])
            if (type(chunkJson) == dict):
                chunkRes = chunkJson['choices'][0]['delta']
                if 'content' in chunkRes and 'role' not in chunkRes:
                    yield chunkRes['content'].encode('utf-8')

@app.route('/streamChat', methods=['GET'])
def create_stream():
    q = request.args.get('q')
    return Response(generate(q), mimetype="text/event-stream")
