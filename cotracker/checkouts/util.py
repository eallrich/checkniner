import datetime
import json
import logging
import os

from django.conf import settings
from django.contrib.auth.models import User
import requests

from .models import AircraftType, Airstrip, Checkout, PilotWeight

# ISO 8601 YYYY-MM-DDTHH:MM:SS
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


logger = logging.getLogger(__name__)


"""
Checkout States
---------------
+ Sudah: The pilot has been checked out at the airstrip in the aircraft type
+ Belum: The pilot has not been checked out at the airstrip in the aircraft
         type, but another pilot has.
+ Unprecedented: No pilot has been checked out at the airstrip in the aircraft
                 type.

These states have corresponding names in the CSS file to make them easy to
style as necessary.
"""
CHECKOUT_SUDAH = "sudah"
CHECKOUT_SUDAH_LABEL = "Sudah Selesai"
CHECKOUT_BELUM = "belum"
CHECKOUT_BELUM_LABEL = "Belum Selesai"
CHECKOUT_UNPRECEDENTED = "unprecedented"


def choices_checkout_status():
    """Provides a consistent method for getting the list of choice tuples."""
    return [(CHECKOUT_SUDAH, CHECKOUT_SUDAH_LABEL), (CHECKOUT_BELUM, CHECKOUT_BELUM_LABEL)]


def get_pilots():
    """Returns an ordered queryset of Users in the Pilots group"""
    return User.objects.filter(groups__name="Pilots").order_by('last_name','first_name')


def get_bases():
    """Returns an ordered queryset of Airstrips which are bases"""
    return Airstrip.objects.filter(is_base=True).order_by('ident')


def get_aircrafttype_names(order="sorted_position"):
    """Populates a sorted list with the names of all known AircraftTypes"""
    aircrafttypes = AircraftType.objects.order_by(order)
    return [actype.name for actype in aircrafttypes]


def get_pilot_airstrip_pairs(pilot=None, airstrip=None, base=None, **kwargs):
    """Populates a sorted list of Pilot/Airstrip tuples"""
    pilots = get_pilots()
    if pilot is not None:
        # Limiting to the requested object and maintaining iterability
        pilots = [pilots.get(pk=pilot.pk),]
    airstrips = Airstrip.objects.all().order_by('ident')
    if airstrip is not None:
        # Limiting to the requested object and maintaining iterability
        airstrips = [airstrips.get(pk=airstrip.pk),]
    elif base is not None:
        airstrips = airstrips.filter(bases=base)
    
    pairs = []
    for p in pilots:
        for a in airstrips:
            pairs.append((p.username, a.ident))
    
    return pairs


def get_precedented_checkouts():
    """Provides a two-tier dictionary summarizing whether each airstrip has an
    existing checkout entry for each aircraft.
    
    precedented = {
        'airstrip_ident': {
            'actype': True,
        },
    }
    """
    precedented = {}
    
    actypes = AircraftType.objects.all()
    for actype in actypes:
        checkouts = Checkout.objects.filter(aircraft_type=actype).select_related('airstrip')
        airstrips = []
        for c in checkouts:
            if c.airstrip not in airstrips:
                airstrips.append(c.airstrip)
        for a in airstrips:
            if a.ident not in precedented:
                precedented[a.ident] = {}
            precedented[a.ident][actype.name] = True
    
    return precedented


def checkout_filter(pilot=None, airstrip=None, base=None, aircraft_type=None, **kwargs):
    """Core function for collecting a set of checkout objects"""
    core_query = Checkout.objects.all()
    if pilot != None:
        core_query = core_query.filter(pilot=pilot)
    if airstrip != None:
        core_query = core_query.filter(airstrip=airstrip)
    if base != None:
        core_query = core_query.filter(airstrip__bases=base)
    if aircraft_type != None:
        core_query = core_query.filter(aircraft_type=aircraft_type)
        
    checkouts = core_query.select_related(
                    'pilot', 'airstrip', 'aircraft_type'
                ).order_by(
                    'pilot__last_name',
                    'pilot__first_name',
                    'airstrip__ident',
                    'aircraft_type__name'
                )
    if aircraft_type:
        actypes = [aircraft_type.name,] # List for iterability
    else:
        actypes = get_aircrafttype_names()
    results = []
    for c in checkouts:
        if results:
            r = results.pop()
            if r['pilot_slug'] == c.pilot.username and r['airstrip_ident'] == c.airstrip.ident:
                r['actypes'][c.aircraft_type.name] = CHECKOUT_SUDAH
                results.append(r)
                continue
            else:
                # Put the unmodified record back in the list before creating
                # the new record
                results.append(r)
                
        r = {
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': c.airstrip.ident,
            'airstrip_name': c.airstrip.name,
            'actypes': {},
        }
        for actype in actypes:
            if actype == c.aircraft_type.name:
                # Mark the entry for the current checkout aircraft during init
                r['actypes'][actype] = CHECKOUT_SUDAH
            else:
                r['actypes'][actype] = CHECKOUT_BELUM
        
        results.append(r)
    return results


