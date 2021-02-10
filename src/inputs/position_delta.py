class PositionDelta:
    """Represents a change in position that an entity wants to make."""
    def __init__(self,
                 dx: int,
                 dy: int,
                 no_clip: bool = False):
        """
        :arg dx Desired in x position
        :arg dy Desired in y position
        :arg no_clip Whether this move respects whether or not the target tile can be moved through."""
        self.dx = dx
        self.dy = dy
        self.no_clip = no_clip