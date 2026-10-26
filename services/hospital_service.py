"""Orchestrates the four trees: admit, classify, attend, discharge, stats."""

from models.patient import (
    Patient,
    STATUS_DISCHARGED,
    STATUS_IN_CARE,
    STATUS_TRIAGE,
    STATUS_WAITING,
)
from models.triage_level import all_levels
from structures.hospital_map import HospitalMap
from structures.patient_registry import PatientRegistry
from structures.triage_decision import TriageDecisionTree
from structures.triage_queue import TriageQueue


class ServiceResult:
    """Outcome of an action, with a Spanish message for the UI."""

    def __init__(self, ok, message, patient=None):
        self.ok = ok
        self.message = message
        self.patient = patient


class LevelCount:
    """Active patients for one triage level."""

    def __init__(self, level, count):
        self.level = level
        self.count = count


class HospitalService:
    def __init__(self):
        self.registry = PatientRegistry()
        self.queue = TriageQueue()
        self.decision_tree = TriageDecisionTree()
        self.hospital = HospitalMap()
        self.arrival_counter = 0

    # ---- Patients -------------------------------------------------------

    def find_patient(self, document_id):
        return self.registry.search(document_id)

    def is_active(self, patient):
        return patient.status == STATUS_WAITING or patient.status == STATUS_IN_CARE

    def admit(self, document_id, full_name, age, symptoms):
        """Register (or update) a patient in the AVL and start triage."""
        existing = self.registry.search(document_id)
        if existing is not None and self.is_active(existing):
            return ServiceResult(False, "El paciente ya se encuentra en espera o en atención.", existing)
        patient = Patient(document_id, full_name, age, symptoms)
        if existing is not None:
            patient.visits = existing.visits + 1
        self.arrival_counter += 1
        patient.arrival_number = self.arrival_counter
        patient.reset_triage(self.decision_tree.get_root().node_id)
        self.registry.add(patient)
        if existing is not None:
            return ServiceResult(True, "Datos actualizados. Nuevo ingreso registrado.", patient)
        return ServiceResult(True, "Paciente registrado. Continúe con el triage.", patient)

    # ---- Triage ---------------------------------------------------------

    def answer_triage(self, document_id, node_id, answer):
        """Move one step down the decision tree; returns the next node."""
        patient = self.registry.search(document_id)
        node = self.decision_tree.find_node(node_id)
        if patient is None or node is None or node.is_leaf():
            return None
        if patient.status != STATUS_TRIAGE or patient.triage_node_id != node_id:
            return None
        patient.add_step(node.node_id, node.question, answer)
        if answer == "yes":
            next_node = node.yes
        else:
            next_node = node.no
        patient.triage_node_id = next_node.node_id
        if next_node.is_leaf():
            self.classify(patient, next_node.result_level)
        return next_node

    def classify(self, patient, level):
        """Assign the triage level and enqueue the patient."""
        patient.triage_level = level
        patient.status = STATUS_WAITING
        self.queue.add(patient, level)

    # ---- Attention and beds --------------------------------------------

    def candidate_areas(self, patient):
        """Areas to look for a bed, in order of preference."""
        level = patient.triage_level
        if patient.age < 14:
            yield "Pediatría"
            if level == 1:
                yield "Reanimación"
                yield "UCI"
            return
        if level == 1:
            yield "Reanimación"
            yield "UCI"
        elif level == 2:
            yield "Urgencias Adultos"
            yield "UCI"
        elif level == 3:
            yield "Observación"
            yield "Urgencias Adultos"
        else:
            yield "Urgencias Adultos"

    def find_bed_for(self, patient):
        for area_name in self.candidate_areas(patient):
            bed = self.hospital.find_free_bed(area_name)
            if bed is not None:
                return bed
        return None

    def attend_next(self):
        """Pop the most urgent patient and assign a bed."""
        next_node = self.queue.peek_next()
        if next_node is None:
            return ServiceResult(False, "No hay pacientes en la cola de atención.")
        patient = next_node.patient
        bed = self.find_bed_for(patient)
        if bed is None:
            return ServiceResult(False, "No hay camas disponibles para " + patient.full_name + " en las áreas asignadas.", patient)
        self.queue.pop_next()
        self.hospital.assign_bed(bed.name, patient)
        patient.bed_name = bed.name
        patient.status = STATUS_IN_CARE
        return ServiceResult(True, patient.full_name + " pasa a atención en la cama " + bed.name + " (" + bed.parent.name + ").", patient)

    def discharge(self, document_id):
        patient = self.registry.search(document_id)
        if patient is None:
            return ServiceResult(False, "Paciente no encontrado.")
        if patient.status != STATUS_IN_CARE:
            return ServiceResult(False, "Solo se puede dar de alta a pacientes en atención.", patient)
        bed_name = patient.bed_name
        self.hospital.release_bed(bed_name)
        patient.status = STATUS_DISCHARGED
        patient.bed_name = None
        return ServiceResult(True, patient.full_name + " fue dado de alta. Cama " + bed_name + " liberada.", patient)

    def bed_of(self, patient):
        if patient is None or patient.bed_name is None:
            return None
        return self.hospital.find(patient.bed_name)

    # ---- Stats ----------------------------------------------------------

    def count_by_status(self, status):
        total = 0
        for patient in self.registry.patients():
            if patient.status == status:
                total += 1
        return total

    def registered_count(self):
        return self.registry.count_nodes(self.registry.root)

    def waiting_count(self):
        return self.queue.size(self.queue.root)

    def total_beds(self):
        return self.hospital.count_beds(self.hospital.root)

    def occupied_beds(self):
        return self.hospital.count_occupied(self.hospital.root)

    def free_beds(self):
        return self.total_beds() - self.occupied_beds()

    def level_counts(self):
        """Yield active (waiting or in care) patients per triage level."""
        for level in all_levels():
            total = 0
            for patient in self.registry.patients():
                if self.is_active(patient) and patient.triage_level == level.number:
                    total += 1
            yield LevelCount(level, total)

    def areas(self):
        yield from self.hospital.nodes_of_kind("area")

    def floors(self):
        yield from self.hospital.nodes_of_kind("floor")
