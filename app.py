# -*- coding: utf-8 -*-
import tensorflow as tf 
import numpy as np
import pandas as pd
import argparse as ap
import os
import uuid
from flask import Flask, render_template, flash, redirect, url_for, request, send_from_directory, session, jsonify
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from validate import LoginForm
from dgaintel import get_prob
from get_data import get_whois, get_ip
import datetime
import mongodb
# from flask_bcrypt import Bcrypt
# import jwt
from flask_restx import Api, Resource, Namespace, fields
# from flask_api_key import APIKeyManager
from bson.json_util import dumps
import json
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super secret')
# my_key_manager = APIKeyManager(app)
# bcrypt = Bcrypt(app)
# SECRET_KEY = 'sdfwaegjwrgoijsdnmfodncvowngowrn2393487295@#%$'
# my_key = my_key_manager.create('abc')
# print(my_key.secret)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    show_predictions_modal=False
    if form.validate_on_submit():
        _prediction = get_prob([form.domain.data])  
        form.whois = get_whois(form.domain.data)
        if _prediction == -1:
            form.prediction = "유효하지 않음 (잘못된 문자열이 포함되어 있습니다.)"
        elif _prediction >= 0.5:
            form.prediction = "DGA Domain ({0:.2f})".format(_prediction)
            dga = True
            form.ip = get_ip(form.domain.data)
            form.whoisIP = get_whois(form.ip)
        else:
            form.prediction = "Legit Domain ({0:.2f})".format(_prediction)
            dga = False
        log = { 'domain':form.domain.data,
                'prob':float(_prediction),
                'dga':dga,
                'date':datetime.datetime.utcnow()
                }
        mongodb.collection.insert_one(log)
        return render_template('mainpage.html', show_predictions_modal=True, form=form)
    return render_template('mainpage.html', show_predictions_modal=False, form=form)

api = Api(app, version='1.0', title='DGATotal REST API', description='API 사용법에 대한 문서', doc="/api/docs", default='DGA API', default_label='DGA 도메인을 예측하거나 이미 예측된 결과를 JSON 형식으로 반환합니다.')

# @api.route('/api/predict/<string:domain>') # 데코레이터 이용, 클래스 등록
# class dgaAPI(Resource):
#     def get(self, domain): # GET 요청
#         prob = get_prob([domain])
#         if prob >= 0.5: # DGA 확률 0.5 이상이면
#             dga = True
#         else:
#             dga = False
#         log = { 'domain':domain,
#                 'prob':float(prob),
#                 'dga':dga,
#                 'date':datetime.datetime.utcnow()
#                 }
#         mongodb.collection.insert_one(log) # DB 로깅
#         return jsonify({"domain":domain, "prob":float(prob), "dga":dga}) # JSON하게 Return

model = api.model('Domain Model', {'domain': fields.String(required=True, description="예측할 도메인 이름", help="Required")})

@api.route('/api/prediction') # 데코레이터 이용, 클래스 등록
class dgaAPI(Resource):
    @api.expect(model)
    def post(self): # POST 요청
        """DGA 도메인인지 딥러닝 모델을 통해 예측하여 반환합니다."""
        body = request.json
        domain = body['domain']
        prob = get_prob([domain])
        if prob >= 0.5: # DGA 확률 0.5 이상이면
            dga = True
        else:
            dga = False
        log = { 'domain':domain,
                'prob':float(prob),
                'dga':dga,
                'date':datetime.datetime.utcnow()
                }
        mongodb.collection.insert_one(log) # DB 로깅
        return jsonify({"domain":domain, "prob":float(prob), "dga":dga}) # JSON하게 Return

def parse_json(data): # JSON 변환
    return json.loads(dumps(data))

@api.route('/api/search/dga') # 데코레이터 이용, 클래스 등록
class dgaAPI(Resource):
    def get(self): # GET 요청
        """쿼리된 DGA 도메인 목록을 조회합니다."""
        data = parse_json(mongodb.collection.find({'dga' : True})) # dga true를 모두 찾기
        return data

@api.route('/api/search/legit') # 데코레이터 이용, 클래스 등록
class dgaAPI(Resource):
    def get(self): # GET 요청
        """쿼리된 Legit 도메인 목록을 조회합니다."""
        data = parse_json(mongodb.collection.find({'dga' : False})) # dga false를 모두 찾기
        return data

@api.route('/api/search') # 데코레이터 이용, 클래스 등록
class dgaAPI(Resource):
    def get(self): # GET 요청
        """쿼리된 모든 도메인 목록을 조회합니다."""
        data = parse_json(mongodb.collection.find()) # 모든 데이터 찾기
        return data


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # app.run(debug=True, host='0.0.0.0', port=5000)