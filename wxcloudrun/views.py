import json
from flask import render_template, request, jsonify
from run import app
import requests
from .powerServices import streamAnswer as powerStreamAnswer
from .powerServices import getStreamAnswer as powerGetStreamAnswer

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
    result = powerStreamAnswer(requestData['question'])
    return jsonify(result)


@app.route('/getStreamAnswer', methods=['POST'])
def get_chat():
    requestData = json.loads(request.data)
    result = powerGetStreamAnswer(requestData['id'])
    return jsonify(result)
