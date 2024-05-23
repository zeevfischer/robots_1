class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def create_from_point(self, other_point):
        new_x = other_point.x
        new_y = other_point.y
        return Point(new_x, new_y)

    def __str__(self):
        return f"({self.x}, {self.y})"