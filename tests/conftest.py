import base64
import betamax
import os
import pytest


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'

    record_mode = 'all'

    config.default_cassette_options['record_mode'] = record_mode


@pytest.fixture
def betamax_simple_body(request):
    """Return configuration to match cassette on uri, method and body."""
    request.cls.betamax_simple_body = {
        'match_requests_on': ['uri', 'method', 'body']
    }


class IfNoneMatchMatcher(betamax.BaseMatcher):

    name = 'if-none-match'

    def match(self, request, recorded_request):
        request_header  = request.headers.get('If-None-Match')
        recorded_header = recorded_request['headers'].get('If-None-Match')
        matches = True if request_header == recorded_header else False
        return matches


betamax.Betamax.register_request_matcher(IfNoneMatchMatcher)