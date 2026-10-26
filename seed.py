"""Initial data loaded with individual add() calls."""

from datetime import datetime, timedelta

from structures.hospital_map import FacilityNode


def add_area(hospital, floor_name, area_name, area_code, bed_prefix, bed_code, beds):
    hospital.add_child(floor_name, FacilityNode(area_name, "area", area_code))
    number = 1
    while number <= beds:
        suffix = str(number).zfill(2)
        hospital.add_child(area_name, FacilityNode(bed_prefix + "-" + suffix, "bed", bed_code + str(number)))
        number += 1


def seed_hospital(hospital):
    hospital.add(FacilityNode("Hospital Universitario San Rafael", "hospital", "HUSR"))
    hospital.add_child("Hospital Universitario San Rafael", FacilityNode("Piso 1", "floor", "P1"))
    hospital.add_child("Hospital Universitario San Rafael", FacilityNode("Piso 2", "floor", "P2"))
    add_area(hospital, "Piso 1", "Reanimación", "REA", "REA", "R", 3)
    add_area(hospital, "Piso 1", "Urgencias Adultos", "URG", "URG", "U", 6)
    add_area(hospital, "Piso 1", "Pediatría", "PED", "PED", "P", 4)
    add_area(hospital, "Piso 2", "Observación", "OBS", "OBS", "O", 5)
    add_area(hospital, "Piso 2", "UCI", "UCI", "UCI", "I", 4)


def admit(service, document_id, full_name, age, symptoms, minutes_ago):
    patient = service.admit(document_id, full_name, age, symptoms).patient
    patient.arrival_time = datetime.now() - timedelta(minutes=minutes_ago)
    return patient


def answer(service, patient, value):
    """Answer the current decision tree question for the patient."""
    service.answer_triage(patient.document_id, patient.triage_node_id, value)


def load_seed_data(service):
    seed_hospital(service.hospital)

    # Patients already in care (attended in priority order)
    jorge = admit(service, "79456123", "Jorge Eliécer Martínez", 71, "Inconsciente tras una caída en casa", 95)
    answer(service, jorge, "yes")

    carlos = admit(service, "1019876543", "Carlos Andrés Rodríguez", 58, "Dolor torácico opresivo irradiado al brazo izquierdo", 80)
    answer(service, carlos, "no")
    answer(service, carlos, "yes")
    answer(service, carlos, "no")

    valentina = admit(service, "1122334455", "Valentina Gómez Rojas", 8, "Fiebre de 39,8 °C y vómito desde la mañana", 70)
    answer(service, valentina, "no")
    answer(service, valentina, "no")
    answer(service, valentina, "yes")
    answer(service, valentina, "no")

    camila = admit(service, "1015432198", "Camila Torres Beltrán", 27, "Dolor de garganta de 4 días con fiebre leve", 150)
    answer(service, camila, "no")
    answer(service, camila, "no")
    answer(service, camila, "no")
    answer(service, camila, "yes")

    service.attend_next()
    service.attend_next()
    service.attend_next()
    service.attend_next()
    service.discharge("1015432198")

    # Patients waiting in the priority queue
    luz = admit(service, "52789456", "Luz Marina Castaño", 45, "Dolor abdominal intenso (9/10) en fosa ilíaca derecha", 48)
    answer(service, luz, "no")
    answer(service, luz, "no")
    answer(service, luz, "yes")
    answer(service, luz, "no")

    santiago = admit(service, "1001234567", "Santiago Herrera López", 23, "Esguince de tobillo jugando fútbol", 40)
    answer(service, santiago, "no")
    answer(service, santiago, "no")
    answer(service, santiago, "no")
    answer(service, santiago, "no")
    answer(service, santiago, "yes")

    ana = admit(service, "43567890", "Ana Lucía Restrepo", 66, "Dificultad respiratoria, labios morados y confusión", 6)
    answer(service, ana, "no")
    answer(service, ana, "yes")
    answer(service, ana, "yes")

    daniela = admit(service, "1098765432", "Daniela Ospina Mejía", 31, "Tos leve de dos días sin fiebre", 25)
    answer(service, daniela, "no")
    answer(service, daniela, "no")
    answer(service, daniela, "no")
    answer(service, daniela, "no")
    answer(service, daniela, "no")

    andres = admit(service, "80123456", "Andrés Felipe Vargas", 39, "Dolor lumbar moderado desde hace 5 días", 18)
    answer(service, andres, "no")
    answer(service, andres, "no")
    answer(service, andres, "no")
    answer(service, andres, "yes")
