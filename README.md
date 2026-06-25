# CS 5701 Project 3

## Overview
This project builds and constrains square terrain maps using a simple min-conflicts approach. Each tile is assigned a terrain type, and the program repeatedly updates tiles until every tile is compatible with its neighbors (or the maximum loop limit is reached).

The project includes support for:
- Any map size with these defaults: 50x50, 75x75, 100x100, 150x150, and 200x200
- diagonal and non-diagonal neighbor rules
- repeated trials with different random initializations
- generated image outputs before and after constraining
- trial summary reports for each configuration
- terrain density weights

## Project Structure
- [main.py](main.py) — runs the experiment and writes the report files
- [map.py](map.py) — defines the `Map` class for terrain generation, visualization, and constraint solving
- [tile.py](tile.py) — defines the `Tile` data structure
- [utils.py](utils.py) — contains helper functions for terrain parsing and compatibility setup
- [reports/](reports/) — output reports and images for each grid size and neighbor setting
- [terrains/](terrains/) — sample terrain input files (if used)

## Terrain Model
The program uses the terrain set:
- `W` = Water
- `B` = Beach
- `L` = Lowland
- `F` = Forest
- `H` = Hill
- `M` = Mountain

Compatibility is determined from a neighbor mapping built in [utils.py](utils.py). The map solver updates a tile to the terrain that is compatible with the most neighboring tiles (or randomly if tied to stop race conditions).

## How the Solver Works
1. A random terrain map is created for the requested grid size.
2. Each tile is assigned neighbors based on the chosen diagonal setting.
3. The `constrain()` method repeatedly calls `run_min_conflict()` until:
   - all tiles are compatible, or
   - the improvement is not observed after some number of loops (default 20).
4. The resulting map is saved as an image, and the trial statistics are recorded.

## Running the Project
From the project root, run:

```bash
python main.py
```

This will:
- generate maps for every required size and neighbor condition
- save images before and after constraining
- create report files in the corresponding folders under [reports/](reports/)

## Output Files
Each experiment folder under [reports/](reports/) contains:
- PNG images showing the map before and after constraining
- a report text/CSV file with per-trial statistics

## Dependencies
See *Requirements.txt*

## Notes
Becuase the maps looked a little unnatural, I included the ability to weight certain terrains as being more likely. This is passed into the Map class if desired but equally selects if not. This only applies to random generation. When constraining, everything is equally chosen from since I didn't have time to figure out why it caused race conditions.

The code is designed to be easily extended by adding more terrain types or changing the compatibility rules in [utils.py](utils.py).

The constraint function doesn't rely on a 2d grid, and every tile has a list of neighbors, it should be relatively easy to make a hex (or triangle, or mix of shapes) grid style random map generator.
