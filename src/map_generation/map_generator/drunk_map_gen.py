from src.map_generation.map_generator.map_generator_ import MapGenerator
from src.map_generation.cellulose import drunk_walk


class DrunkMapGenerator(MapGenerator):
    """Generates a map based on drunk artist rooms--independent passability brushes which wander their field space."""
    def __init__(self,
                 grid_width: int,
                 grid_height: int):
        candidates = [drunk_walk.SmallDrunkRoom,
                      drunk_walk.MediumDrunkRoom,
                      drunk_walk.LargeDrunkRoom]
        weights = [.15, .45, .4]  # Small rooms should be less likely if others can fit in the same grid space.
        super().__init__(grid_width=grid_width,
                         grid_height=grid_height,
                         candidates=candidates,
                         candidate_weights=weights)


if __name__ == "__main__":
    import multiprocessing as mp
    mp.freeze_support()

    mapgen = DrunkMapGenerator(grid_width=7,
                               grid_height=5)

    walls, passability = mapgen._render()
    for row in walls:
        char_row = ["#" if truth else " "
                    for truth in row]
        print("".join(char_row))