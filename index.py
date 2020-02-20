from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
import traceback
from urllib.parse import parse_qs, urlparse

import pytz

from workflowy import WorkFlowy
from utils import DEFAULT_TIMEZONE


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        location = urlparse(self.path)
        path = location.path[1:]
        query = parse_qs(location.query, keep_blank_values=True)

        # only valid route is /overdue?session_id=foo
        # optional summary, index and timezone GET parameters
        if path != 'overdue':
            self.send_response(400)
            self.end_headers()
            return

        try:
            # initialize API client with populated data
            session_id = query['session_id'][-1]
            timezone = pytz.timezone(query.get('timezone', [DEFAULT_TIMEZONE])[-1])
            api = WorkFlowy(session_id, timezone)

            # get all tasks until midnight
            next_midnight = datetime.now(timezone).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)
            overdue = api.filter(until=next_midnight, completed=False)

            # forward to API actions
            if query.get('summary'):
                response = api.summarize(overdue)
            elif query.get('index'):
                response = api.detail(overdue, int(query['index'][-1]))
            else:
                response = api.list(overdue)

        # catches missing or invalid session_id, invalid timezone and downstream API errors
        except Exception:
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()

        else:
            self.send_response(200)
            self.send_header('content-type', 'application/rss+xml')
            self.end_headers()
            self.wfile.write(bytes(response))
