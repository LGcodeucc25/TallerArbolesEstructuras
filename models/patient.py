"""Patient model."""

from datetime import datetime

from models.triage_level import level_info

STATUS_TRIAGE = "triage"
STATUS_WAITING = "waiting"
STATUS_IN_CARE = "in_care"
STATUS_DISCHARGED = "discharged"


def status_label(status):
    """Spanish label for a patient status."""
    if status == STATUS_TRIAGE:
        return "Pendiente de triage"
    if status == STATUS_WAITING:
        return "En espera"
    if status == STATUS_IN_CARE:
        return "En atención"
    if status == STATUS_DISCHARGED:
        return "Dado de alta"
    return "Desconocido"


class TriageStep:
    """One answered question of the triage decision tree (linked chain)."""

    def __init__(self, node_id, text, answer):
        self.node_id = node_id
        self.text = text
        self.answer = answer
        self.next = None


class Patient:
    """A person attended in the emergency room."""

    def __init__(self, document_id, full_name, age, symptoms):
        self.document_id = document_id
        self.full_name = full_name
        self.age = age
        self.symptoms = symptoms
        self.arrival_number = 0
        self.arrival_time = datetime.now()
        self.triage_level = None
        self.status = STATUS_TRIAGE
        self.bed_name = None
        self.triage_node_id = None
        self.first_step = None
        self.last_step = None
        self.visits = 1

    def reset_triage(self, root_id):
        """Start a new triage from the decision tree root."""
        self.triage_level = None
        self.triage_node_id = root_id
        self.first_step = None
        self.last_step = None
        self.status = STATUS_TRIAGE

    def add_step(self, node_id, text, answer):
        """Append an answered question to the triage path."""
        step = TriageStep(node_id, text, answer)
        if self.first_step is None:
            self.first_step = step
        else:
            self.last_step.next = step
        self.last_step = step

    def path_steps(self):
        """Yield the triage path from the first question."""
        current = self.first_step
        while current is not None:
            yield current
            current = current.next

    def path_contains(self, node_id):
        """True if the decision node was visited during triage."""
        for step in self.path_steps():
            if step.node_id == node_id:
                return True
        return node_id == self.triage_node_id

    def count_steps(self):
        total = 0
        for _ in self.path_steps():
            total += 1
        return total

    def level(self):
        return level_info(self.triage_level)

    def status_label(self):
        return status_label(self.status)

    def wait_minutes(self):
        """Minutes elapsed since arrival."""
        delta = datetime.now() - self.arrival_time
        return int(delta.total_seconds() // 60)

    def wait_text(self):
        minutes = self.wait_minutes()
        if minutes < 60:
            return str(minutes) + " min"
        return str(minutes // 60) + " h " + str(minutes % 60) + " min"

    def is_overdue(self):
        info = self.level()
        if info is None or self.status != STATUS_WAITING:
            return False
        return self.wait_minutes() > info.max_wait_minutes

    def initials(self):
        """First letter of the first two words of the name."""
        result = ""
        take_next = True
        for char in self.full_name:
            if char == " ":
                take_next = True
            elif take_next and len(result) < 2:
                result += char.upper()
                take_next = False
            else:
                take_next = False
        return result

    def short_name(self):
        """First name plus the first surname initial."""
        first = ""
        surname_initial = ""
        spaces = 0
        for char in self.full_name:
            if char == " ":
                spaces += 1
            elif spaces == 0:
                first += char
            elif surname_initial == "":
                surname_initial = char.upper()
        if surname_initial:
            return first + " " + surname_initial + "."
        return first
