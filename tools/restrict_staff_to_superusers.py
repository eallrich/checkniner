import json

with open('user.json', 'rb') as f:
    users = json.load(f)
    print "'user.json' contains %d records" % len(users)

for u in users:
    is_superuser = u['fields']['is_superuser']
    if not is_superuser:
        u['fields']['is_staff'] = False

with open('restricted_user.json', 'wb') as f:
    print "Writing users to 'restricted_user.json'...",
    json.dump(users, f, indent=4, separators=(',',': '), sort_keys=True)
    print "done"

