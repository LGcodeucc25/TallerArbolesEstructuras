<p align="center">
  <img src="static/img/logo.svg" alt="MediTree" width="72">
</p>

# MediTree Urgencias

Sistema de gestión de urgencias hospitalarias construido en **Python (Flask)** sobre **estructuras de árboles implementadas a mano**.

Taller Árboles — Estructuras de Datos.

## Caso de estudio

El servicio de urgencias del *Hospital Universitario San Rafael* necesita:

1. Registrar pacientes y encontrar su historia rápidamente por número de documento.
2. Clasificar la gravedad de cada paciente (triage) con un protocolo estandarizado.
3. Atender siempre primero al paciente más grave; si dos tienen la misma gravedad, al que llegó antes.
4. Saber qué camas están libres u ocupadas en cada piso y área, y asignarlas según la gravedad.

Cada una de estas necesidades se resuelve con un tipo de árbol distinto.

## ¿Por qué cada árbol?

| # | Estructura | Archivo | Problema que resuelve |
|---|-----------|---------|-----------------------|
| 1 | **Árbol AVL** de pacientes por documento (cédula) | `structures/patient_registry.py` | Registro e historia de pacientes con búsqueda O(log n), balanceado aunque las cédulas lleguen ordenadas. |
| 2 | **Árbol binario de búsqueda de prioridad** (cola de triage) | `structures/triage_queue.py` | Atender siempre al paciente más grave primero; en empate, al que llegó antes. Clave compuesta `(nivel, número de llegada)`. |
| 3 | **Árbol de decisión binario** (sí/no) | `structures/triage_decision.py` | Clasificar la gravedad del paciente con preguntas guiadas (Triage Manchester / Resolución 5596 de 2015). |
| 4 | **Árbol n-ario** (primer hijo / siguiente hermano) | `structures/hospital_map.py` | Infraestructura Hospital → Pisos → Áreas → Camas, con la ocupación sumada recursivamente hacia arriba. |

### Niveles de triage (Resolución 5596 de 2015)

| Nivel | Color | Categoría | Tiempo máximo |
|-------|-------|-----------|---------------|
| 1 | Rojo | Resucitación | Inmediato |
| 2 | Naranja | Emergencia | ≤ 30 min |
| 3 | Amarillo | Urgencia | ≤ 2 h |
| 4 | Verde | Menos urgente | ≤ 4 h |
| 5 | Azul | No urgente | ≤ 8 h |

## Conceptos de árboles aplicados

La página **Estructuras** dibuja en SVG los cuatro árboles y calcula, para cada uno:

- **Raíz**: nodo sin padre (amarillo en los diagramas).
- **Rama**: nodo interno, con padre y con hijos (azul claro).
- **Hoja**: nodo sin hijos (verde).
- **Altura**: número de niveles del árbol.
- **Nivel**: distancia de un nodo a la raíz (la raíz está en el nivel 0).
- **Peso**: número total de nodos.
- **Grado**: número de hijos de un nodo; se muestra el grado máximo.
- **Orden**: número máximo de hijos permitido (2 en los árboles binarios; en el n-ario, el grado máximo).

Además, el AVL muestra el contador de **rotaciones** realizadas para mantenerse balanceado.

## Complejidades

| Operación | Estructura | Complejidad |
|-----------|-----------|-------------|
| Insertar / buscar paciente | AVL | O(log n) |
| Listar pacientes ordenados (inorden) | AVL | O(n) |
| Encolar paciente | BST de prioridad | O(h) — O(log n) promedio |
| Consultar / atender al más urgente | BST de prioridad | O(h) — nodo más a la izquierda |
| Clasificar un paciente | Árbol de decisión | O(h) — una pregunta por nivel |
| Buscar área / cama | Árbol n-ario | O(n) |
| Contar camas y ocupación | Árbol n-ario | O(n) recursivo |

## Restricción: sin listas de Python

El proyecto **no usa listas de Python** (`[]`, `list()`, `.append()`, comprensiones de listas). Todas las colecciones viven en los árboles hechos a mano y los recorridos se hacen con **generadores (`yield`)**, por ejemplo:

```python
def in_order_asc(self, current_node):
    if current_node is not None:
        yield from self.in_order_asc(current_node.left)
        yield current_node
        yield from self.in_order_asc(current_node.right)
```

El camino recorrido en el triage se guarda como una cadena enlazada de nodos (`TriageStep`).

## Funcionalidades

- **Panel general**: indicadores (en espera, en atención, camas libres/ocupadas, pacientes registrados), conteo por color de triage, próximo paciente y ocupación por área.
- **Admisión**: registro o actualización del paciente en el AVL.
- **Triage guiado**: una pregunta por pantalla con botones Sí / No y el camino resaltado sobre el árbol de decisión.
- **Cola de atención**: tablero tipo sala de espera con tiempo de espera y tiempo máximo según el nivel; botón *Atender siguiente* que asigna cama automáticamente.
- **Pacientes**: listado ordenado por documento, búsqueda por cédula, ficha y alta (libera la cama).
- **Mapa de camas**: pisos y áreas desplegables con ocupación agregada por nivel.
- **Estructuras**: los cuatro árboles dibujados en SVG con sus propiedades.

### Reglas de asignación de cama

| Paciente | Áreas (en orden de preferencia) |
|----------|---------------------------------|
| Menor de 14 años | Pediatría (nivel 1: también Reanimación o UCI) |
| Nivel 1 | Reanimación, UCI |
| Nivel 2 | Urgencias Adultos, UCI |
| Nivel 3 | Observación, Urgencias Adultos |
| Niveles 4 y 5 | Urgencias Adultos |

## Estructura del proyecto

```
TallerArbolesEstructuras/
├── app.py                      # Rutas Flask
├── models/
│   ├── patient.py              # Clase Patient y pasos del triage
│   └── triage_level.py         # Niveles de triage Manchester
├── structures/
│   ├── patient_registry.py     # Árbol AVL
│   ├── triage_queue.py         # BST de prioridad
│   ├── triage_decision.py      # Árbol de decisión binario
│   └── hospital_map.py         # Árbol n-ario
├── services/
│   ├── hospital_service.py     # Orquesta los cuatro árboles
│   └── tree_layout.py          # Coordenadas SVG de los árboles
├── seed.py                     # Datos iniciales
├── templates/                  # Plantillas Jinja (HTML)
├── static/
│   ├── css/styles.css
│   └── js/app.js               # Reloj en vivo y menú
├── requirements.txt
└── README.md
```

## Ejecución

```
pip install -r requirements.txt
python app.py
# abrir http://127.0.0.1:5000
```

Los datos se cargan en memoria al iniciar (`seed.py`) con pacientes de ejemplo en espera, en atención y dados de alta.
