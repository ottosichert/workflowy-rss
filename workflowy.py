import re

from datetime import datetime
import requests

from utils import XML


class WorkFlowy:
    CLIENT_VERSION = 21
    INITIALIZATION_URL = f'https://workflowy.com/get_initialization_data?client_version={CLIENT_VERSION}'
    ID_KEY = 'id'
    CHILDREN_KEY = 'ch'
    TITLE_KEY = 'nm'
    COMPLETION_KEY = 'cp'
    TIME_PATTERN = r'<time startYear="(?P<year>\d+)".*startMonth="(?P<month>\d+)".*startDay="(?P<day>\d+)"[^>]*>([^<]*)</time>'  # noqa: E501

    def __init__(self, session_id, timezone):
        self.session_id = session_id
        self.timezone = timezone

        # bounded methods for use in filter method
        self.FILTER_MAP = {
            'until': self.filter_until,
            'completed': self.filter_completed,
        }

        self.initialize_data()

    def initialize_data(self):
        """Load all nodes and user settings"""

        response = requests.get(self.INITIALIZATION_URL, cookies={'sessionid': self.session_id})
        response.raise_for_status()
        self.data = response.json()

    def filter(self, *path, **kwargs):
        # create root node as top level is a list of children only
        if not path:
            path += ({
                self.TITLE_KEY: 'Home',
                self.CHILDREN_KEY: self.data['projectTreeData']['mainProjectTreeInfo']['rootProjectChildren'],
            },)

        result = []
        node = path[-1]

        # add current node if all conditions apply
        if all(self.FILTER_MAP[key](node, value) for key, value in kwargs.items()):
            result.append(path)

        # recursively add nodes down the tree
        children = node.get(self.CHILDREN_KEY, [])
        for child in children:
            result.extend(self.filter(*path, child, **kwargs))

        return result

    def filter_until(self, node, until):
        """Only allow nodes with a WorkFlowy date time element before a given date time"""

        title = node.get(self.TITLE_KEY, '')
        match = re.search(self.TIME_PATTERN, title)

        if not match:
            return False

        start = datetime.now(self.timezone).replace(
            **{segment: int(value) for segment, value in match.groupdict().items()},
            hour=0, minute=0, second=0, microsecond=0,
        )
        return start < until

    def filter_completed(self, node, completed):
        completion_time = node.get(self.COMPLETION_KEY, 0)
        return completed == (completion_time > 0)

    def wrap(self, *content):
        return (  # noqa: E128
            XML('rss',
                XML('channel',
                    XML('title', 'WorkFlowy summary'),
                    XML('link', 'https://workflowy.com'),
                    XML('atom:link', 'https://workflowy-rss.now.sh'),
                    *content
                ),
                version='2.0',
                **{'xmlns:atom': 'http://www.w3.org/2005/Atom'},
            )
        )

    def summarize(self, paths):
        return self.wrap(  # noqa: E128
            XML('item',
                XML('title', f'{len(paths)} tasks today'),
                XML('link', 'https://workflowy.com/#?q=today%20-is%3Acomplete'),
                XML('guid', 'summary'),
            )
        )

    def empty(self):
        return self.wrap(XML('item', XML('title', '-')))

    def node(self, path):
        """Format RSS item with WorkFlowy date time element"""

        *parents, node = path
        return XML('item',  # noqa: E128
            XML('title', re.sub(self.TIME_PATTERN, '', node.get(self.TITLE_KEY, '')).strip() or '-'),
            XML('author', re.search(self.TIME_PATTERN, node.get(self.TITLE_KEY, '')).group(4)),
            XML('description', ' / '.join(parent.get(self.TITLE_KEY, '') for parent in parents)),
            XML('link', f'https://workflowy.com/#/{node[self.ID_KEY].split("-")[-1]}'),
            XML('guid', node[self.ID_KEY]),
        )

    def detail(self, paths, index):
        # index is user provided but allow negative indexing
        try:
            return self.wrap(self.node(paths[index]))
        except IndexError:
            return self.empty()

    def list(self, paths):
        return self.wrap(*map(self.node, paths))
