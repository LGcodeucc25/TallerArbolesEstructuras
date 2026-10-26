"""Manchester triage levels (Resolution 5596 of 2015, Colombia)."""


class TriageLevel:
    """Display information for one triage level."""

    def __init__(self, number, name, label, color, max_wait_minutes, max_wait_text):
        self.number = number
        self.name = name
        self.label = label
        self.color = color
        self.max_wait_minutes = max_wait_minutes
        self.max_wait_text = max_wait_text


LEVEL_1 = TriageLevel(1, "Rojo", "Resucitación", "#dc2626", 0, "Inmediato")
LEVEL_2 = TriageLevel(2, "Naranja", "Emergencia", "#ea580c", 30, "≤ 30 min")
LEVEL_3 = TriageLevel(3, "Amarillo", "Urgencia", "#ca8a04", 120, "≤ 2 h")
LEVEL_4 = TriageLevel(4, "Verde", "Menos urgente", "#16a34a", 240, "≤ 4 h")
LEVEL_5 = TriageLevel(5, "Azul", "No urgente", "#2563eb", 480, "≤ 8 h")


def level_info(number):
    """Return the TriageLevel for a level number (None if unknown)."""
    if number == 1:
        return LEVEL_1
    if number == 2:
        return LEVEL_2
    if number == 3:
        return LEVEL_3
    if number == 4:
        return LEVEL_4
    if number == 5:
        return LEVEL_5
    return None


def all_levels():
    """Yield the five triage levels from most to least urgent."""
    number = 1
    while number <= 5:
        yield level_info(number)
        number += 1
