import json
import pprint

with open('checkout.json','rb') as f:
    checkouts = json.load(f)
    print "'checkout.json' contains %d records" % len(checkouts)

uniques = []
counts = {}
for c in checkouts:
    pilot = c['fields']['pilot']
    airstrip = c['fields']['airstrip']
    aircraft = c['fields']['aircraft_type']
    key = "%d|%d|%d" % (pilot, airstrip, aircraft)
    if key not in counts:
	counts[key] = 1
	uniques.append(c)
    else:
	counts[key] += 1

print "Found %d unique records..." % len(uniques),
duplicates = []
for key,count in counts.items():
    if count > 1:
	duplicates.append((key, count))
print "and %d duplicate keys" % len(duplicates)
#pprint.pprint(duplicates)

for i,c in enumerate(uniques):
    c['pk'] = i+1 # Correcting the order of primary keys

with open('unique_checkout.json','wb') as f:
    print "Writing uniques to 'unique_checkout.json'...",
    json.dump(uniques, f, indent=4, separators=(',',': '), sort_keys=True)
    print "done"
