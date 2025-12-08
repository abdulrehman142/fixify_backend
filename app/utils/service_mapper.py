"""
Utility to map service names to service categories.
Maps service names from frontend to the 9 service provider categories.
"""

SERVICE_CATEGORY_MAP = {
    # Cleaning services -> cleaner
    "home cleaning": "cleaner",
    "home-cleaning": "cleaner",
    "office cleaning": "cleaner",
    "office-cleaning": "cleaner",
    "toilet cleaning": "cleaner",
    "toilet-cleaning": "cleaner",
    "pest cleaning": "cleaner",
    "pest-cleaning": "cleaner",
    "sofa cleaning": "cleaner",
    "sofa-cleaning": "cleaner",
    "glass cleaning": "cleaner",
    "glass-cleaning": "cleaner",
    "kitchen cleaning": "cleaner",
    "kitchen-cleaning": "cleaner",
    "water tank cleaning": "cleaner",
    "water-tank-cleaning": "cleaner",
    
    # Electrical services -> electrician
    "fan repair installation": "electrician",
    "fan-repair-installation": "electrician",
    "circuit breaker repair installation": "electrician",
    "circuit-breaker-repair-installation": "electrician",
    "generator repair installation": "electrician",
    "generator-repair-installation": "electrician",
    "socket repair installation": "electrician",
    "socket-repair-installation": "electrician",
    "light repair installation": "electrician",
    "light-repair-installation": "electrician",
    "wiring rewiring": "electrician",
    "wiring-rewiring": "electrician",
    "switchboard repair installation": "electrician",
    "switchboard-repair-installation": "electrician",
    
    # Plumbing services -> plumber
    "leak repair": "plumber",
    "leak-repair": "plumber",
    "pipe installation": "plumber",
    "pipe-installation": "plumber",
    "drain unclogging": "plumber",
    "drain-unclogging": "plumber",
    "gyser installation": "plumber",
    "gyser-installation": "plumber",
    "bathroom fittings installation": "plumber",
    "bathroom-fittings-installation": "plumber",
    "sink repair": "plumber",
    "kitchen-sink-repair": "plumber",
    "toilet repair installation": "plumber",
    "toilet-repair-installation": "plumber",
    
    # Mechanical services -> mechanic
    "car engine tune": "mechanic",
    "car-engine-tune": "mechanic",
    "brake service": "mechanic",
    "brake-service": "mechanic",
    "oil change": "mechanic",
    "oil-change": "mechanic",
    "ac repair": "mechanic",
    "ac-repair": "mechanic",
    "battery replacement": "mechanic",
    "battery-replacement": "mechanic",
    "suspension repair": "mechanic",
    "suspension-repair": "mechanic",
    "wheel repair": "mechanic",
    "wheel-repair": "mechanic",
    "diagnostic scanning": "mechanic",
    "diagnostic-scanning": "mechanic",
    
    # Moving services -> mover
    "home shifting": "mover",
    "home-shifting": "mover",
    "office relocation": "mover",
    "office-relocation": "mover",
    "packing unpacking": "mover",
    "packing-unpacking": "mover",
    "loading unloading": "mover",
    "loading-unloading": "mover",
    "intercity moving": "mover",
    "intercity-moving": "mover",
    
    # Technician services -> technician
    "ac installation repair": "technician",
    "ac-installation-repair": "technician",
    "refrigerator repair": "technician",
    "refrigerator-repair": "technician",
    "washing machine repair": "technician",
    "washing-machine-repair": "technician",
    "microwave repair": "technician",
    "microwave-repair": "technician",
    "cctv installation": "technician",
    "cctv-installation": "technician",
    "tv repair installation": "technician",
    "tv-repair-installation": "technician",
    
    # Painting services -> painter
    "interior painting": "painter",
    "interior-painting": "painter",
    "exterior painting": "painter",
    "exterior-painting": "painter",
    "door paint": "painter",
    "door-paint": "painter",
    "wooden paint": "painter",
    "wooden-paint": "painter",
    "commercial painting": "painter",
    "commercial-painting": "painter",
    
    # Gardening services -> gardener
    "lawn maintenance": "gardener",
    "lawn-maintenance": "gardener",
    "planting replanting": "gardener",
    "planting-replanting": "gardener",
    "hedge trimming": "gardener",
    "hedge-trimming": "gardener",
    "pest control plants": "gardener",
    "pest-control-plants": "gardener",
    "fertilizer treatment": "gardener",
    "fertilizer-treatment": "gardener",
    
    # Carpentry services -> carpenter
    "furniture repair": "carpenter",
    "furniture-repair": "carpenter",
    "custom furniture": "carpenter",
    "custom-furniture": "carpenter",
    "door lock installation": "carpenter",
    "door-lock-installation": "carpenter",
    "wooden flooring": "carpenter",
    "wooden-flooring": "carpenter",
    "shelves installation": "carpenter",
    "shelves-installation": "carpenter",
    "bed repair": "carpenter",
    "bed-repair": "carpenter",
}


def get_service_category(service_name: str) -> str:
    """
    Map a service name to its corresponding service category.
    Returns the category if found, otherwise defaults to 'cleaner'.
    """
    # Normalize service name: lowercase and strip whitespace
    normalized = service_name.lower().strip()
    
    # Direct match
    if normalized in SERVICE_CATEGORY_MAP:
        return SERVICE_CATEGORY_MAP[normalized]
    
    # Partial match - check if any key is contained in the service name
    for key, category in SERVICE_CATEGORY_MAP.items():
        if key in normalized or normalized in key:
            return category
    
    # Default fallback
    return "cleaner"

