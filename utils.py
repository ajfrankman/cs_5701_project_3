
def get_terrain_list(terrain_str: str):
    return terrain_str.strip().split(',')
    

def get_compatible_dict(terrain_list: list[str]):
    compatible_dict = {}
    for index, terrain in enumerate(terrain_list):
        compatible_dict[terrain] = [terrain_list[index]]
        if index + 1 <= len(terrain_list) - 1:                
            compatible_dict[terrain].append(terrain_list[index + 1])
        if index - 1 >= 0:
            compatible_dict[terrain].append(terrain_list[index - 1])
    return compatible_dict