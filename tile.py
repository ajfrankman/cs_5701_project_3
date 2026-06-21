class Tile:
    def __init__(self, terrain_type: str, coordinate: tuple):
        self.terrain_type = terrain_type
        self.coordinate = coordinate
        self.neighbor_coordinates = []
        self.neighbor_tiles = []

    
    def __str__(self):
        self_str = f'''
        coordinate: {self.coordinate}
        neighbor_coordinates: {self.neighbor_coordinates}
        neighbors: {self.neighbors}
        return self_str
        '''
        return self_str
