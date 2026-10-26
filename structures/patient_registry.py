"""AVL tree of patients indexed by document id."""


class PatientNode:
    """AVL node holding one patient."""

    def __init__(self, patient):
        self.document_id = patient.document_id
        self.patient = patient
        self.left = None
        self.right = None
        self.height = 1


class PatientRegistry:
    """Self-balancing BST: O(log n) search even with sorted document ids."""

    def __init__(self):
        self.root = None
        self.rotations_count = 0

    def add(self, patient):
        new_node = PatientNode(patient)
        if self.root is None:
            self.root = new_node
        else:
            self.root = self.add_recursive(new_node, self.root)

    def add_recursive(self, new_node, current_node):
        """Insert and rebalance on the way back; returns the subtree root."""
        if current_node is None:
            return new_node
        key = int(new_node.document_id)
        current_key = int(current_node.document_id)
        if key < current_key:
            current_node.left = self.add_recursive(new_node, current_node.left)
        elif key > current_key:
            current_node.right = self.add_recursive(new_node, current_node.right)
        else:
            # Same document: update the stored data, like the class phone book
            current_node.patient = new_node.patient
            return current_node

        self.update_height(current_node)
        balance = self.balance_factor(current_node)

        if balance > 1 and key < int(current_node.left.document_id):
            return self.rotate_right(current_node)
        if balance < -1 and key > int(current_node.right.document_id):
            return self.rotate_left(current_node)
        if balance > 1 and key > int(current_node.left.document_id):
            current_node.left = self.rotate_left(current_node.left)
            return self.rotate_right(current_node)
        if balance < -1 and key < int(current_node.right.document_id):
            current_node.right = self.rotate_right(current_node.right)
            return self.rotate_left(current_node)
        return current_node

    def node_height(self, node):
        if node is None:
            return 0
        return node.height

    def update_height(self, node):
        node.height = 1 + max(self.node_height(node.left), self.node_height(node.right))

    def balance_factor(self, node):
        if node is None:
            return 0
        return self.node_height(node.left) - self.node_height(node.right)

    def rotate_right(self, node):
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        self.update_height(node)
        self.update_height(pivot)
        self.rotations_count += 1
        return pivot

    def rotate_left(self, node):
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        self.update_height(node)
        self.update_height(pivot)
        self.rotations_count += 1
        return pivot

    def search(self, document_id):
        """Iterative search; returns the patient or None."""
        if not str(document_id).isdigit():
            return None
        key = int(document_id)
        current_node = self.root
        while current_node is not None:
            current_key = int(current_node.document_id)
            if key == current_key:
                return current_node.patient
            if key < current_key:
                current_node = current_node.left
            else:
                current_node = current_node.right
        return None

    def in_order_asc(self, current_node):
        if current_node is not None:
            yield from self.in_order_asc(current_node.left)
            yield current_node
            yield from self.in_order_asc(current_node.right)

    def patients(self):
        """Yield patients sorted by document id."""
        for node in self.in_order_asc(self.root):
            yield node.patient

    def count_nodes(self, current_node):
        if current_node is None:
            return 0
        return 1 + self.count_nodes(current_node.left) + self.count_nodes(current_node.right)

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
