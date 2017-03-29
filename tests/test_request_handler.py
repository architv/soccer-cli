import os
import sys
sys.path.append('soccer')
import json
import requests
import unittest
import leagueids
import mock
import click
from main import load_json
from mock_response import MockResponse
from soccer.exceptions import APIErrorException
from request_handler import RequestHandler
from soccer.writers import get_writer
from soccer.writers import Stdout


def mocked_requests_get(*args, **kwargs):
    return MockResponse(args[0], int(args[1]))


def get_team_data():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "../soccer/teams.json")) as jfile:
        data = json.load(jfile)
    return data


class TestRequestHandler(unittest.TestCase):

    def setUp(self):
        dummy_key = 12345678901234567890123456789012
        headers = {'X-Auth-Token': dummy_key}
        TEAM_DATA = get_team_data()["teams"]
        TEAM_NAMES = {team["code"]: team["id"] for team in TEAM_DATA}
        LEAGUE_IDS = leagueids.LEAGUE_IDS
        self.dummy_url = "http://some_url"
        writer = get_writer()
        self.rq = RequestHandler(headers, LEAGUE_IDS, TEAM_NAMES, writer)

    def tearDown(self):
        pass

    @mock.patch('requests.get')
    def test_ok_code(self, mock_call):
        mock_call.return_value = mock.MagicMock(
                status_code=requests.codes.ok,
                response=json.dumps({'key': 'value'}))
        raised = False
        try:
            self.rq._get(self.dummy_url)
        except APIErrorException:
            raised = True
        self.assertFalse(raised is True)

    @mock.patch('requests.get')
    def test_bad_code(self, mock_call):
        mock_call.return_value = mock.MagicMock(
                status_code=requests.codes.bad,
                response=json.dumps({'key': 'value'}))
        raised = False
        try:
            self.rq._get(self.dummy_url)
        except APIErrorException:
            raised = True
        self.assertTrue(raised is True)

    @mock.patch('requests.get')
    def test_forbidden_code(self, mock_call):
        mock_call.return_value = mock.MagicMock(
                status_code=requests.codes.forbidden,
                response=json.dumps({'key': 'value'}))
        raised = False
        try:
            self.rq._get(self.dummy_url)
        except APIErrorException:
            raised = True
        self.assertTrue(raised is True)

    @mock.patch('requests.get')
    def test_not_found_code(self, mock_call):
        mock_call.return_value = mock.MagicMock(
                status_code=requests.codes.not_found,
                response=json.dumps({'key': 'value'}))
        raised = False
        try:
            self.rq._get(self.dummy_url)
        except APIErrorException:
            raised = True
        self.assertTrue(raised is True)

    @mock.patch('requests.get')
    def test_too_many_requests_code(self, mock_call):
        mock_call.return_value = mock.MagicMock(
                status_code=requests.codes.too_many_requests,
                response=json.dumps({'key': 'value'}))
        raised = False
        try:
            self.rq._get(self.dummy_url)
        except APIErrorException:
            raised = True
        self.assertTrue(raised is True)

    @mock.patch('test_request_handler.Stdout.live_scores')
    @mock.patch('requests.get')
    def test_get_live_scores_ok(self, mock_request_call, mock_writer):
        mock_request_call.side_effect = [mocked_requests_get({'games': [1, 2]}, 200)]
        mock_writer.return_value = mock.Mock()
        self.rq.get_live_scores(True)
        mock_writer.assert_called_once()

    @mock.patch('test_request_handler.click.secho')
    @mock.patch('test_request_handler.Stdout.live_scores')
    @mock.patch('requests.get')
    def test_get_live_scores_0_games(self,
                                     mock_request_call, mock_writer,
                                     mock_click):
        mock_request_call.side_effect = [mocked_requests_get({'games': []}, 200)]
        mock_writer.return_value = mock.Mock()
        self.rq.get_live_scores(True)
        mock_click.assert_called_with("No live action currently", fg="red", bold=True)

    @mock.patch('test_request_handler.click.secho')
    @mock.patch('test_request_handler.Stdout.live_scores')
    @mock.patch('requests.get')
    def test_get_live_scores_error(self,
                                   mock_request_call, mock_writer,
                                   mock_click):
        mock_request_call.side_effect = [mocked_requests_get({'games': [1, 2]}, 400)]
        mock_writer.return_value = mock.Mock()
        self.rq.get_live_scores(True)
        mock_click.assert_called_with("There was problem getting live scores", fg="red", bold=True)

    @mock.patch('test_request_handler.Stdout.team_scores')
    @mock.patch('requests.get')
    def test_get_team_scores_ok(self,
                                mock_request_call, mock_writer):
        mock_request_call.side_effect = [mocked_requests_get({'fixtures': [1, 2]}, 200)]
        mock_writer.return_value = mock.Mock()
        self.rq.get_team_scores("AFC", 6, True, True)
        mock_writer.assert_called_once()

    @mock.patch('test_request_handler.click.secho')
    @mock.patch('test_request_handler.Stdout.team_scores')
    @mock.patch('requests.get')
    def test_get_team_scores_0_fixtures(self,
                                        mock_request_call,
                                        mock_writer, mock_click):
        mock_request_call.side_effect = [mocked_requests_get({'fixtures': []}, 200)]
        mock_writer.return_value = mock.Mock()
        self.rq.get_team_scores("AFC", 6, True, True)
        mock_click.assert_called_with("No action during past week. Change the time "
         "parameter to get more fixtures.", fg="red", bold=True)

    @mock.patch('test_request_handler.click.secho')
    @mock.patch('test_request_handler.Stdout.team_scores')
    @mock.patch('requests.get')
    def test_get_team_scores_bad_id(self,
                                    mock_request_call,
                                    mock_writer, mock_click):
        mock_request_call.side_effect = [mocked_requests_get({'fixtures': [1, 2]}, 200)]
        mock_writer.return_value = mock.Mock()
        self.rq.get_team_scores("AdkljdfkljkdlFC", 6, True, True)
        mock_click.assert_called_with("Team code is not correct.", fg="red", bold=True)


if __name__ == '__main__':
    unittest.main()
