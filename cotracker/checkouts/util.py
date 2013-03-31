from .models import AircraftType


def get_aircrafttype_names(order="name"):
    """Populates a sorted list with the names of all known
    AircraftTypes"""
    aircrafttypes = AircraftType.objects.order_by(order)
    return [actype.name for actype in aircrafttypes]
