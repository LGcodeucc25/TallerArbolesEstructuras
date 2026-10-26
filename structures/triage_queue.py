"""Priority BST used as the triage waiting queue."""


class QueueNode:
    """Queue node keyed by (triage_level, arrival_number)."""

    def __init__(self, patient, level):
        self.triage_level = level
        self.arrival_number = patient.arrival_number
        self.patient = patient
        self.left = None
        self.right = None


class TriageQueue:
    """Leftmost node = most urgent patient; ties go to who arrived first."""

    def __init__(self):
        self.root = None

    def is_before(self, a, b):
        """True if node a must be attended before node b."""
        if a.triage_level != b.triage_level:
            return a.triage_level < b.triage_level
        return a.arrival_number < b.arrival_number

    def add(self, patient, level):
        new_node = QueueNode(patient, level)
        if self.root is None:
            self.root = new_node
        else:
            self.add_recursive(new_node, self.root)

    def add_recursive(self, new_node, current_node):
        if self.is_before(new_node, current_node):
            if current_node.left is None:
                current_node.left = new_node
            else:
                self.add_recursive(new_node, current_node.left)
        else:
            if current_node.right is None:
                current_node.right = new_node
            else:
                self.add_recursive(new_node, current_node.right)

    def peek_next(self):
        """Most urgent node (leftmost) without removing it."""
        current_node = self.root
        if current_node is None:
            return None
        while current_node.left is not None:
            current_node = current_node.left
        return current_node

    def pop_next(self):
        """Remove and return the most urgent node."""
        if self.root is None:
            return None
        parent = None
        current_node = self.root
        while current_node.left is not None:
            parent = current_node
            current_node = current_node.left
        if parent is None:
            self.root = current_node.right
        else:
            parent.left = current_node.right
        current_node.right = None
        return current_node

    def in_order_asc(self, current_node):
        if current_node is not None:
            yield from self.in_order_asc(current_node.left)
            yield current_node
            yield from self.in_order_asc(current_node.right)

    def attention_order(self):
        """Yield queued nodes in the order they will be attended."""
        yield from self.in_order_asc(self.root)

    def size(self, current_node):
        if current_node is None:
            return 0
        return 1 + self.size(current_node.left) + self.size(current_node.right)

    def get_height(self, current_node):
        if current_node is None:
            return 0
        return 1 + max(self.get_height(current_node.left), self.get_height(current_node.right))

    def count_leaves(self, current_node):
        if current_node is None:
            return 0
        if current_node.left is None and current_node.right is None:
            return 1
        return self.count_leaves(current_node.left) + self.count_leaves(current_node.right)
