# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from redis import Redis
# from kafka import KafkaProducer
# from pymongo import MongoClient
# import os
#
# app = Flask(__name__)
# app.config.from_object('config.Config')
#
# db = SQLAlchemy(app)
# redis_client = Redis(host='localhost', port=6379, db=0)
# kafka_producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
# mongo_client = MongoClient('localhost', 27017)