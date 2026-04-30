from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Iterable, Iterator


BOARD_SIZE = 8
TOTAL_SQUARES = BOARD_SIZE * BOARD_SIZE
ALL_SQUARES = tuple(range(TOTAL_SQUARES))

MOVE_DELTAS = (
    (-2, -1),
    (-2, 1),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (1, 2),
    (2, -1),
    (2, 1),
)

MUTATION_OPERATORS = {"swap", "insert", "inversion", "shuffle", "mixed"}


def index_to_coord(index: int) -> tuple[int, int]:
    return divmod(index, BOARD_SIZE)


def coord_to_index(row: int, col: int) -> int:
    return row * BOARD_SIZE + col


def index_to_label(index: int) -> str:
    row, col = index_to_coord(index)
    return f"{chr(ord('a') + col)}{BOARD_SIZE - row}"


def build_knight_neighbors() -> tuple[tuple[int, ...], ...]:
    neighbors: list[tuple[int, ...]] = []
    for index in ALL_SQUARES:
        row, col = index_to_coord(index)
        moves: list[int] = []
        for dr, dc in MOVE_DELTAS:
            next_row = row + dr
            next_col = col + dc
            if 0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE:
                moves.append(coord_to_index(next_row, next_col))
        neighbors.append(tuple(moves))
    return tuple(neighbors)


KNIGHT_NEIGHBORS = build_knight_neighbors()


@dataclass(frozen=True)
class RouteStats:
    valid_moves: int
    longest_streak: int
    unique_squares: int
    fitness: float

    @property
    def invalid_moves(self) -> int:
        return (TOTAL_SQUARES - 1) - self.valid_moves

    @property
    def complete(self) -> bool:
        return self.valid_moves == TOTAL_SQUARES - 1 and self.unique_squares == TOTAL_SQUARES


@dataclass(frozen=True)
class GAConfig:
    population_size: int = 240
    generations: int = 1000
    tournament_size: int = 4
    elite_size: int = 6
    crossover_rate: float = 0.9
    mutation_rate: float = 0.35
    mutation_operator: str = "mixed"
    seed: int | None = None
    warm_start: bool = True
    report_every: int = 5


def is_knight_move(origin: int, destination: int) -> bool:
    return destination in KNIGHT_NEIGHBORS[origin]


def evaluate_route(route: list[int]) -> RouteStats:
    valid_moves = 0
    longest_streak = 0
    current_streak = 0

    for origin, destination in zip(route, route[1:]):
        if is_knight_move(origin, destination):
            valid_moves += 1
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0

    unique_squares = len(set(route))
    duplicate_penalty = (TOTAL_SQUARES - unique_squares) * 500
    length_penalty = abs(TOTAL_SQUARES - len(route)) * 500
    fitness = (valid_moves * 100) + (longest_streak * 2) + unique_squares - duplicate_penalty - length_penalty

    return RouteStats(
        valid_moves=valid_moves,
        longest_streak=longest_streak,
        unique_squares=unique_squares,
        fitness=fitness,
    )


def invalid_edge_indexes(route: list[int]) -> list[int]:
    return [
        index
        for index, (origin, destination) in enumerate(zip(route, route[1:]))
        if not is_knight_move(origin, destination)
    ]


def repair_route(route: Iterable[int], rng: random.Random) -> list[int]:
    repaired = list(route)[:TOTAL_SQUARES]
    seen: set[int] = set()
    duplicate_positions: list[int] = []

    for position, square in enumerate(repaired):
        if square not in ALL_SQUARES or square in seen:
            duplicate_positions.append(position)
        else:
            seen.add(square)

    missing = [square for square in ALL_SQUARES if square not in seen]
    rng.shuffle(missing)

    for position, square in zip(duplicate_positions, missing):
        repaired[position] = square

    if len(repaired) < TOTAL_SQUARES:
        repaired.extend(missing[len(duplicate_positions) :])

    return repaired


def random_route(rng: random.Random) -> list[int]:
    route = list(ALL_SQUARES)
    rng.shuffle(route)
    return route


def onward_count(square: int, visited: set[int]) -> int:
    return sum(1 for neighbor in KNIGHT_NEIGHBORS[square] if neighbor not in visited)


