import datetime
import pprint

def escape_quoted_spaces(line):
    in_quote = False
    replacement = '!@#'
    new_line = ""
    for c in line:
        new_c = c
        if c == '"':
            in_quote = not in_quote
            new_c = ''
        elif c == ' ' and in_quote:
            new_c = replacement
        new_line += new_c
    return new_line


def unescape_quoted_spaces(line):
    replacement = '!@#'
    return line.replace(replacement, ' ')


def users(parsed):
    usernames = []
    for d in parsed:
        user, ip = d['client'].split('@')
        if user not in usernames:
            usernames.append(user)
    usernames.sort()
    print("%d usernames identified" % len(usernames))
    pprint.pprint(usernames)


def clients(parsed):
    clients = {}
    for d in parsed:
        count = clients.get(d['client'], 0)
        clients[d['client']] = count + 1
    print("%d clients identified" % len(clients))
    pprint.pprint(clients)


def last(parsed):
    most_recent = {}
    now = datetime.datetime.now()
    for d in parsed:
        user, ip = d['client'].split('@')
        then = datetime.datetime.strptime(d['timestamp'], '%Y-%m-%dT%H:%M:%S+0000')
        difference = now - then
        days_ago = difference.days
        most_recent[user] = [days_ago, ip]
    activity = ["%-12s| %3d days ago via %s" % (user, details[0], details[1]) for user, details in most_recent.items()]
    activity.sort()
    print("Most recent activity by username:")
    pprint.pprint(activity)


def per_day(parsed):
    max_days = 30
    now = datetime.datetime.now()
    by_day = {}
    for d in parsed:
        user, ip = d['client'].split('@')
        then = datetime.datetime.strptime(d['timestamp'], '%Y-%m-%dT%H:%M:%S+0000')
        difference = now - then
        if difference.days <= max_days:
            day = then.date()
            current = by_day.get(day, {'users': [], 'ips': []})
            if user not in current['users']:
                current['users'].append(user)
            if ip not in current['ips']:
                current['ips'].append(ip)
            by_day[day] = current
    print("Hits in the past %d days:" % max_days)
    data = ["%s | %2d users from %2d IPs" % (day.isoformat(), len(stats['users']), len(stats['ips'])) for day, stats in by_day.items()]
    data.sort()
    pprint.pprint(data)


def useragents(parsed):
    uas = {}
    for d in parsed:
        ua = d['useragent']
        count = uas.get(ua, 0)
        uas[ua] = count + 1
    print("%d useragents identified" % len(uas))
    pprint.pprint(uas)


def statuscodes(parsed):
    statuses = {}
    for d in parsed:
        status = d['status']
        statuses[status] = statuses.get(status, 0) + 1
    print("%d status codes identified" % len(statuses))
    pprint.pprint(statuses)


def not_founds(parsed):
    paths = {}
    for d in parsed:
        if d['status'] == '404':
            path = d['path']
            paths[path] = paths.get(path, 0) + 1
    print("Paths with 404 status codes:")
    pprint.pprint(paths)


f = open('analytics.log', 'rb')

lines = f.readlines()

parsed = []
for line in lines:
    prefix, keyvalues = line.split(': ')
    timestamp, _ = prefix.split()
    keyvalues = escape_quoted_spaces(keyvalues)
    kvpairs = []
    for kv in keyvalues.split():
        kvpairs.append(unescape_quoted_spaces(kv))
    try:
        d = dict([s.split('=') for s in kvpairs])
    except:
        print("Failed on '%s'" % line)
        continue
    d['timestamp'] = timestamp
    parsed.append(d)

#users(parsed)
#clients(parsed)
#useragents(parsed)
#statuscodes(parsed)
not_founds(parsed)
last(parsed)
per_day(parsed)
