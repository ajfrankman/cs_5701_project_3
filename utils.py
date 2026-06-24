import time
from pathlib import Path
from map import Map


def get_terrain_list(terrain_str: str):
    return terrain_str.strip().split(',')


def get_compatible_dict(terrain_list: list[str]):
    # Create a dictionary where each terrain type is a key, and the
    # value is a list of compatible terrain types (including itself
    # and its immediate neighbors in the list)
    compatible_dict = {}
    for index, terrain in enumerate(terrain_list):
        compatible_dict[terrain] = [terrain_list[index]]
        if index + 1 <= len(terrain_list) - 1:
            compatible_dict[terrain].append(terrain_list[index + 1])
        if index - 1 >= 0:
            compatible_dict[terrain].append(terrain_list[index - 1])
    return compatible_dict


def _write_lines(file_path: str, lines: list[str]) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(lines))


def _report_folder_path(dimension: int, diagonal: bool) -> str:
    return f'reports/{dimension}{"_diagonal" if diagonal else "_nondiagonal"}/'


def _run_trial(dimension: int, diagonal: bool, trial: int, folder_path: str,
        terrain_list: list[str],compatible_dict: dict[str, list[str]],
        terrain_weights: list[int]) -> dict:
    
    my_map = Map(terrain_list, compatible_dict, terrain_weights=terrain_weights)
    my_map.generate_random_terrain(
        grid_height=dimension,
        grid_width=dimension,
        diagonal=diagonal,
    )
    file_path = f'{folder_path}{trial}_map_pre_constrain_{dimension}_{diagonal}.png'
    my_map.save_map(file_path=file_path)

    start_time = time.perf_counter()
    map_constrained, loops, fewest_conflicts = my_map.constrain()
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    my_map.save_map(
        file_path=f'{folder_path}{trial}_map_post_constrain_{dimension}_{diagonal}.png'
    )

    return {
        'trial': trial,
        'dimension': dimension,
        'diagonal': diagonal,
        'map_constrained': map_constrained,
        'loops': loops,
        'fewest_conflicts': fewest_conflicts,
        'execution_time': execution_time,
    }


def _build_trial_lines(result: dict) -> str:
    return (
        f'Trial: {result["trial"]}, Dimension: {result["dimension"]}, '
        f'Diagonal: {result["diagonal"]}, Map Constrained: {result["map_constrained"]}, '
        f'Loops: {result["loops"]}, Constrain Time: {result["execution_time"]:.6f} seconds, '
        f'Fewest Conflicts: {result["fewest_conflicts"]}'
    )


def _build_condition_report_lines(trial_results: list[dict], num_trials: int) -> tuple[list[str], float | str]:
    success_iterations = sum(
        result['loops'] for result in trial_results if result['map_constrained']
    )
    failure_count = sum(
        1 for result in trial_results if not result['map_constrained']
    )
    successful_trials = num_trials - failure_count

    report_lines = []
    if successful_trials > 0:
        report_lines.append(
            f'Successfully constrained {successful_trials} out of {num_trials} maps. '
            f'({successful_trials / num_trials:.2%})'
        )
        report_lines.append(
            f'Average Loops to Constrain: {success_iterations / num_trials:.2f}'
        )
        report_lines.append(
            f'Average Time to Constrain: '
            f'{sum(result["execution_time"] for result in trial_results) / num_trials:.6f} seconds'
        )
    else:
        report_lines.append('Could not successfully constrain any maps.')

    report_lines.append(f'Failure Count: {failure_count}/{num_trials}')
    avg_iterations = (
        success_iterations / successful_trials if successful_trials > 0 else 'N/A'
    )
    return report_lines, avg_iterations


def _write_condition_report(dimension: int, diagonal: bool, trial_results: list[dict],
        num_trials: int, final_report_lines: list[str],) -> None:
    
    folder_path = _report_folder_path(dimension, diagonal)
    report_lines, avg_iterations = _build_condition_report_lines(
        trial_results, num_trials
    )

    trial_lines = [_build_trial_lines(result) for result in trial_results]
    trial_lines.extend(report_lines)
    _write_lines(f'{folder_path}report_{dimension}_{diagonal}.csv', trial_lines)

    final_report_lines.append(
        f'{dimension}, {diagonal}, {avg_iterations}, '
        f'{sum(1 for result in trial_results if not result["map_constrained"])}/{num_trials}, '
        f'{"Max Loops without improvement" if sum(1 for result in trial_results if not result["map_constrained"]) == num_trials else "Constrained Successfully"}'
    )


def gen_report():
    # Required map sizes: 50×50, 75×75, 100×100, 150×150, and 200×200.
    # Diagonal neighbors: on and off (two conditions).
    # Trials: run each condition at least 10 times with different random initializations.
    # Images: Save a random and constrained map for each dimension/diagonal (not each trial).
    # map_dimensions = [50, 60, 70, 75, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
    map_dimensions = [50, 75, 100, 150, 200]
    diagonal_conditions = [True, False]
    num_trials = 10
    terrain_dict = {'W': 20, 'B': 0, 'L': 0, 'F': 0, 'H': 0, 'M': 20}
    final_report_lines = [
        'Map Size, Diagonals, Avg. Iterations (success), Failures/Total Trials, Stop Criterion'
    ]
    terrain_list = list(terrain_dict.keys())
    terrain_weights = list(terrain_dict.values())
    compatible_dict = get_compatible_dict(terrain_list)

    total_unique_trials = len(map_dimensions) * len(diagonal_conditions) * num_trials
    trial_count = 0

    for dimension in map_dimensions:
        for diagonal in diagonal_conditions:
            folder_path = _report_folder_path(dimension, diagonal)
            trial_results = []

            for trial in range(num_trials):
                trial_count += 1
                print(
                    f'{trial_count}/{total_unique_trials}: '
                    f'Running trial {trial} for dimension {dimension} and diagonal {diagonal}'
                )
                result = _run_trial(
                    dimension=dimension,
                    diagonal=diagonal,
                    trial=trial,
                    folder_path=folder_path,
                    terrain_list=terrain_list,
                    compatible_dict=compatible_dict,
                    terrain_weights=terrain_weights,
                )
                trial_results.append(result)

            _write_condition_report(
                dimension=dimension,
                diagonal=diagonal,
                trial_results=trial_results,
                num_trials=num_trials,
                final_report_lines=final_report_lines,
            )

    _write_lines('reports/final_report.csv', final_report_lines)
