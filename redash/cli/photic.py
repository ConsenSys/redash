import os
import time
import pprint
import json

from flask.cli import AppGroup
from flask_migrate import stamp
from sqlalchemy.exc import DatabaseError

from redash.utils import JSONEncoder

manager = AppGroup(help="Manage photic queries, widgets, and dashboards.")
pp = pprint.PrettyPrinter(indent=4)
ds_ledger = "Ledger API"
ds_stream = "Devops Stream"


def _wait_for_db_connection(db):
    retried = False
    while not retried:
        try:
            db.engine.execute('SELECT 1;')
            return
        except DatabaseError:
            time.sleep(30)

        retried = True


@manager.command()
def queries():
    """Create the cpu query."""
    from redash.models import db, Query

    _wait_for_db_connection(db)
    
    for i, query in enumerate(Query.query):
        if i > 0:
            print("-" * 120)
        pp.pprint(query.to_dict(with_visualizations=True))


@manager.command()
def visualizations():
    """Create the cpu query."""
    from redash.models import db, Visualization

    _wait_for_db_connection(db)
    
    for i, visual in enumerate(Visualization.query):
        if i > 0:
            print("-" * 120)
        pp.pprint(visual.to_dict())


@manager.command()
def dashboards():
    """Create the cpu query."""
    from redash.models import db, Dashboard

    _wait_for_db_connection(db)
    
    for i, dashboard in enumerate(Dashboard.query):
        if i > 0:
            print("-" * 120)
        pp.pprint(dashboard.to_dict(with_widgets=True))


@manager.command()
def widgets():
    """Create the cpu query."""
    from redash.models import db, Widget

    _wait_for_db_connection(db)
    
    for i, widget in enumerate(Widget.query):
        if i > 0:
            print("-" * 120)
        pp.pprint(widget.to_dict())


@manager.command()
def ensure_cpu_query():
    """Create the cpu query."""
    from redash.models import db, Query, Visualization, DataSource

    _wait_for_db_connection(db)

    query_name = "CPU Usage"
    datasource = DataSource.query.filter(DataSource.name == ds_stream)
    # Check for query
    query = Query.query.filter(Query.name == query_name)
    # Add query if it does not exist
    if query is None:
        query = Query.query.filter(
            name=query_name,
            description="",
            query_text=json.dumps({
                "Namespace": "k8s-netplane-" + os.environ.get("ENV"),
                "MetricName": "TotalCPU",
                "Extra": {
                    "Node": "?environment({{consortia_id}}, {{environment_id}})...node_list?"
                },
                "Period": 3600,
                "Statistics": ["Average"],
                "Dimensions": [
                    {
                        "Name": "Namespace",
                        "Value": "{{environment_id}}"
                    },
                    {
                        "Name": "SetName",
                        "Value": "{{environment_id}}-?environment({{consortia_id}}, {{environment_id}})...node_list?-geth-node"
                    }
                ]
            }, cls=JSONEncoder),
            data_source=datasource,
            is_draft=False
        )

        db.session.add(query)
        db.session.commit()


@manager.command()
def ensure_memory_query():
    """Create the memory query."""
    from redash.models import db, Query, Visualization, DataSource

    _wait_for_db_connection(db)

    query_name = "Memory Usage"
    datasource = DataSource.query.filter(DataSource.name == ds_stream)
    # Check for query
    query = Query.query.filter(Query.name == query_name)
    # Add query if it does not exist
    if query is None:
        query = Query.query.filter(
            name=query_name,
            description="",
            query_text=json.dumps({
                "Namespace": "k8s-netplane-" + os.environ.get("ENV"),
                "MetricName": "TotalMemory",
                "Extra": {
                    "Node": "?environment({{consortia_id}}, {{environment_id}})...node_list?"
                },
                "Period": 3600,
                "Statistics": ["Average"],
                "Dimensions": [
                    {
                        "Name": "Namespace",
                        "Value": "{{environment_id}}"
                    },
                    {
                        "Name": "SetName",
                        "Value": "{{environment_id}}-?environment({{consortia_id}}, {{environment_id}})...node_list?-geth-node"
                    }
                ]
            }, cls=JSONEncoder),
            data_source=datasource,
            is_draft=False
        )

        db.session.add(query)
        db.session.commit()


