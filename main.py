from matplotlib.pylab import diagonal
from tile import Tile
from map import Map
from utils import *
import time




def gen_report():
    # Required map sizes: 50×50, 75×75, 100×100, 150×150, and 200×200.
    # Diagonal neighbors: on and off (two conditions).
    # Trials: run each condition at least 10 times with different random initializations.
    # Images: Save the a random and constrained map for each dimmension/diagonal (not each trial)
    map_dimmensions = [50, 75, 100, 150, 200]
    diagonal_conditions = [True, False]
    num_trials = 10
    TERRAIN_DICT = {'W': 4, 'B': 1, 'L': 1, 'F': 1, 'H': 1, 'M': 4}
    terrain_list = list(TERRAIN_DICT.keys())
    terrain_weights = list(TERRAIN_DICT.values())
    compatible_dict = get_compatible_dict(terrain_list)

    total_unique_trials = len(map_dimmensions) * len(diagonal_conditions) * num_trials
    trial_count = 0
    for dimmension in map_dimmensions:
        for diagonal in diagonal_conditions:
            folder_path = f'reports/{dimmension}{"_diagonal" if diagonal else "_nondiagonal"}/'
            trial_strings = []
            success_iterations = 0
            failure_count = 0
            total_execution_time = 0
            for trial in range(num_trials):
                trial_count += 1
                print(f'{trial_count}/{total_unique_trials}: Running trial {trial} for dimmension {dimmension} and diagonal {diagonal}')
                my_map = Map(terrain_list, compatible_dict, terrain_weights=terrain_weights)
                my_map.generate_random_terrain(grid_height=dimmension, grid_width=dimmension, diagonal=diagonal)
                my_map.save_map(file_path=f'{folder_path}{trial}_map_pre_constrain_{dimmension}_{diagonal}.png')
                start_time = time.perf_counter()
                map_constrained, loops = my_map.constrain(max_loop=50)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                total_execution_time += execution_time
                my_map.save_map(file_path=f'{folder_path}{trial}_map_post_constrain_{dimmension}_{diagonal}.png')
                if map_constrained:
                    success_iterations += loops
                elif not map_constrained and loops == 50:
                    failure_count += 1
                
                trial_str = f'Trial: {trial}, Dimmension: {dimmension}, Diagonal: {diagonal}, Map Constrained: {map_constrained}, Loops: {loops}, Constrain Time: {execution_time:.6f} seconds'
                trial_strings.append(trial_str)
            if success_iterations > 0:
                trial_strings.append(f'Successfully constrained {num_trials - failure_count} out of {num_trials} maps. ({(num_trials - failure_count)/num_trials:.2%})')
                trial_strings.append(f'Average Loops to Constrain: {success_iterations/num_trials:.2f}')
                trial_strings.append(f'Average Time to Constrain: {total_execution_time/num_trials:.6f} seconds')
            else:
                trial_strings.append('Could not successfully constrain any maps.')
            trial_strings.append(f'Failure Count: {failure_count}/{num_trials}')
            # Save the trial strings to a text file
            with open(f'{folder_path}report_{dimmension}_{diagonal}.csv', 'w') as f:
                f.write('\n'.join(trial_strings))


gen_report()

