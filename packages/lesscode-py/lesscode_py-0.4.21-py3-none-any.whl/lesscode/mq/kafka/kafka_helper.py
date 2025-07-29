# -*- coding: utf-8 -*-
import importlib
import json
import logging
import traceback

from tornado.options import options


class KafkaHelper:
    def __init__(self, **kwargs):
        if kwargs.get("bootstrap_servers"):
            self.bootstrap_servers = kwargs.pop("bootstrap_servers")
        else:
            self.bootstrap_servers = options.kafka_config.get("bootstrap_servers", ["127.0.0.1:9092"])
        if kwargs.get("topic"):
            self.topic = kwargs.pop("topic")
        else:
            raise Exception("missing topic")
        #
        self.sasl_config = {}
        if kwargs.get("username"):
            username = kwargs.pop("username")
        else:
            username = options.kafka_config.get("username")
        if kwargs.get("password"):
            password = kwargs.pop("password")
        else:
            password = options.kafka_config.get("password")
        if username and password:
            self.sasl_config = {
                "sasl_mechanism": "PLAIN",
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_plain_username": username,
                "sasl_plain_password": password
            }
        try:
            kafka = importlib.import_module("kafka")
        except ImportError:
            raise Exception(f"kafka is not exist,run:pip install kafka-python==2.0.2")
        self.api_version = tuple([int(x) for x in kafka.__version__.split(".")])

    def publish(self, value=None, key=None, headers=None, partition=None, timestamp_ms=None, **configs):
        try:
            kafka = importlib.import_module("kafka")
        except ImportError as e:
            raise Exception(f"kafka is not exist,run:pip install kafka-python==2.0.2")
        producer = kafka.KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                       api_version=self.api_version,
                                       **self.sasl_config,
                                       **configs)
        try:
            value = json.dumps(value).encode("utf-8")
            key = json.dumps(key).encode("utf-8")
            future = producer.send(self.topic, value=value, key=key, headers=headers, partition=partition,
                                   timestamp_ms=timestamp_ms)
            record_metadata = future.get(timeout=10)
            data = {
                "topic": self.topic,
                "value": value,
                "key": key,
                "partition": partition if partition else record_metadata.partition,
                "offset": record_metadata.offset
            }
            logging.info(f'send data={data}')
        except Exception:
            logging.error(traceback.format_exc())

    def consume(self, callback, **configs):
        try:
            kafka = importlib.import_module("kafka")
        except ImportError as e:
            raise Exception(f"kafka is not exist,run:pip install kafka-python==2.0.2")
        consumer = kafka.KafkaConsumer(self.topic, bootstrap_servers=self.bootstrap_servers,
                                       api_version=self.api_version,
                                       enable_auto_commit=False,
                                       **self.sasl_config, **configs)
        callback(consumer=consumer)
