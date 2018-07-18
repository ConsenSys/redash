import os
import logging
import boto3
import requests
import simplejson
import json
import re
import itertools
import datetime

import redash.models

from flask import request
from flask_login import current_user
from redash.query_runner import *
from redash.utils import JSONEncoder
from redash.settings import array_from_string


logger = logging.getLogger(__name__)

types_map = {
    'Timestamp': TYPE_DATETIME,
    'SampleCount': TYPE_FLOAT,
    'Average': TYPE_FLOAT,
    'Sum': TYPE_FLOAT,
    'Minimum': TYPE_FLOAT,
    'Maximum': TYPE_FLOAT,
    'Unit': TYPE_STRING,
    'ExtendedStatistics': TYPE_FLOAT
}

def list_all_ns_metrics(client, ns):
    options = {}

    if ns is not None and ns != '*':
        options['Namespace'] = ns

    curr = client.list_metrics(**options)
    result = curr.get('Metrics')

    while 'NextToken' in curr:
        options['NextToken'] = curr.get('NextToken')
        curr = client.list_metrics(**options)
        result += curr.get('Metrics')
    
    return result


class CloudWatch(BaseQueryRunner):
    def run_query(self, query, user):
        try:
            json_queries = simplejson.loads(query)
            data = { 'columns' : [], 'rows': [] }

            if type(json_queries) is not list:
                json_queries = [json_queries]
            print json_queries
            for json_query in json_queries:
                extra_data = json_query.pop('Extra', None)
                past_value = json_query.pop('Past', 604800)

                if json_query.get('Period', None) is None and json_query.get('StartTime', None) is None:
                    past_interval = int(past_value)
                    json_query['StartTime'] = (datetime.datetime.now() - datetime.timedelta(seconds=past_interval)).isoformat()
                    json_query['Period'] = int(past_interval / 1440) + (past_interval % 1440 > 0)

                if json_query.get('StartTime', None) is None:
                    json_query['StartTime'] = (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat()

                if json_query.get('EndTime', None) is None:
                    json_query['EndTime'] = datetime.datetime.now().isoformat()
                    
                client = self._get_client()
                response = client.get_metric_statistics(**json_query)

                statistic_columns = [(s, types_map.get(s, None)) for s in json_query.get('Statistics', [])]
                extended_columns = [(e, TYPE_FLOAT) for e in json_query.get('ExtendedStatistics', [])]
                extra_columns = [(e, TYPE_STRING) for e in extra_data.keys()]
                columns = self.fetch_columns([('Timestamp', TYPE_DATETIME)] + statistic_columns + extended_columns + extra_columns)
                rows = response.get('Datapoints', [])

                for r in rows:
                    for c, e in extra_data.iteritems():
                        r[c] = e
                
                data['columns'] = columns
                data['rows'] += rows
            error = None
            json_data = json.dumps(data, cls=JSONEncoder)
        except (KeyboardInterrupt, InterruptException):
            error = "Query cancelled by user"
            json_data = None
        return json_data, error

    def test_connection(self):
        client = self._get_client()
        client.list_metrics()
        return True

    def get_schema(self, get_stats=False):
        client = self._get_client()
        response = list(itertools.chain.from_iterable(list_all_ns_metrics(client, ns) for ns in self.whitelist))
        schema = {}
        namespaces = []

        for metric in response:
            name = metric['MetricName']
            ns = metric['Namespace']

            if name not in schema:
                schema[name] = { 'name': name, 'columns': [], 'ns': ns }
            if ns not in namespaces:
                namespaces.append(ns)
                
            schema[name]['columns'] = list(set(schema[name]['columns'] + ['%s=%s' % (dim['Name'], dim['Value']) for dim in metric['Dimensions']]))

        if len(namespaces):
            schema['meta'] = { 'name': '_ns', 'columns' : namespaces }

        return schema.values()

    @property
    def whitelist(self):
        _namespaces = self.configuration.get('namespaces', '*')

        if _namespaces is '*':
            return [None]
        
        return array_from_string(_namespaces)

    @classmethod
    def annotate_query(cls):
        return False

    @classmethod
    def cacheable(cls):
        return False

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "id": {
                    "title": "Access Key ID",
                    "type": "string"
                },
                "key": {
                    "title": "Secret Access Key",
                    "type": "string"
                },
                "region": {
                    "title": "Default Region",
                    "type": "string",
                    "options": [
                        "us-east-1",
                        "us-east-2",
                        "us-west-1",
                        "us-west-2",
                        "ap-northeast-1",
                        "ap-northeast-2",
                        "ap-northeast-3",
                        "ap-south-1",
                        "ap-southeast-1",
                        "ap-southeast-2",
                        "ca-central-1",
                        "cn-north-1",
                        "cn-northwest-1",
                        "eu-central-1",
                        "eu-west-1",
                        "eu-west-2",
                        "eu-west-3",
                        "sa-east-1",
                        "us-gov-west-1"
                    ],
                    "default": "us-east-1"
                },
                "namespaces": {
                    "title": "Namespace Whitelist",
                    "type": "string",
                    "default": "*"
                }
            },
            "required": ["id", "key", "region", "namespaces"],
            "secret": ["key"],
            "order": ["id", "key", "region", "namespaces"]
        }

    def _get_client(self):
        return boto3.client(
            'cloudwatch',
            aws_access_key_id=self.configuration.get('id'),
            aws_secret_access_key=self.configuration.get('key'),
            region_name=self.configuration.get('region')
        )


register(CloudWatch)