def sudah_selesai(**kwargs):
    """Gathers complete checkouts and returns them in a dictionary format as
    expected by the display_checkouts template."""
    if 'aircraft_type' in kwargs and kwargs['aircraft_type']:
        actypes = [kwargs['aircraft_type'].name, ]
    else:
        actypes = get_aircrafttype_names()
    
    results = {
        'populate': {
            'pilot': True,
            'airstrip': True,
        },
        'aircraft_types': actypes,
        'results': checkout_filter(**kwargs),
    }
    
    return results


def belum_selesai(**kwargs):
    """Gathers incomplete checkouts and returns them in a dictionary format as
    expected by the display_checkouts template."""
    results = {
        'populate': {
            'pilot': True,
            'airstrip': True,
        },
    }
    
    original_checkouts = checkout_filter(**kwargs)
    if 'aircraft_type' in kwargs and kwargs['aircraft_type']:
        actypes = [kwargs['aircraft_type'].name, ]
    else:
        actypes = get_aircrafttype_names()
    results['aircraft_types'] = actypes
    pilots_v_airstrips = get_pilot_airstrip_pairs(**kwargs)
    next_pair_index = 0
    
    belum_selesai_checkouts = []
    for c in original_checkouts:
        current_pair = (c['pilot_slug'], c['airstrip_ident'])
        expected_pair = pilots_v_airstrips[next_pair_index]
        while current_pair != expected_pair:
            # Need to insert the missing pair
            pilot_slug, airstrip_ident = expected_pair
            pilot = User.objects.get(username=pilot_slug)
            airstrip = Airstrip.objects.get(ident=airstrip_ident)
            new_result = {
                'pilot_name': pilot.full_name,
                'pilot_slug': pilot_slug,
                'airstrip_ident': airstrip_ident,
                'airstrip_name': airstrip.name,
                'actypes': {},
            }
            for actype in actypes:
                new_result['actypes'][actype] = CHECKOUT_BELUM
            
            belum_selesai_checkouts.append(new_result)
            
            # Still missing a Pilot/Airstrip pair?
            next_pair_index += 1
            expected_pair = pilots_v_airstrips[next_pair_index]
        
        belum_selesai_checkouts.append(c)
        # Prepare for the next check
        next_pair_index += 1
    
    if next_pair_index != len(pilots_v_airstrips):
        # Still some missing pairs
        for i in range(next_pair_index, len(pilots_v_airstrips)):
            expected_pair = pilots_v_airstrips[i]
            pilot_slug, airstrip_ident = expected_pair
            pilot = User.objects.get(username=pilot_slug)
            airstrip = Airstrip.objects.get(ident=airstrip_ident)
            new_result = {
                'pilot_name': pilot.full_name,
                'pilot_slug': pilot_slug,
                'airstrip_ident': airstrip_ident,
                'airstrip_name': airstrip.name,
                'actypes': {},
            }
            for actype in actypes:
                new_result['actypes'][actype] = CHECKOUT_BELUM
            
            belum_selesai_checkouts.append(new_result)
    
    precedented = get_precedented_checkouts()
    checkouts = []
    for c in belum_selesai_checkouts:
        ident = c['airstrip_ident']
        incomplete = False
        unprecedented_count = 0
        for ac, status in c['actypes'].items():
            if status == CHECKOUT_BELUM:
                incomplete = True
                # A Belum should be changed to Unprecedented when no pilot has
                # been checked out at the given location in the given AircraftType
                if ident not in precedented or ac not in precedented[ident]:
                    c['actypes'][ac] = CHECKOUT_UNPRECEDENTED
                    unprecedented_count += 1
        
        # Only save entries with BELUM or UNPRECEDENTED statuses
        if incomplete:
            # But only if the airstrip has at least one valid checkout. If it
            # doesn't have any existing checkouts, then we're not going to show
            # it at as a 'belum selesai' airstrip.
            if ident not in precedented:
                logger.debug("Dropping %s: airstrip is globally unprecedented" % ident)
            else:
                checkouts.append(c)
    
    results['results'] = checkouts
    return results


