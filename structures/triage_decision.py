"""Binary yes/no decision tree for Manchester triage classification."""


class DecisionNode:
    """Inner nodes hold a question; leaves hold a triage level."""

    def __init__(self, node_id, question=None, result_level=None):
        self.node_id = node_id
        self.question = question
        self.result_level = result_level
        self.yes = None
        self.no = None

    def is_leaf(self):
        return self.result_level is not None


class TriageDecisionTree:
    """Guided triage: each answer moves to the yes or no child."""

    def __init__(self):
        self.root = None
        self.build()

    def add(self, new_node, parent_id=None, answer=None):
        """Attach new_node as the yes/no child of parent_id (root if None)."""
        if self.root is None:
            self.root = new_node
            return
        parent = self.find_node(parent_id)
        if parent is None:
            return
        if answer == "yes":
            parent.yes = new_node
        else:
            parent.no = new_node

    def build(self):
        """Questions based on the Manchester system / Res. 5596 of 2015."""
        self.add(DecisionNode("P1", "¿El paciente está en paro respiratorio, no respira o está inconsciente?"))
        self.add(DecisionNode("N1-A", result_level=1), "P1", "yes")
        self.add(DecisionNode("P2", "¿Presenta dolor torácico intenso, dificultad respiratoria grave o sangrado abundante?"), "P1", "no")

        self.add(DecisionNode("P2.1", "¿Tiene signos de shock: piel pálida y fría, pulso débil o confusión?"), "P2", "yes")
        self.add(DecisionNode("N1-B", result_level=1), "P2.1", "yes")
        self.add(DecisionNode("N2-A", result_level=2), "P2.1", "no")

        self.add(DecisionNode("P3", "¿Tiene fiebre mayor a 39 °C o dolor intenso (8 a 10 sobre 10)?"), "P2", "no")
        self.add(DecisionNode("P3.1", "¿Presenta convulsiones, rigidez de nuca o es un bebé menor de 3 meses?"), "P3", "yes")
        self.add(DecisionNode("N2-B", result_level=2), "P3.1", "yes")
        self.add(DecisionNode("N3", result_level=3), "P3.1", "no")

        self.add(DecisionNode("P4", "¿Tiene síntomas de más de 3 días con dolor moderado?"), "P3", "no")
        self.add(DecisionNode("N4-A", result_level=4), "P4", "yes")
        self.add(DecisionNode("P5", "¿Presenta una lesión o síntoma agudo leve (herida pequeña, esguince, vómito)?"), "P4", "no")
        self.add(DecisionNode("N4-B", result_level=4), "P5", "yes")
        self.add(DecisionNode("N5", result_level=5), "P5", "no")

    def get_root(self):
        return self.root

    def find_node(self, node_id, current_node=None, start=True):
        """Recursive pre-order search by node id."""
        if start:
            current_node = self.root
        if current_node is None:
            return None
        if current_node.node_id == node_id:
            return current_node
        found = self.find_node(node_id, current_node.yes, False)
        if found is not None:
            return found
        return self.find_node(node_id, current_node.no, False)

    def depth_of(self, node_id, current_node=None, depth=0, start=True):
        """Level of a node (root = 0), or -1 if missing."""
        if start:
            current_node = self.root
        if current_node is None:
            return -1
        if current_node.node_id == node_id:
            return depth
        found = self.depth_of(node_id, current_node.yes, depth + 1, False)
        if found >= 0:
            return found
        return self.depth_of(node_id, current_node.no, depth + 1, False)

    def pre_order(self, current_node):
        if current_node is not None:
            yield current_node
            yield from self.pre_order(current_node.yes)
            yield from self.pre_order(current_node.no)

    def count_nodes(self, current_node):
        if current_node is None:
            return 0
        return 1 + self.count_nodes(current_node.yes) + self.count_nodes(current_node.no)

    def get_height(self, current_node):
        if current_node is None:
            return 0
        return 1 + max(self.get_height(current_node.yes), self.get_height(current_node.no))

    def count_leaves(self, current_node):
        if current_node is None:
            return 0
        if current_node.is_leaf():
            return 1
        return self.count_leaves(current_node.yes) + self.count_leaves(current_node.no)
