from datetime import datetime

import requests

from brook import plugin, config


date_format = '%Y-%m-%dT%H:%M:%SZ'


class GitHub(plugin.Plugin):

    def main(self):
        url = 'https://api.github.com/users/{0}/events'
        r = requests.get(url.format(config.GITHUB_USER))

        if 'message' in r.json:
            print 'GitHub: ' + r.json['message']
            return

        for event in r.json:
            # Execute function of the same name as the Event Type
            # Hacky way of doing it, would like to find a nicer way
            if event['type'] in globals():
                # Each event should return a dict with every value
                # it needs to build the HTML templates

                event_info = globals()[event['type']](event)

                s = self.insert_data(*event_info)
                if not s['success']:
                    # We're only going to find events
                    # we've already got in the DB
                    return


def event_handler(func):
    """
    This decorator takes the event_id and event_time
    from the json so events only need to return `info`

    """

    def wrapper(event):
        info = func(event)
        if 'type' not in info:
            info.update({'type': event['type']})

        event_id = event['id']
        event_time = datetime.strptime(event['created_at'], date_format)
        return (event_id, event_time, info)

    return wrapper


@event_handler
def PushEvent(event):
    info = {
        'repo': event['repo']['name'],
        'branch': event['payload']['ref'].rsplit('/', 1)[1],
        'amount': event['payload']['size'],
        'commits': event['payload']['commits']
    }

    return info


@event_handler
def WatchEvent(event):
    info = {
        'repo': event['repo']['name'],
        'action': event['payload']['action']
    }

    return info


@event_handler
def FollowEvent(event):
    info = {
        'user': event['payload']['target']['login']
    }

    return info


@event_handler
def IssuesEvent(event):
    info = {
        'action': event['payload']['action'],
        'repo': event['repo']['name'],
        'number': event['payload']['issue']['number'],
        'title': event['payload']['issue']['title']

    }

    return info


@event_handler
def CreateEvent(event):
    info = {
        'ref_type': event['payload']['ref_type'],
        'ref': event['payload']['ref'],
        'repo': event['repo']['name']
    }

    return info


@event_handler
def DeleteEvent(event):
    info = {
        'ref_type': event['payload']['ref_type'],
        'ref': event['payload']['ref'],
        'repo': event['repo']['name']
    }

    return info


@event_handler
def ForkEvent(event):
    info = {
        'forked_from': event['repo']['name']
    }

    try:
        d = {'fork': event['payload']['forkee']['full_name']}
    except KeyError:
        # fullname is not always in json
        actor = event['actor']['login']
        repo = event['payload']['forkee']['name']
        d = {'fork': '{0}/{1}'.format(actor, repo)}

    info.update(d)

    return info


@event_handler
def PullRequestEvent(event):
    info = {
        'action': event['payload']['action'],
        'number': event['payload']['number'],
        'repo': event['repo']['name']
    }

    return info


@event_handler
def IssueCommentEvent(event):
    info = {
        'action': event['payload']['action'],
        'repo': event['repo']['name'],
        'number': event['payload']['issue']['number'],
        'comment_id': event['payload']['comment']['id'],
        'comment': event['payload']['comment']['body']
    }

    return info


@event_handler
def GistEvent(event):
    info = {
        'action': event['payload']['action'],
        'gist_url': event['payload']['gist']['html_url'],
        'gist_id': event['payload']['gist']['id']
    }

    return info


@event_handler
def PullRequestReviewCommentEvent(event):
    info = {
        'repo': event['repo']['name'],
        'comment': event['payload']['comment']['body'],
        'url': event['payload']['comment']['_links']['html']['href'],
    }

    info['number'] = info['url'].rsplit('/', 1)[1].split('#')[0]

    return info


@event_handler
def GollumEvent(event):
    info = {
        'repo': event['repo']['name'],
        'amount': len(event['payload']['pages']) - 1,
        'action': event['payload']['pages'][0]['action'],
        'name': event['payload']['pages'][0]['title'],
        'url': event['payload']['pages'][0]['html_url'],
    }

    return info


@event_handler
def CommitCommentEvent(event):
    info = {
        'repo': event['repo']['name'],
        'url': event['payload']['comment']['html_url'],
        'comment': event['payload']['comment']['body'],
        'commit_id': event['payload']['comment']['commit_id']
    }

    return info

# Register our plugin
GitHub('GitHub')
