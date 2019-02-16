import csv
import datetime
import sys

def parse(line):
    meta, rest = line.strip().split(']: ')
    ts, pid = meta.split(' [')
    dt = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S+0000')
    #print('date = %r' % dt)
    #print('pid = %r' % pid)
    pieces = rest.split(' ')
    segments = [['date', dt.date().strftime('%Y-%m-%d')], ['time', dt.time().strftime('%H:%M:%S')], ['pid', pid]]
    for piece in pieces:
        if '=' in piece:
            name, value = piece.split('=')
            if name == 'at':
                segments.append(['level', value])
            elif name == 'client':
                username, ip = value.split('@')
                segments.append(['username', username])
                segments.append(['ip', ip])
            elif name in ['queue', 'real']:
                segments.append([name, int(value.strip('ms'))])
            elif name == 'bytes':
                segments.append([name, int(value)])
            elif name == 'useragent':
                segments.append([name, value.strip('"').strip(',')])
            else:
                segments.append([name, value])
        else:
            segments[-1][1] += ' ' + piece.strip('"').strip(',')
    #print('segments = %r' % segments)
    return {k:v for k,v in segments}

if len(sys.argv) == 1:
    print("Usage: python %s FILE1 [FILE2 [...]]" % sys.argv[0])
    sys.exit(1)

files = sys.argv[1:]
records = []

for name in files:
    with open(name, 'r') as f:
        for line in f:
            records.append(parse(line))

headers = ['date', 'time', 'pid', 'level', 'username', 'ip', 'method', 'path', 'queue', 'real', 'status', 'bytes', 'useragent']
with open('cleaned.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for row in records:
        writer.writerow(row)

print('Done. Wrote %d records' % len(records))