def warnsdorff_route(rng: random.Random, start: int | None = None) -> list[int]:
    current = rng.choice(ALL_SQUARES) if start is None else start
    route = [current]
    visited = {current}

    while len(route) < TOTAL_SQUARES:
        candidates = [neighbor for neighbor in KNIGHT_NEIGHBORS[current] if neighbor not in visited]
        if not candidates:
            break

        candidates.sort(key=lambda square: (onward_count(square, visited), rng.random()))
        if len(candidates) > 1 and rng.random() < 0.16:
            current = rng.choice(candidates[: min(3, len(candidates))])
        else:
            current = candidates[0]

        route.append(current)
        visited.add(current)

    if len(route) < TOTAL_SQUARES:
        remaining = [square for square in ALL_SQUARES if square not in visited]
        rng.shuffle(remaining)
        route.extend(remaining)

    return route


def best_warnsdorff_seed(rng: random.Random, attempts: int = 160) -> list[int]:
    best_route = random_route(rng)
    best_stats = evaluate_route(best_route)
    starts = list(ALL_SQUARES)
    rng.shuffle(starts)

    for attempt in range(attempts):
        start = starts[attempt % TOTAL_SQUARES]
        route = warnsdorff_route(rng, start=start)
        stats = evaluate_route(route)
        if stats.fitness > best_stats.fitness:
            best_route = route
            best_stats = stats
        if stats.complete:
            return route

    return best_route


def ordered_crossover(parent_a: list[int], parent_b: list[int], rng: random.Random) -> list[int]:
    start, end = sorted(rng.sample(range(TOTAL_SQUARES), 2))
    child: list[int | None] = [None] * TOTAL_SQUARES
    child[start : end + 1] = parent_a[start : end + 1]
    copied = set(parent_a[start : end + 1])

    parent_index = (end + 1) % TOTAL_SQUARES
    child_index = (end + 1) % TOTAL_SQUARES

    while any(square is None for square in child):
        candidate = parent_b[parent_index]
        if candidate not in copied:
            child[child_index] = candidate
            copied.add(candidate)
            child_index = (child_index + 1) % TOTAL_SQUARES
        parent_index = (parent_index + 1) % TOTAL_SQUARES

    return [square for square in child if square is not None]


def mutate_swap(route: list[int], rng: random.Random) -> list[int]:
    mutated = route.copy()
    first, second = rng.sample(range(TOTAL_SQUARES), 2)
    mutated[first], mutated[second] = mutated[second], mutated[first]
    return mutated


def mutate_insert(route: list[int], rng: random.Random) -> list[int]:
    mutated = route.copy()
    origin, destination = rng.sample(range(TOTAL_SQUARES), 2)
    square = mutated.pop(origin)
    mutated.insert(destination, square)
    return mutated


def mutate_inversion(route: list[int], rng: random.Random) -> list[int]:
    mutated = route.copy()
    start, end = sorted(rng.sample(range(TOTAL_SQUARES), 2))
    mutated[start : end + 1] = reversed(mutated[start : end + 1])
    return mutated


def mutate_shuffle(route: list[int], rng: random.Random) -> list[int]:
    mutated = route.copy()
    start, end = sorted(rng.sample(range(TOTAL_SQUARES), 2))
    segment = mutated[start : end + 1]
    rng.shuffle(segment)
    mutated[start : end + 1] = segment
    return mutated


def apply_mutation(route: list[int], operator: str, rng: random.Random) -> list[int]:
    if operator == "mixed":
        operator = rng.choice(["swap", "insert", "inversion", "shuffle"])

    if operator == "swap":
        return mutate_swap(route, rng)
    if operator == "insert":
        return mutate_insert(route, rng)
    if operator == "inversion":
        return mutate_inversion(route, rng)
    if operator == "shuffle":
        return mutate_shuffle(route, rng)

    raise ValueError(f"Operador de mutacao invalido: {operator}")


def tournament_selection(
    evaluated_population: list[tuple[RouteStats, list[int]]],
    tournament_size: int,
    rng: random.Random,
) -> list[int]:
    size = min(tournament_size, len(evaluated_population))
    competitors = rng.sample(evaluated_population, size)
    return max(competitors, key=lambda candidate: candidate[0].fitness)[1]


