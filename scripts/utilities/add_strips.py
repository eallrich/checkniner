import sys

from checkouts.models import Airstrip

def main(airstrips_file, base_ident):
    print("Loading from %s and associating with %s" % (airstrips_file, base_ident))
    base = Airstrip.objects.get(ident=base_ident)
    with open(airstrips_file, 'rb') as f:
        lines = [r.strip().split(',') for r in f]
    for ident, name in lines:
        name = name.title()
        print("Adding Airstrip with ident=%s and name=%s" % (ident, name))
        airstrip = Airstrip.objects.create(ident=ident, name=name, is_base=False)
        airstrip.bases.add(base)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python %s [file with new airstrips] [ident of base to attach]" % sys.argv[0])
        sys.exit(1)

    import django
    django.setup()

    _, airstrips_file, base_ident = sys.argv
    main(airstrips_file, base_ident)
    print("Done!")