def pilot_checkouts_grouped_by_airstrip(pilot):
    """Organizes the pilot's checkouts by airstrip."""
    results = sudah_selesai(pilot=pilot)
    results['populate']['pilot'] = False
    return results


def airstrip_checkouts_grouped_by_pilot(airstrip):
    """Organizes the airstrip's checkouts by pilot."""
    results = sudah_selesai(airstrip=airstrip)
    results['populate']['airstrip'] = False
    return results


def export_pilotweights():
    """Regenerates the 'static' files containing the PilotWeights"""
    pilotweights = PilotWeight.objects.all().order_by("pilot__last_name", "pilot__first_name")
    logger.info("Exporting %d PilotWeight records to static files" % len(pilotweights))

    to_export = {
        "version": "1",
        "updated": datetime.datetime.utcnow().strftime(DATE_FORMAT),
        "pilots": [],
    }
    for pw in pilotweights:
        data = {
            'lastname': pw.pilot.last_name,
            'firstname': pw.pilot.first_name,
            'weight': pw.weight,
        }
        to_export["pilots"].append(data)

    jsonpath = os.path.join(settings.STATIC_ROOT, settings.PILOTWEIGHTS_JSON_FILE)
    with open(jsonpath, 'w') as f:
        json.dump(to_export, f, indent=4, sort_keys=True)
    logger.info("Wrote %d bytes to %s" % (os.path.getsize(jsonpath), jsonpath))

    xmlpath = os.path.join(settings.STATIC_ROOT, settings.PILOTWEIGHTS_XML_FILE)
    with open(xmlpath, 'w') as f:
        f.write("<pilotweights>\n")
        f.write("  <version>%s</version>\n" % to_export["version"])
        f.write("  <updated>%s</updated>\n" % to_export["updated"])
        for pilot in to_export["pilots"]:
            f.write("  <pilot>\n")
            f.write("    <lastname>%s</lastname>\n" % pilot["lastname"])
            f.write("    <firstname>%s</firstname>\n" % pilot["firstname"])
            f.write("    <weight>%d</weight>\n" % pilot["weight"])
            f.write("  </pilot>\n")
        f.write("</pilotweights>\n")
    logger.info("Wrote %d bytes to %s" % (os.path.getsize(xmlpath), xmlpath))


def notify_pilotweight_update(pilotweight):
    """Informs another party via email that a pilot weight has been updated"""
    if settings.MAILGUN_CONFIG is None:
        logger.warn("Received request to send weight update notification email, but no email settings are configured. The settings.MAILGUN_CONFIG dictionary must be populated before email can be sent.")
        return
    name = pilotweight.pilot.full_name
    weight = pilotweight.weight
    message = "The pilot weight for '%s' has been updated to %d." % (name, weight)
    mgconfig = settings.MAILGUN_CONFIG
    logger.info("Sending weight update notification to '%s'" % mgconfig['send_weight_notify_to'])

    data = {
        'from':    mgconfig['from'],
        'to':      mgconfig['send_weight_notify_to'],
        'subject': 'Checkouts App: Pilot Weight Updated',
        'text':    message,
    }
    if mgconfig['send_weight_notify_cc'] is not None:
        data['cc'] = mgconfig['send_weight_notify_cc']
    if mgconfig['send_weight_notify_bcc'] is not None:
        data['bcc'] = mgconfig['send_weight_notify_bcc']

    response = requests.post(
        mgconfig['api_url'],
        auth=('api', mgconfig['api_key']),
        data=data)
    logger.info("Response status: %d, text: %s" % (response.status_code, response.text))


def get_pilotweights_mtime():
    """Enables the pilotweight_list view to report the export file's status."""
    jsonpath = os.path.join(settings.STATIC_ROOT, settings.PILOTWEIGHTS_JSON_FILE)
    if not os.path.exists(jsonpath):
        return None
    timestamp = os.path.getmtime(jsonpath)
    return datetime.datetime.fromtimestamp(timestamp)
