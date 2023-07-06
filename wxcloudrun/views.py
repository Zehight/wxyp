import json
from datetime import datetime
from flask import render_template, request, jsonify, Response, stream_with_context
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests
from sse_starlette.sse import ServerSentEvent, EventSourceResponse
import powerServices


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/getAnswer', methods=['POST'])
def answer():
    requestData = json.loads(request.data)
    a = requests.post(url='https://api.miragari.com/fast/wxChat', json={'question': requestData['question']})
    return jsonify({"answer": json.loads(a.text)['choices'][0]['message']['content']})


@app.route('/streamAnswer', methods=['POST'])
def test_chat():
    requestData = json.loads(request.data)
    result = powerServices.streamAnswer(requestData['question'])
    return jsonify(result)


@app.route('/getStreamAnswer', methods=['POST'])
def get_chat():
    requestData = json.loads(request.data)
    result = powerServices.getStreamAnswer(requestData['id'])
    return jsonify(result)