def initial_population(config: GAConfig, rng: random.Random) -> list[list[int]]:
    population: list[list[int]] = []

    if config.warm_start:
        seed_route = best_warnsdorff_seed(rng)
        population.append(seed_route)

        warm_count = max(1, int(config.population_size * 0.55))
        while len(population) < warm_count:
            route = warnsdorff_route(rng)
            if rng.random() < 0.75:
                route = apply_mutation(route, "mixed", rng)
            population.append(repair_route(route, rng))

    while len(population) < config.population_size:
        population.append(random_route(rng))

    return population[: config.population_size]


def route_payload(
    generation: int,
    route: list[int],
    stats: RouteStats,
    elapsed_seconds: float,
    done: bool = False,
    reason: str = "running",
) -> dict:
    return {
        "generation": generation,
        "route": [
            {
                "index": square,
                "row": index_to_coord(square)[0],
                "col": index_to_coord(square)[1],
                "label": index_to_label(square),
            }
            for square in route
        ],
        "valid_moves": stats.valid_moves,
        "invalid_moves": stats.invalid_moves,
        "invalid_edges": invalid_edge_indexes(route),
        "longest_streak": stats.longest_streak,
        "unique_squares": stats.unique_squares,
        "fitness": round(stats.fitness, 2),
        "complete": stats.complete,
        "elapsed_seconds": round(elapsed_seconds, 2),
        "done": done,
        "reason": reason,
    }


def sanitize_config(config: GAConfig) -> GAConfig:
    mutation_operator = config.mutation_operator if config.mutation_operator in MUTATION_OPERATORS else "mixed"
    population_size = min(max(config.population_size, 20), 1000)
    generations = min(max(config.generations, 1), 20000)
    tournament_size = min(max(config.tournament_size, 2), population_size)
    elite_size = min(max(config.elite_size, 1), max(1, population_size // 3))
    crossover_rate = min(max(config.crossover_rate, 0.0), 1.0)
    mutation_rate = min(max(config.mutation_rate, 0.0), 1.0)
    report_every = min(max(config.report_every, 1), 250)

    return GAConfig(
        population_size=population_size,
        generations=generations,
        tournament_size=tournament_size,
        elite_size=elite_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        mutation_operator=mutation_operator,
        seed=config.seed,
        warm_start=config.warm_start,
        report_every=report_every,
    )


def run_genetic_algorithm(config: GAConfig) -> Iterator[dict]:
    config = sanitize_config(config)
    rng = random.Random(config.seed)
    started_at = time.perf_counter()
    population = initial_population(config, rng)

    best_route = population[0]
    best_stats = evaluate_route(best_route)

    for generation in range(config.generations + 1):
        evaluated_population = [(evaluate_route(route), route) for route in population]
        evaluated_population.sort(key=lambda candidate: candidate[0].fitness, reverse=True)

        generation_best_stats, generation_best_route = evaluated_population[0]
        if generation_best_stats.fitness > best_stats.fitness:
            best_stats = generation_best_stats
            best_route = generation_best_route.copy()

        solved = best_stats.complete
        should_report = generation == 0 or generation % config.report_every == 0 or solved
        if should_report:
            yield route_payload(
                generation=generation,
                route=best_route,
                stats=best_stats,
                elapsed_seconds=time.perf_counter() - started_at,
                done=solved,
                reason="solution" if solved else "running",
            )

        if solved:
            return
        if generation == config.generations:
            break

        next_population = [route.copy() for _, route in evaluated_population[: config.elite_size]]

        while len(next_population) < config.population_size:
            parent_a = tournament_selection(evaluated_population, config.tournament_size, rng)
            parent_b = tournament_selection(evaluated_population, config.tournament_size, rng)

            if rng.random() < config.crossover_rate:
                child = ordered_crossover(parent_a, parent_b, rng)
            else:
                child = parent_a.copy()

            if rng.random() < config.mutation_rate:
                child = apply_mutation(child, config.mutation_operator, rng)

            next_population.append(repair_route(child, rng))

        population = next_population

    yield route_payload(
        generation=config.generations,
        route=best_route,
        stats=best_stats,
        elapsed_seconds=time.perf_counter() - started_at,
        done=True,
        reason="max_generations",
    )
