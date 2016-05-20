import base64
import betamax
import os
import pytest
from betamax_serializers import pretty_json

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    record_mode = 'once'

    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['record_mode'] = record_mode
    #config.default_cassette_options['serialize_with'] = 'prettyjson'


@pytest.fixture
def betamax_simple_body(request):
    """Return configuration to match cassette on uri, method and body."""
    request.cls.betamax_simple_body = {
        'match_requests_on': ['uri', 'method', 'body']
    }

