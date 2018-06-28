from flask_restful import Api
from werkzeug.wrappers import Response
from flask import make_response

from redash import settings
from redash.utils import json_dumps
from redash.handlers.base import org_scoped_rule
from redash.handlers.permissions import ObjectPermissionsListResource, CheckPermissionResource
from redash.handlers.alerts import AlertResource, AlertListResource, AlertSubscriptionListResource, AlertSubscriptionResource
from redash.handlers.dashboards import DashboardListResource, RecentDashboardsResource, DashboardResource, DashboardShareResource, PublicDashboardResource
from redash.handlers.data_sources import DataSourceTypeListResource, DataSourceListResource, DataSourceSchemaResource, DataSourceResource, DataSourcePauseResource, DataSourceTestResource
from redash.handlers.events import EventsResource
from redash.handlers.queries import QueryForkResource, QueryRefreshResource, QueryListResource, QueryRecentResource, QuerySearchResource, QueryResource, MyQueriesResource
from redash.handlers.query_results import QueryResultListResource, QueryResultResource, JobResource
from redash.handlers.users import UserResource, UserListResource, UserInviteResource, UserResetPasswordResource, UserDisableResource
from redash.handlers.visualizations import VisualizationListResource
from redash.handlers.visualizations import VisualizationResource
from redash.handlers.widgets import WidgetResource, WidgetListResource
from redash.handlers.groups import GroupListResource, GroupResource, GroupMemberListResource, GroupMemberResource, \
    GroupDataSourceListResource, GroupDataSourceResource
from redash.handlers.destinations import DestinationTypeListResource, DestinationResource, DestinationListResource
from redash.handlers.query_snippets import QuerySnippetListResource, QuerySnippetResource
from redash.handlers.settings import OrganizationSettings


class ApiExt(Api):
    def add_org_resource(self, resource, *urls, **kwargs):
        urls = [org_scoped_rule(url) for url in urls]
        return self.add_resource(resource, *urls, **kwargs)

api = ApiExt(prefix=settings.ROOT_API_URL)

@api.representation('application/json')
def json_representation(data, code, headers=None):
    # Flask-Restful checks only for flask.Response but flask-login uses werkzeug.wrappers.Response
    if isinstance(data, Response):
        return data
    resp = make_response(json_dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


api.add_org_resource(AlertResource, '/alerts/<alert_id>', endpoint='alert')
api.add_org_resource(AlertSubscriptionListResource, '/alerts/<alert_id>/subscriptions', endpoint='alert_subscriptions')
api.add_org_resource(AlertSubscriptionResource, '/alerts/<alert_id>/subscriptions/<subscriber_id>', endpoint='alert_subscription')
api.add_org_resource(AlertListResource, '/alerts', endpoint='alerts')

api.add_org_resource(DashboardListResource, '/dashboards', endpoint='dashboards')
api.add_org_resource(RecentDashboardsResource, '/dashboards/recent', endpoint='recent_dashboards')
api.add_org_resource(DashboardResource, '/dashboards/<dashboard_slug>', endpoint='dashboard')
api.add_org_resource(PublicDashboardResource, '/dashboards/public/<token>', endpoint='public_dashboard')
api.add_org_resource(DashboardShareResource, '/dashboards/<dashboard_id>/share', endpoint='dashboard_share')

api.add_org_resource(DataSourceTypeListResource, '/data_sources/types', endpoint='data_source_types')
api.add_org_resource(DataSourceListResource, '/data_sources', endpoint='data_sources')
api.add_org_resource(DataSourceSchemaResource, '/data_sources/<data_source_id>/schema')
api.add_org_resource(DataSourcePauseResource, '/data_sources/<data_source_id>/pause')
api.add_org_resource(DataSourceTestResource, '/data_sources/<data_source_id>/test')
api.add_org_resource(DataSourceResource, '/data_sources/<data_source_id>', endpoint='data_source')

api.add_org_resource(GroupListResource, '/groups', endpoint='groups')
api.add_org_resource(GroupResource, '/groups/<group_id>', endpoint='group')
api.add_org_resource(GroupMemberListResource, '/groups/<group_id>/members', endpoint='group_members')
api.add_org_resource(GroupMemberResource, '/groups/<group_id>/members/<user_id>', endpoint='group_member')
api.add_org_resource(GroupDataSourceListResource, '/groups/<group_id>/data_sources', endpoint='group_data_sources')
api.add_org_resource(GroupDataSourceResource, '/groups/<group_id>/data_sources/<data_source_id>', endpoint='group_data_source')

api.add_org_resource(EventsResource, '/events', endpoint='events')

api.add_org_resource(QuerySearchResource, '/queries/search', endpoint='queries_search')
api.add_org_resource(QueryRecentResource, '/queries/recent', endpoint='recent_queries')
api.add_org_resource(QueryListResource, '/queries', endpoint='queries')
api.add_org_resource(MyQueriesResource, '/queries/my', endpoint='my_queries')
api.add_org_resource(QueryRefreshResource, '/queries/<query_id>/refresh', endpoint='query_refresh')
api.add_org_resource(QueryResource, '/queries/<query_id>', endpoint='query')
api.add_org_resource(QueryForkResource, '/queries/<query_id>/fork', endpoint='query_fork')

api.add_org_resource(ObjectPermissionsListResource, '/<object_type>/<object_id>/acl', endpoint='object_permissions')
api.add_org_resource(CheckPermissionResource, '/<object_type>/<object_id>/acl/<access_type>', endpoint='check_permissions')

api.add_org_resource(QueryResultListResource, '/query_results', endpoint='query_results')
api.add_org_resource(QueryResultResource,
                     '/query_results/<query_result_id>.<filetype>',
                     '/query_results/<query_result_id>',
                     '/queries/<query_id>/results.<filetype>',
                     '/queries/<query_id>/results/<query_result_id>.<filetype>',
                     endpoint='query_result')
api.add_org_resource(JobResource, '/jobs/<job_id>', endpoint='job')

api.add_org_resource(UserListResource, '/users', endpoint='users')
api.add_org_resource(UserResource, '/users/<user_id>', endpoint='user')
api.add_org_resource(UserInviteResource, '/users/<user_id>/invite', endpoint='user_invite')
api.add_org_resource(UserResetPasswordResource, '/users/<user_id>/reset_password', endpoint='user_reset_password')
api.add_org_resource(UserDisableResource, '/users/<user_id>/disable', endpoint='user_disable')

api.add_org_resource(VisualizationListResource, '/visualizations', endpoint='visualizations')
api.add_org_resource(VisualizationResource, '/visualizations/<visualization_id>', endpoint='visualization')

api.add_org_resource(WidgetListResource, '/widgets', endpoint='widgets')
api.add_org_resource(WidgetResource, '/widgets/<int:widget_id>', endpoint='widget')

api.add_org_resource(DestinationTypeListResource, '/destinations/types', endpoint='destination_types')
api.add_org_resource(DestinationResource, '/destinations/<destination_id>', endpoint='destination')
api.add_org_resource(DestinationListResource, '/destinations', endpoint='destinations')

api.add_org_resource(QuerySnippetResource, '/query_snippets/<snippet_id>', endpoint='query_snippet')
api.add_org_resource(QuerySnippetListResource, '/query_snippets', endpoint='query_snippets')

api.add_org_resource(OrganizationSettings, '/settings/organization', endpoint='organization_settings')
