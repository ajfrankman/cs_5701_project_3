from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from tile import Tile
import random
import seaborn as sns
from pathlib import Path


class Map:
    def __init__(self, terrain_list: list, compatible_dict: dict, terrain_weights: dict = None):
        self.tile_list = []
        self.terrain_list = terrain_list
        # adjacency/compatibility dict mapping terrain types to compatible terrains
        self.compatible_dict = compatible_dict
        self.grid_height = 50
        self.grid_width = 50

        # If anyone would like to expand the tiel types, add them here.
        self.terrain_colors = ["dodgerblue", "lightblue", "khaki", "darkgreen", "yellowgreen", "saddlebrown", "black"]
        self.terrain_color_map = {'W': 0, 'B': 1, 'L': 2, 'F': 3, 'H': 4, 'M': 5}
        self.symbol_terrain_label = {'W': 'Water', 'B': 'Beach', 'L': 'Lowland', 'F': 'Forest', 'H': 'Hill', 'M': 'Mountain'}
        if terrain_weights:
            self.terrain_weights = terrain_weights
        else:
            self.terrain_weights = [100/len(self.terrain_list) for _ in self.terrain_list]


    def __repr__(self):
        return self.symbol
    
    def __str__(self):
        self_str = f'''
        tile_list: {self.tile_list}
        terrain_list: {self.terrain_list}
        compatible_dict: {self.compatible_dict}
        '''
        return self_str

    def print_map(self):
        # Make an empty grid
        grid = [[' ' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        # Fill the grid with terrain symbols using tile_list
        for tile in self.tile_list:
            row, col = tile.coordinate
            grid[row][col] = tile.terrain_type[0].upper()  # Use the first letter of the terrain type as a symbol
        # Convert the grid to a string for printing
        grid_str = '\n'.join([' '.join(row) for row in grid])  
        print(grid_str + '\n\n')
    
    def get_plt(self):
        # Make an empty grid
        grid = [[' ' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        # Fill the grid with terrain numbers for coloring.
        for tile in self.tile_list:
            row, col = tile.coordinate
            grid[row][col] = self.terrain_color_map.get(tile.terrain_type[0].upper(), '-1')

        # 3. Plot the colored tiles (no letters, no axis ticks, square tiles)
        fig, ax = plt.subplots()
        sns.heatmap(grid, cmap=self.terrain_colors, cbar=False, square=True, vmin=0, vmax=len(self.terrain_colors)-1,
                    xticklabels=False, yticklabels=False, ax=ax)

        # 4. Add the legend
        patches = [mpatches.Patch(color=self.terrain_colors[i], label=self.symbol_terrain_label.get(self.terrain_list[i], self.terrain_list[i])) for i in range(len(self.terrain_list))]
        ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

        # Save or show
        plt.tight_layout()
        return plt

    def show_map(self):
        plt = self.get_plt()          
        plt.show()
        plt.close('all')
    
    def save_map(self, file_path: str):
        plt = self.get_plt()
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(file_path, bbox_inches='tight')
        plt.close('all')

    def get_compatible_terrain(self, terrain_type: str):
        terrain_type = terrain_type.upper()
        ret_val = self.compatible_dict[terrain_type] if terrain_type in self.terrain_list else []
        return ret_val
    
    def is_compatible_terrain(self, terrain_one: str, terrain_two: str):
        '''Because our locations are bidrectional, our compatible check is pretty easy'''
        return terrain_two in self.get_compatible_terrain(terrain_one)
    
    def _get_neighbor_coor(self, coordinate: tuple, diagonal: bool = True):
        row, col = coordinate
        neighbor_unit_vectors = [(1,0), (0,1), (-1,0), (0,-1)]
        diag_unit_vectors = [(1,1), (-1,1), (-1,-1), (1,-1)]
        if diagonal:
            neighbor_unit_vectors += diag_unit_vectors
        neighbor_coordinates = [(coordinate[0]+dx, coordinate[1]+dy)
            for dx,dy in neighbor_unit_vectors
            if 0 <= coordinate[0]+dx < self.grid_width 
            and 0 <= coordinate[1]+dy < self.grid_height
        ]
        return neighbor_coordinates

    def _create_tile_list(self, terrain_grid: list):
        for row in terrain_grid:
            for tile in row:
                for neighbor_coor in tile.neighbor_coordinates:
                    tile.neighbor_tiles.append(terrain_grid[neighbor_coor[0]][neighbor_coor[1]])
                self.tile_list.append(tile)

    def import_terrain_from_file(self, file_path: str):
        with open(file_path, 'r') as f:
            terrain_grid = []
            # First line in file is the grid height and width, so we can set those values
            first_line = f.readline().split(' ')
            self.grid_height = int(first_line[0])
            self.grid_width = int(first_line[1])
            for line in f:
                row = []
                for terrain_type in line.strip().split(' '):
                    coordinate = (len(terrain_grid), len(row))
                    new_tile = Tile(terrain_type, coordinate)
                    neighbor_coordinates = self._get_neighbor_coor(coordinate)
                    new_tile.neighbor_coordinates = neighbor_coordinates
                    row.append(new_tile)
                terrain_grid.append(row)  
        # Now that the terrain is populated, make neighbor references
        self._create_tile_list(terrain_grid)

    def generate_random_terrain(self, grid_height: int = 0, grid_width: int = 0, diagonal: bool = True):
        self.grid_height = grid_height if grid_height > 0 else self.grid_height
        self.grid_width = grid_width if grid_width > 0 else self.grid_width

        # Create a 2d array with terrain values
        terrain_grid = []
        for i in range(self.grid_height):
            row = []
            for j in range(self.grid_width):
                terrain_type = random.choices(self.terrain_list, weights=self.terrain_weights, k=1)[0]
                coordinate = (i,j)
                new_tile = Tile(terrain_type, coordinate)
                neighbor_coordinates = self._get_neighbor_coor(coordinate, diagonal)
                new_tile.neighbor_coordinates = neighbor_coordinates
                row.append(new_tile)
            terrain_grid.append(row)
        
        # Now that the terrain is populated, make neighbor references
        self._create_tile_list(terrain_grid)

    def run_min_conflict(self, tile: Tile):
        '''
        Returns Values:
            False if tile is not compatible with all neighbors,
            True if tile is compatible with all neighbors

        '''
        max_terrains = [tile.terrain_type]
        max_compatible_neighbors = sum(self.is_compatible_terrain(tile.terrain_type, neighbor.terrain_type) for neighbor in tile.neighbor_tiles)
        #Checks if the tile is already compatible with all of its neighbors, if so, we can skip it
        if max_compatible_neighbors == len(tile.neighbor_tiles):
            return True
        
        other_terrain = [terrain for terrain in self.terrain_list if terrain != tile.terrain_type]
        # Check which terrain is compatible with the most neighbors, and assign that terrain to the tile
        for terrain in other_terrain:
            compatible_neighbors = sum(self.is_compatible_terrain(terrain, neighbor.terrain_type) for neighbor in tile.neighbor_tiles)
            if compatible_neighbors > max_compatible_neighbors:
                max_terrains = [terrain]
                max_compatible_neighbors = compatible_neighbors
            elif compatible_neighbors == max_compatible_neighbors:
                max_terrains.append(terrain)
        tile.terrain_type = random.choice(max_terrains)
        return False

    def constrain(self, max_loop: int = 100, debug: bool = False):
        loops = 0
        map_constrained = False
        while not map_constrained and loops < max_loop:
            map_constrained = all([self.run_min_conflict(tile) for tile in self.tile_list])
            loops += 1
            if debug:
                self.print_map()
        return map_constrained, loops