@manager.command()
def ensure_requests_query():
    """Create the requests query."""
    from redash.models import db, Query, Visualization, DataSource

    _wait_for_db_connection(db)

    query_name = "RPC Requests"
    datasource = DataSource.query.filter(DataSource.name == ds_stream)
    # Check for query
    query = Query.query.filter(Query.name == query_name)
    # Add query if it does not exist
    if query is None:
        query = Query.query.filter(
            name=query_name,
            description="",
            query_text=json.dumps({
                "Namespace": "k8s-netplane-" + os.environ.get("ENV"),
                "MetricName": "Requests",
                "Extra": {
                    "Node": "?environment({{consortia_id}}, {{environment_id}})...node_list?"
                },
                "Period": 3600,
                "Statistics": ["Average"],
                "Dimensions": [
                    {
                        "Name": "IngressHost",
                        "Value": "{{environment_id}}-?environment({{consortia_id}}, {{environment_id}})...node_list?-rpc.%s.photic.io" % os.environ.get("ENV")
                    }
                ]
            }, cls=JSONEncoder),
            data_source=datasource,
            is_draft=False
        )

        db.session.add(query)
        db.session.commit()


@manager.command()
def ensure_blocks_query():
    """Create the blocks query."""
    from redash.models import db, Query, Visualization, DataSource

    _wait_for_db_connection(db)

    query_name = "Ledger Blocks"
    datasource = DataSource.query.filter(DataSource.name == ds_ledger)
    # Check for query
    query = Query.query.filter(Query.name == query_name)
    # Add query if it does not exist
    if query is None:
        query = Query.query.filter(
            name=query_name,
            description="",
            query_text=json.dumps({
                "path": "/api/v1/ledger/{{consortia_id}}/{{environment_id}}/blocks",
                "headers": {
                    "Authorization": "Bearer {request.cookies.jwt}"
                },
                "query": {
                    "number": ["Block Number", "string"],
                    "hash": ["Hash", "string"],
                    "timestamp": ["Timestamp", "string"],
                    "transactionCount": ["Txs", "string"],
                    "miner": ["Miner", "string"]
                }
            }, cls=JSONEncoder),
            data_source=datasource
        )

        db.session.add(query)
        db.session.commit()


@manager.command()
def ensure_txs_query():
    """Create the transactions query."""
    from redash.models import db, Query, Visualization, DataSource

    _wait_for_db_connection(db)

    query_name = "Ledger Transactions"
    datasource = DataSource.query.filter(DataSource.name == ds_ledger)
    # Check for query
    query = Query.query.filter(Query.name == query_name)
    # Add query if it does not exist
    if query is None:
        query = Query.query.filter(
            name=query_name,
            description="",
            query_text=json.dumps({
                "path": "/api/v1/ledger/{{consortia_id}}/{{environment_id}}/transactions",
                "headers": {
                    "Authorization": "Bearer {request.cookies.jwt}"
                },
                "query": {
                    "hash": ["Hash", "string"],
                    "status": ["Hash", "string"],
                    "from": ["Hash", "string"],
                    "to": ["Hash", "string"],
                    "timestamp": ["Timestamp", "string"],
                    "blockNumber": ["Txs", "string"],
                    "blockHash": ["Hash", "string"]
                }
            }, cls=JSONEncoder),
            data_source=datasource
        )

        db.session.add(query)
        db.session.commit()


@manager.command()
def ensure_ops_dashboard():
    """Create the ops dashboard"""
    from redash.models import db, Dashboard, Widget

    _wait_for_db_connection(db)

    # Check for dashboard
    dashboard = Dashboard.query.filter(name="Ops")
    require_commit = False
    # Add dasboard if it does not exist
    if dashboard is None:
        dashboard = Dashboard(name="Ops", is_draft=False)

        db.session.add(dashboard)
        db.session.commit()
