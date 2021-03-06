from flask_restplus import Namespace, Resource, fields, abort
from apis.data import state_services
from apis.data import city_services

data_endpoints = Namespace('cases', description='Cases related operations')

headers = data_endpoints.parser()
headers.add_argument(
    'Authorization',
    location='headers',
    required=True,
    help="Access token. E.g.: Bearer [JWT]"
)

pagination = data_endpoints.model('Pagination Info', {
    'total_pages': fields.Integer(
        required=False, description='Total Pages'),
    'has_next': fields.Boolean(
        required=False, description='Has next page?'),
    'has_previous': fields.Boolean(
        required=False, description='Has previous page?'),
    'next_page': fields.Integer(
        required=False, description='Next page'),
    'current_page': fields.Integer(
        required=False, description='Current page')

})

city_cases = data_endpoints.model('City Cases', {
    'id': fields.Integer(required=True, description='Id'),
    'city': fields.String(required=True, description='City'),
    'ibge_id': fields.String(required=True, description='IBGE Id'),
    'country': fields.String(required=True, description='Country'),
    'state_id': fields.Integer(required=True, description='State Id'),
    'totalcases': fields.Integer(required=True, description='Total cases'),
    'deaths': fields.Integer(required=True, description='Deaths')

})

city_cases_response_list = data_endpoints.model('City Cases Response List', {
    'cases': fields.Nested(
        city_cases, required=True, as_list=True, description='Cases')
})

city_cases_response_paginated_list = data_endpoints.inherit(
    'City Cases Response List Paginated', city_cases_response_list, {
        'pagination': fields.Nested(
            pagination, required=False, description='Pagination info')
    }
)

city_cases_response_report = data_endpoints.model(
    'City Cases Response Report', {
        'totalCases': fields.Integer(
            required=True, description='Total cases'),
        'deaths': fields.Integer(
            required=True, description='Deaths')
    }
)


city_cases_filtered_response_report = data_endpoints.model(
    'City Cases Filtered Response Report', {
        'city': fields.String(
            required=True, description='City'),
        'state': fields.String(
            required=True, description='State'),
        'cases': fields.Nested(
            city_cases_response_report, required=False,
            description='Cases info')
    }
)

city_cases_response_list_report = data_endpoints.model(
    'City Cases Response List Report', {
        'totalCases': fields.Integer(
            required=True, description='Total cases')
    }
)


cases_detail_response = data_endpoints.model(
    'State Cases Detail Response',
    {
        'totalCases': fields.Integer(required=True,
                                     description='Total active cases'),
        'deaths': fields.Integer(required=True,
                                 description='Total deaths')
    }
)

state_cases_list_response = data_endpoints.model('State Cases Response', {
    'stateCode': fields.String(required=True, description='State code'),
    'stateName': fields.String(required=True, description='State name'),
    'lat': fields.String(required=True, description='State Latitude'),
    'lng': fields.String(required=True, description='State Longitude'),
    'cases': fields.Nested(cases_detail_response,
                           required=True, description='Case details'),
}, as_list=True)


daily_state_case_detail_response = data_endpoints.model(
    'Daily State Case Detail Response',
    {
        'totalCases': fields.Integer(required=True,
                                     description='Total active cases'),
        'newCases': fields.Integer(required=True,
                                   description='Total new cases')
    }
)

daily_state_case_response = data_endpoints.model('Daily State Case Response', {
    'stateCode': fields.String(required=False, description='State code'),
    'stateName': fields.String(required=False, description='State name'),
    'lat': fields.String(required=False, description='State Latitude'),
    'lng': fields.String(required=False, description='State Longitude'),
    'country': fields.String(required=True, description='Country'),
    'date': fields.String(required=True, description='Date'),
    'case_detail': fields.Nested(
        daily_state_case_detail_response,
        required=True, description='Case details'),
})

daily_state_cases_response = data_endpoints.model(
    'Daily State Cases Response Paginated', {
        'cases': fields.Nested(
            daily_state_case_response, required=False, as_list=True,
            description='Cases list'),
        'pagination': fields.Nested(
            pagination, required=False, description='Pagination info')
    }
)

state_cases_report_response = data_endpoints.model(
    'State Cases Report Response', {
        'totalCases': fields.String(required=True, description='Total cases'),
        'totalCasesMS': fields.String(
            required=True, description='Total cases confirmed by MS'),
        'deaths': fields.String(required=True, description='Deaths'),
    }
)


@data_endpoints.route('/state')
class ListStateCases(Resource):
    @data_endpoints.doc('state_cases')
    @data_endpoints.marshal_with(state_cases_list_response)
    def get(self):
        """List cases per state"""
        response = state_services.get_state_cases()
        if not response:
            abort(404, "No cases found for states")
        return response


@data_endpoints.route('/state/report')
class GetStateCasesTotals(Resource):
    @data_endpoints.doc('state_report_cases')
    @data_endpoints.marshal_with(state_cases_report_response)
    def get(self):
        """Cases per state report"""
        response = state_services.get_sum_state_cases()
        if not all(report for report in response.values()):
            abort(404, "No report found for states")
        return response


@data_endpoints.route('/state/daily/<int:page>')
class ListStateCasesDaily(Resource):
    @data_endpoints.doc('state_cases_per_day')
    @data_endpoints.marshal_with(daily_state_cases_response)
    def get(self, page):
        """List cases per state daily"""
        response = state_services.get_daily_state_cases(page)
        if not response:
            abort(404, "No cases found for states")
        return response


@data_endpoints.route('/city')
class CityCasesList(Resource):
    @data_endpoints.doc('city_cases_list')
    @data_endpoints.marshal_with(city_cases_response_list)
    def get(self):
        """Cases per city list"""
        response = city_services.get_city_cases(None)
        if not response.get('cases'):
            abort(404, "No cases found")
        return response


@data_endpoints.route('/city/<int:page>')
class CityCasesPaginatedList(Resource):
    @data_endpoints.doc('city_cases_paginated_list')
    @data_endpoints.marshal_with(city_cases_response_paginated_list)
    def get(self, page):
        """Cases per city list paginated"""
        response = city_services.get_city_cases(page)

        if not response.get('cases'):
            abort(404, "No cases found for this page")

        return response


@data_endpoints.route('/city/report')
class CityCasesReport(Resource):
    @data_endpoints.doc('city_cases_report')
    @data_endpoints.marshal_with(city_cases_response_report)
    def get(self):
        """Cases per city report"""
        response = city_services.get_totals_cases_per_city()
        if response.get('totalCases') == 0:
            abort(404, "No cases found")

        return response


@data_endpoints.route('/city/<string:term>/report')
class GetCityCasesTotalsFiltered(Resource):
    @data_endpoints.doc('city_cases_filtered_report')
    @data_endpoints.marshal_with(city_cases_filtered_response_report)
    def get(self, term):
        """Cases per city report, filtered by city term"""
        response = city_services.search_on_location_by_term(term)
        if not response:
            abort(404, f"No cases found for city {term}")
        return response


def bind(api):
    api.add_namespace(data_endpoints)
