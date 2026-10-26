"""MediTree Urgencias - Flask routes."""

from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from models.patient import STATUS_IN_CARE, STATUS_TRIAGE, STATUS_WAITING, STATUS_DISCHARGED
from models.triage_level import all_levels, level_info
from seed import load_seed_data
from services.hospital_service import HospitalService
from services import tree_layout

app = Flask(__name__)
app.secret_key = "meditree-urgencias-dev-key"

service = HospitalService()
load_seed_data(service)


def current_shift(now):
    if 7 <= now.hour < 13:
        return "Turno mañana · 07:00–13:00"
    if 13 <= now.hour < 19:
        return "Turno tarde · 13:00–19:00"
    return "Turno noche · 19:00–07:00"


def weekday_name(number):
    if number == 0:
        return "lunes"
    if number == 1:
        return "martes"
    if number == 2:
        return "miércoles"
    if number == 3:
        return "jueves"
    if number == 4:
        return "viernes"
    if number == 5:
        return "sábado"
    return "domingo"


def month_name(number):
    names = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre"
    position = 1
    word = ""
    for char in names + " ":
        if char == " ":
            if position == number:
                return word
            position += 1
            word = ""
        else:
            word += char
    return ""


def spanish_date(now):
    return weekday_name(now.weekday()) + ", " + str(now.day) + " de " + month_name(now.month) + " de " + str(now.year)


def greeting(now):
    if now.hour < 12:
        return "Buenos días"
    if now.hour < 19:
        return "Buenas tardes"
    return "Buenas noches"


def first_pending_triage():
    """First patient (by document) still waiting to answer the triage."""
    for patient in service.registry.patients():
        if patient.status == STATUS_TRIAGE:
            return patient
    return None


@app.context_processor
def inject_globals():
    now = datetime.now()
    return {
        "hospital_name": service.hospital.root.name,
        "now": now,
        "today_text": spanish_date(now),
        "greeting": greeting(now),
        "pending_triage": first_pending_triage(),
        "shift": current_shift(now),
        "level_info": level_info,
        "all_levels": all_levels,
        "waiting_badge": service.waiting_count(),
        "STATUS_TRIAGE": STATUS_TRIAGE,
        "STATUS_WAITING": STATUS_WAITING,
        "STATUS_IN_CARE": STATUS_IN_CARE,
        "STATUS_DISCHARGED": STATUS_DISCHARGED,
    }


@app.route("/")
def dashboard():
    return render_template("dashboard.html", service=service, next_node=service.queue.peek_next())


@app.route("/admit", methods=("GET", "POST"))
def admit():
    if request.method == "POST":
        document_id = request.form.get("document_id", "").strip()
        full_name = request.form.get("full_name", "").strip()
        age_text = request.form.get("age", "").strip()
        symptoms = request.form.get("symptoms", "").strip()
        if not document_id.isdigit() or len(document_id) < 5 or len(document_id) > 12:
            flash("El documento debe tener entre 5 y 12 dígitos.", "error")
        elif len(full_name) < 3:
            flash("Ingrese el nombre completo del paciente.", "error")
        elif not age_text.isdigit() or int(age_text) > 120:
            flash("Ingrese una edad válida (0 a 120 años).", "error")
        elif symptoms == "":
            flash("Describa el motivo de consulta.", "error")
        else:
            result = service.admit(document_id, full_name, int(age_text), symptoms)
            if not result.ok:
                flash(result.message, "warning")
                return redirect(url_for("patient_detail", document_id=document_id))
            flash(result.message, "success")
            return redirect(url_for("triage", document_id=document_id, node_id=result.patient.triage_node_id))
        return render_template("admit.html", form=request.form, previous=None)

    previous = service.find_patient(request.args.get("document_id", ""))
    return render_template("admit.html", form=None, previous=previous)


@app.route("/triage/<document_id>/<node_id>")
def triage(document_id, node_id):
    patient = service.find_patient(document_id)
    node = service.decision_tree.find_node(node_id)
    if patient is None or node is None:
        flash("Paciente o pregunta de triage no encontrados.", "error")
        return redirect(url_for("patients"))
    if patient.status == STATUS_TRIAGE and node_id != patient.triage_node_id:
        return redirect(url_for("triage", document_id=document_id, node_id=patient.triage_node_id))
    if not node.is_leaf() and patient.status != STATUS_TRIAGE:
        return redirect(url_for("patient_detail", document_id=document_id))
    step = service.decision_tree.depth_of(node_id) + 1
    total_steps = service.decision_tree.get_height(service.decision_tree.root) - 1
    drawing = tree_layout.decision_drawing(service.decision_tree, patient)
    return render_template(
        "triage.html",
        patient=patient,
        node=node,
        step=step,
        total_steps=total_steps,
        drawing=drawing,
    )


@app.route("/triage/<document_id>/<node_id>/answer", methods=("POST",))
def triage_answer(document_id, node_id):
    answer = request.form.get("answer", "")
    if answer != "yes" and answer != "no":
        flash("Respuesta no válida.", "error")
        return redirect(url_for("triage", document_id=document_id, node_id=node_id))
    next_node = service.answer_triage(document_id, node_id, answer)
    if next_node is None:
        flash("No fue posible registrar la respuesta.", "error")
        return redirect(url_for("patients"))
    if next_node.is_leaf():
        info = level_info(next_node.result_level)
        flash("Clasificado como Nivel " + str(info.number) + " · " + info.name + ". El paciente ingresó a la cola.", "success")
    return redirect(url_for("triage", document_id=document_id, node_id=next_node.node_id))


@app.route("/queue")
def queue():
    return render_template("queue.html", service=service, next_node=service.queue.peek_next())


@app.route("/queue/attend", methods=("POST",))
def attend_next():
    result = service.attend_next()
    if result.ok:
        flash(result.message, "success")
    else:
        flash(result.message, "warning")
    return redirect(url_for("queue"))


@app.route("/patients")
def patients():
    return render_template("patients.html", service=service, query="")


@app.route("/patients/search")
def patients_search():
    query = request.args.get("document_id", "").strip()
    patient = service.find_patient(query)
    if patient is None:
        flash("No se encontró ningún paciente con el documento " + query + ".", "warning")
        return render_template("patients.html", service=service, query=query)
    return redirect(url_for("patient_detail", document_id=patient.document_id))


@app.route("/patients/<document_id>")
def patient_detail(document_id):
    patient = service.find_patient(document_id)
    if patient is None:
        flash("Paciente no encontrado.", "error")
        return redirect(url_for("patients"))
    bed = service.bed_of(patient)
    bed_path = None
    if bed is not None:
        bed_path = service.hospital.path_text(bed)
    return render_template("patient_detail.html", patient=patient, bed=bed, bed_path=bed_path)


@app.route("/patients/<document_id>/discharge", methods=("POST",))
def discharge(document_id):
    result = service.discharge(document_id)
    if result.ok:
        flash(result.message, "success")
    else:
        flash(result.message, "error")
    return redirect(url_for("patient_detail", document_id=document_id))


@app.route("/beds")
def beds():
    return render_template("beds.html", service=service, hospital=service.hospital)


@app.route("/structures")
def structures():
    registry = service.registry
    return render_template(
        "structures.html",
        service=service,
        avl=tree_layout.avl_drawing(registry),
        queue_tree=tree_layout.queue_drawing(service.queue),
        decision=tree_layout.decision_drawing(service.decision_tree),
        hospital_tree=tree_layout.hospital_drawing(service.hospital),
    )


if __name__ == "__main__":
    app.run(debug=True)
