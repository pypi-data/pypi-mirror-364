from manim import *
from ..core import FlowGroup


class FlowArray(FlowGroup):
    def __init__(self, elements: list, direction=RIGHT, extend_scope=1):
        """
        Initializes the FlowArray with virtual edge nodes and animatable content.
        """
        super().__init__()
        self.extend_scope = extend_scope
        self.direction = direction
        self.elements = elements
        self.squares, self.labels = [], []
        self._initialize_array_mobjects()

    def _add_element(self, label_val, is_edge_node=False):
        """
        Creates a visual box + label for a given value and adds it to the group.
        If marked as an edge node, it is made invisible.
        """
        square = Square(side_length=1)
        label = Tex(str(label_val)).move_to(square.get_center())

        self.squares.append(square)
        self.labels.append(label)

        group = VGroup(square, label)
        if is_edge_node:
            group.set_opacity(0)

        self.add(group)

    def _initialize_array_mobjects(self):
        """
        Constructs the full visual array with edge nodes and arranges them.
        """
        self.logger.log(f"Direction: {self.direction}")

        for _ in range(self.extend_scope):
            self._add_element(-1, True)  # Left edge

        for i, elem in enumerate(self.elements):
            self.logger.log(f"Inserting: arr[{i}] = {elem}")
            self._add_element(elem)

        for _ in range(self.extend_scope):
            self._add_element(-1, True)  # Right edge

        self.arrange(self.direction, buff=0.1)
        self.move_to(ORIGIN)

    def update_position(self, index, new_value) -> AnimationGroup:
        """
        Replaces the label at `index` with a new value using a Transform animation.
        """
        if not (0 <= index < len(self.elements)):
            raise IndexError("Index out of range for update()")
        self.logger.log(f"Updating: arr[{index}] = {new_value}")

        old_label = self.labels[index + self.extend_scope]
        new_label = Tex(str(new_value)).move_to(old_label.get_center())

        # Update internal state
        self.labels[index + self.extend_scope] = new_label
        self.elements[index] = new_value

        return AnimationGroup(Transform(old_label, new_label))

    def swap(self, i: int, j: int) -> AnimationGroup:
        """
        Swaps two values and their labels using arc-based motion.
        """
        self.logger.log(f"Swapping: arr[{i}] <-> arr[{j}]")

        i += self.extend_scope
        j += self.extend_scope

        label_i, label_j = self.labels[i], self.labels[j]
        pos_i, pos_j = self.squares[i].get_center(), self.squares[j].get_center()

        # Animate labels along arc paths
        anim_i = MoveAlongPath(label_i, ArcBetweenPoints(pos_i, pos_j, angle=-PI / 2))
        anim_j = MoveAlongPath(label_j, ArcBetweenPoints(pos_j, pos_i, angle=-PI / 2))

        self.labels[i], self.labels[j] = label_j, label_i

        i -= self.extend_scope
        j -= self.extend_scope

        # Swap internal state
        self.elements[i], self.elements[j] = (self.elements[j], self.elements[i])

        return AnimationGroup(anim_i, anim_j)

    def at(self, index):
        """
        Enables array-style access to logical values.
        """
        if not (0 <= index < len(self.elements)):
            raise IndexError("Index out of range for update()")
        return self.elements[index]

    # Python Protocol Methods

    def __len__(self):
        """
        Returns logical length (excluding virtual nodes).
        """
        return len(self.elements)

    def __iter__(self):
        """
        Allows iteration over real visual array (excludes virtual edges).
        """
        return iter(self.submobjects[self.extend_scope : -self.extend_scope])

    def __getitem__(self, index: int):
        """
        Enables array-style access to logical values.
        """
        return self.squares[index + self.extend_scope]
