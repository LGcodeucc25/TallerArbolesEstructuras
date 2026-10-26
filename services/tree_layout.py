"""Computes SVG coordinates of the trees recursively, using generators."""

from models.triage_level import level_info

NODE_HEIGHT = 44
LEVEL_GAP = 92
GAP_X = 16
PADDING = 24


class LayoutNode:
    """Drawable copy of a tree node (binary or first child / next sibling)."""

    def __init__(self, label, sublabel="", title="", accent=None):
        self.label = label
        self.sublabel = sublabel
        self.title = title
        self.accent = accent
        self.left = None
        self.right = None
        self.first_child = None
        self.next_sibling = None
        self.parent = None
        self.edge_label = ""
        self.highlight = False
        self.kind = "leaf"
        self.depth = 0
        self.x = 0
        self.y = 0

    def children(self):
        if self.left is not None:
            yield self.left
        if self.right is not None:
            yield self.right
        current = self.first_child
        while current is not None:
            yield current
            current = current.next_sibling

    def degree(self):
        total = 0
        for _ in self.children():
            total += 1
        return total

    def kind_label(self):
        if self.kind == "root":
            return "Raíz"
        if self.kind == "branch":
            return "Rama"
        return "Hoja"


class TreeDrawing:
    """Positions plus the tree concepts seen in class (height, weight...)."""

    def __init__(self, key, title, root, binary, node_width, order):
        self.key = key
        self.title = title
        self.root = root
        self.binary = binary
        self.node_width = node_width
        self.node_height = NODE_HEIGHT
        self.order = order
        self.slots = 0
        self.max_depth = 0
        if root is not None:
            self.assign_depth(root, 0)
            if binary:
                self.assign_in_order(root)
            else:
                self.assign_slots(root)
            self.assign_kinds(root)
        columns = max(self.slots, 1)
        self.width = PADDING * 2 + columns * (node_width + GAP_X) - GAP_X
        self.height = PADDING * 2 + self.max_depth * LEVEL_GAP + NODE_HEIGHT + 16

    def slot_x(self, slot):
        return PADDING + slot * (self.node_width + GAP_X) + self.node_width / 2

    def assign_depth(self, node, depth):
        node.depth = depth
        node.y = PADDING + depth * LEVEL_GAP + NODE_HEIGHT / 2
        self.max_depth = max(self.max_depth, depth)
        for child in node.children():
            self.assign_depth(child, depth + 1)

    def assign_in_order(self, node):
        """Binary trees: x follows the in-order position."""
        if node is None:
            return
        self.assign_in_order(node.left)
        node.x = self.slot_x(self.slots)
        self.slots += 1
        self.assign_in_order(node.right)

    def assign_slots(self, node):
        """N-ary trees: leaves take consecutive slots, parents get centered."""
        first_x = None
        last_x = None
        for child in node.children():
            self.assign_slots(child)
            if first_x is None:
                first_x = child.x
            last_x = child.x
        if first_x is None:
            node.x = self.slot_x(self.slots)
            self.slots += 1
        else:
            node.x = (first_x + last_x) / 2

    def assign_kinds(self, node):
        if node.parent is None:
            node.kind = "root"
        elif node.degree() > 0:
            node.kind = "branch"
        else:
            node.kind = "leaf"
        for child in node.children():
            self.assign_kinds(child)

    def pre_order(self, node):
        if node is not None:
            yield node
            for child in node.children():
                yield from self.pre_order(child)

    def nodes(self):
        yield from self.pre_order(self.root)

    def edges(self):
        """Yield every node that has a parent (one edge each)."""
        for node in self.nodes():
            if node.parent is not None:
                yield node

    def weight(self):
        total = 0
        for _ in self.nodes():
            total += 1
        return total

    def tree_height(self):
        if self.root is None:
            return 0
        return self.max_depth + 1

    def leaves(self):
        total = 0
        for node in self.nodes():
            if node.degree() == 0:
                total += 1
        return total

    def branches(self):
        total = 0
        for node in self.nodes():
            if node.kind == "branch":
                total += 1
        return total

    def max_degree(self):
        best = 0
        for node in self.nodes():
            best = max(best, node.degree())
        return best

    def root_label(self):
        if self.root is None:
            return "—"
        return self.root.label


def from_binary(source, left_name, right_name, describe, left_edge="", right_edge=""):
    """Recursively copy a binary tree into LayoutNodes."""
    if source is None:
        return None
    layout = describe(source)
    layout.left = from_binary(getattr(source, left_name), left_name, right_name, describe, left_edge, right_edge)
    layout.right = from_binary(getattr(source, right_name), left_name, right_name, describe, left_edge, right_edge)
    if layout.left is not None:
        layout.left.parent = layout
        layout.left.edge_label = left_edge
    if layout.right is not None:
        layout.right.parent = layout
        layout.right.edge_label = right_edge
    return layout


def from_nary(source, describe):
    """Recursively copy a first child / next sibling tree into LayoutNodes."""
    if source is None:
        return None
    layout = describe(source)
    previous = None
    child = source.first_child
    while child is not None:
        child_layout = from_nary(child, describe)
        child_layout.parent = layout
        if previous is None:
            layout.first_child = child_layout
        else:
            previous.next_sibling = child_layout
        previous = child_layout
        child = child.next_sibling
    return layout


def describe_patient_node(node):
    patient = node.patient
    title = patient.full_name + " · altura " + str(node.height)
    return LayoutNode(node.document_id, patient.short_name(), title)


def describe_queue_node(node):
    info = level_info(node.triage_level)
    label = "N" + str(node.triage_level) + " · #" + str(node.arrival_number)
    title = node.patient.full_name + " · " + info.name + " (" + info.label + ")"
    return LayoutNode(label, node.patient.short_name(), title, info.color)


def avl_drawing(registry):
    root = from_binary(registry.root, "left", "right", describe_patient_node)
    return TreeDrawing("avl", "Registro de pacientes (AVL)", root, True, 104, 2)


def queue_drawing(queue):
    root = from_binary(queue.root, "left", "right", describe_queue_node)
    return TreeDrawing("queue", "Cola de prioridad (BST)", root, True, 100, 2)


def decision_drawing(tree, patient=None):
    def describe(node):
        if node.is_leaf():
            info = level_info(node.result_level)
            layout = LayoutNode(node.node_id, "Nivel " + str(node.result_level), info.name + " · " + info.label, info.color)
        else:
            layout = LayoutNode(node.node_id, "Pregunta", node.question)
        if patient is not None and patient.path_contains(node.node_id):
            layout.highlight = True
        return layout

    root = from_binary(tree.root, "yes", "no", describe, "Sí", "No")
    return TreeDrawing("decision", "Árbol de decisión de triage", root, True, 74, 2)


def hospital_drawing(hospital):
    def describe(node):
        if node.kind == "bed":
            if node.patient is None:
                return LayoutNode(node.code, "Libre", node.name + " · libre")
            return LayoutNode(node.code, node.patient.initials(), node.name + " · " + node.patient.full_name, "#dc2626")
        occupancy = str(hospital.count_occupied(node)) + "/" + str(hospital.count_beds(node))
        return LayoutNode(node.code, occupancy, node.name)

    root = from_nary(hospital.root, describe)
    drawing = TreeDrawing("hospital", "Infraestructura del hospital (n-ario)", root, False, 58, 0)
    drawing.order = drawing.max_degree()
    return drawing
