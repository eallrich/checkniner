from .models import AircraftType, Checkout


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
CHECKOUT_BELUM = "belum"
CHECKOUT_UNPRECEDENTED = "unprecedented"


def get_aircrafttype_names(order="name"):
    """Populates a sorted list with the names of all known AircraftTypes"""
    aircrafttypes = AircraftType.objects.order_by(order)
    return [actype.name for actype in aircrafttypes]


def pilot_checkouts_grouped_by_airstrip(pilot):
    """Organizes the pilot's checkouts by airstrips.
    
    Returns a list (sorted by airstrip ident) in which every airstrip at which
    the given pilot is checked out is a dictionary, with a key:value pair 
    indicating whether the pilot is checked out or not in each AircraftType."""
    actypes = get_aircrafttype_names()

    pilot_checkouts = Checkout.objects.filter(pilot=pilot).select_related('airstrip', 'aircraft_type')
    pilot_checkouts = pilot_checkouts.order_by('airstrip__ident', 'aircraft_type__name')
    
    by_airstrip = []
    row_data = None
    for c in pilot_checkouts:
	if row_data == None or c.airstrip.ident != row_data['ident']:
	    # Don't save on the initial loop iteration
	    if row_data != None:
		by_airstrip.append(row_data)
	    
	    row_data = {
		'ident': c.airstrip.ident,
		'name': c.airstrip.name,
		'aircraft': [CHECKOUT_BELUM,] * len(actypes),
	    }
	
	ac_index = actypes.index(c.aircraft_type.name)
	row_data['aircraft'][ac_index] = CHECKOUT_SUDAH
    
    # Saving the very last airstrip record is missed by 
    # the 'is this the same airstrip as before?' check,
    # so we'll manually save it to the list (if necessary)
    if row_data != None:
        by_airstrip.append(row_data)
    
    return by_airstrip


def airstrip_checkouts_grouped_by_pilot(airstrip):
    """Organizes the airstrip's checkouts by pilot.
    
    Returns a list (sorted by pilot last name then first name) in which every
    pilot checked out at the given airstrip is a dictionary, with a key:value
    pair indicating whether the pilot is checked out or not in each 
    AircraftType.
    """
    actypes = get_aircrafttype_names()
    
    airstrip_checkouts = Checkout.objects.filter(airstrip=airstrip).select_related('pilot', 'aircraft_type')
    airstrip_checkouts = airstrip_checkouts.order_by('pilot__last_name', 'pilot__first_name', 'aircraft_type__name')
    
    by_pilot = []
    row_data = None
    for c in airstrip_checkouts:
	if row_data == None or c.pilot.username != row_data['pilot_username']:
	    # Don't save on the initial loop iteration
	    if row_data != None:
		by_pilot.append(row_data)
	    
	    row_data = {
		'pilot_name': c.get_pilot_name(),
		'pilot_username': c.pilot.username,
		'aircraft': [CHECKOUT_BELUM,] * len(actypes),
	    }
	
	ac_index = actypes.index(c.aircraft_type.name)
	row_data['aircraft'][ac_index] = CHECKOUT_SUDAH
    
    # Saving the very last airstrip record is missed by 
    # the 'is this the same airstrip as before?' check,
    # so we'll manually save it to the list (if necessary)
    if row_data != None:
        by_pilot.append(row_data)
    
    return by_pilot
