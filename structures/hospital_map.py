"""N-ary tree (first child / next sibling) of the hospital infrastructure."""


class FacilityNode:
    """Hospital, floor, area or bed."""

    def __init__(self, name, kind, code):
        self.name = name
        self.kind = kind
        self.code = code
        self.first_child = None
        self.next_sibling = None
        self.parent = None
        self.patient = None


class HospitalMap:
    """Hospital -> Floors -> Areas -> Beds, with occupancy summed upwards."""

    def __init__(self):
        self.root = None

    def add(self, node):
        """Set the root (the hospital)."""
        if self.root is None:
            self.root = node

    def add_child(self, parent_name, node):
        parent = self.find(parent_name)
        if parent is None:
            return False
        node.parent = parent
        if parent.first_child is None:
            parent.first_child = node
        else:
            current = parent.first_child
            while current.next_sibling is not None:
                current = current.next_sibling
            current.next_sibling = node
        return True

    def find(self, name, current_node=None, start=True):
        """Recursive search by name."""
        if start:
            current_node = self.root
        if current_node is None:
            return None
        if current_node.name == name:
            return current_node
        child = current_node.first_child
        while child is not None:
            found = self.find(name, child, False)
            if found is not None:
                return found
            child = child.next_sibling
        return None

    def children(self, node):
        current = node.first_child
        while current is not None:
            yield current
            current = current.next_sibling

    def pre_order(self, current_node):
        if current_node is not None:
            yield current_node
            for child in self.children(current_node):
                yield from self.pre_order(child)

    def nodes_of_kind(self, kind):
        for node in self.pre_order(self.root):
            if node.kind == kind:
                yield node

    def count_beds(self, node):
        if node.kind == "bed":
            return 1
        total = 0
        for child in self.children(node):
            total += self.count_beds(child)
        return total

    def count_occupied(self, node):
        if node.kind == "bed":
            if node.patient is None:
                return 0
            return 1
        total = 0
        for child in self.children(node):
            total += self.count_occupied(child)
        return total

    def occupancy_percent(self, node):
        beds = self.count_beds(node)
        if beds == 0:
            return 0
        return round(self.count_occupied(node) * 100 / beds)

    def find_free_bed(self, area_name):
        area = self.find(area_name)
        if area is None:
            return None
        for bed in self.children(area):
            if bed.kind == "bed" and bed.patient is None:
                return bed
        return None

    def assign_bed(self, bed_name, patient):
        bed = self.find(bed_name)
        if bed is None or bed.kind != "bed" or bed.patient is not None:
            return False
        bed.patient = patient
        return True

    def release_bed(self, bed_name):
        bed = self.find(bed_name)
        if bed is None or bed.patient is None:
            return None
        patient = bed.patient
        bed.patient = None
        return patient

    def get_height(self, current_node):
        if current_node is None:
            return 0
        tallest = 0
        for child in self.children(current_node):
            tallest = max(tallest, self.get_height(child))
        return 1 + tallest

    def get_weight(self, current_node):
        if current_node is None:
            return 0
        total = 1
        for child in self.children(current_node):
            total += self.get_weight(child)
        return total

    def count_leaves(self, current_node):
        if current_node is None:
            return 0
        if current_node.first_child is None:
            return 1
        total = 0
        for child in self.children(current_node):
            total += self.count_leaves(child)
        return total

    def degree(self, node):
        total = 0
        for _ in self.children(node):
            total += 1
        return total

    def max_degree(self, current_node):
        if current_node is None:
            return 0
        best = self.degree(current_node)
        for child in self.children(current_node):
            best = max(best, self.max_degree(child))
        return best

    def level_of(self, node):
        level = 0
        while node.parent is not None:
            level += 1
            node = node.parent
        return level

    def path_to_root(self, node):
        """Yield nodes from the given one up to the hospital."""
        while node is not None:
            yield node
            node = node.parent

    def path_text(self, node):
        """Hospital > Floor > Area > Bed."""
        text = ""
        for step in self.path_to_root(node):
            if text == "":
                text = step.name
            else:
                text = step.name + " › " + text
        return text
