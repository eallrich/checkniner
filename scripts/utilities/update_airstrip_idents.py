import csv

from checkouts.models import Airstrip

with open('airstrip_change_list.csv', 'rb') as f:
    reader = csv.DictReader(f)
    updates = [x for x in reader]

for change in updates:
    old_ident = change['Old Ident']
    new_ident = change['New Ident']
    try:
        airstrip = Airstrip.objects.get(ident=old_ident)
    except Airstrip.DoesNotExist:
        try:
            Airstrip.objects.get(ident=new_ident)
            print("No need to change %s to %s, already switched" % (old_ident, new_ident))
        except Airstrip.DoesNotExist:
            print("Could not find an existing airstrip for %s, skipping" % old_ident)
        continue
    print("Changing %s => %s" % (old_ident, new_ident))
    airstrip.ident = new_ident
    airstrip.save()

print("Done!")
