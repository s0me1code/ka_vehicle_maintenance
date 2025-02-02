from enum import Enum


class VehicleOwnershipType(Enum):
    RENTED = "Rental"
    LTO = "LTO"


class VehicleStatus(Enum):
    UNUSED = "Unused"  # defult

    SERVICED = "Serviced"
    OVERDUE = "Overdue"

    IN_GARAGE = "In Garage"
    NOTIFIED = "Notified"
    EARLY_NOTIFIED = "Early Notified"

    PENDING_APPROVAL = "Pending Approval"

    UPCOMING = "Upcoming"
    UNCHECKED = "Unchecked"


class AvailabilityStatus(Enum):
    ON_ROAD = "On Road"
    IN_GARAGE = "In Garage"
