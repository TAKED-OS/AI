"""Compare state-space search strategies for the 4 L and 3 L jug problem."""

import argparse
import heapq
import tracemalloc
from collections import deque
from pathlib import Path
from statistics import median
from time import perf_counter_ns


START = (0, 0)
STATES = [(x, y) for x in range(5) for y in range(4)]
GOALS = {(2, y) for y in range(4)}


def transitions(state):
    x, y = state
    into_small = min(x, 3 - y)
    into_large = min(y, 4 - x)
    for action, target in (
        ("F4", (4, y)), ("F3", (x, 3)), ("E4", (0, y)), ("E3", (x, 0)),
        ("P43", (x - into_small, y + into_small)),
        ("P34", (x + into_large, y - into_large)),
    ):
        if target != state:
            yield action, target


def is_goal(state):
    return state in GOALS


def cost(_source, _target):
    return 1


def heuristic(state):
    # Any non-goal must take at least one operation.
    if is_goal(state):
        return 0
    return 1 if any(is_goal(target) for _, target in transitions(state)) else 2


def path_to(state, parents):
    path = []
    while state is not None:
        path.append(state)
        state = parents[state]
    return list(reversed(path))


def blind(start, strategy):
    frontier = deque([start])
    parents = {start: None}
    visited = 0
    while frontier:
        state = frontier.pop() if strategy == "DFS" else frontier.popleft()
        visited += 1
        if is_goal(state):
            return path_to(state, parents), visited
        if strategy == "mixed":
            x, y = state
            # Direct rule for the subspace containing exactly two litres in total.
            if y > 0 and x + y == 2:
                return path_to(state, parents) + [(2, 0)], visited
        for _, target in transitions(state):
            if target not in parents:
                parents[target] = state
                frontier.append(target)
    return [], visited


def astar(start):
    frontier = [(heuristic(start), heuristic(start), 0, start)]
    parents = {start: None}
    distances = {start: 0}
    visited = 0
    while frontier:
        _, _, distance, state = heapq.heappop(frontier)
        if distance != distances[state]:
            continue
        visited += 1
        if is_goal(state):
            return path_to(state, parents), visited
        for _, target in transitions(state):
            new_distance = distance + cost(state, target)
            if new_distance < distances.get(target, float("inf")):
                distances[target] = new_distance
                parents[target] = state
                h = heuristic(target)
                heapq.heappush(frontier, (new_distance + h, h, new_distance, target))
    return [], visited


def reverse_adjacency():
    incoming = {state: [] for state in STATES}
    for source in STATES:
        for _, target in transitions(source):
            incoming[target].append(source)
    return incoming


def reverse_search(start):
    incoming = reverse_adjacency()
    frontier = deque(sorted(GOALS))
    successors = dict.fromkeys(GOALS)
    visited = 0
    while frontier:
        state = frontier.popleft()
        visited += 1
        if state == start:
            return list(reversed(path_to(start, successors))), visited
        for source in incoming[state]:
            if source not in successors:
                successors[source] = state
                frontier.append(source)
    return [], visited


def graph():
    lines = ["flowchart LR"]
    for x, y in STATES:
        lines.append(f'    s{x}{y}["({x}, {y})"]')
        for action, (a, b) in transitions((x, y)):
            lines.append(f"    s{x}{y} -->|{action}| s{a}{b}")
    lines += [
        "    classDef source fill:#d1e7ff,color:#142a44",
        "    classDef goal fill:#d5f3dd,color:#17412b",
        "    class s00 source",
        "    class s20,s21,s22,s23 goal",
    ]
    return "```mermaid\n" + "\n".join(lines) + "\n```\n"



def benchmark_markdown(results):
    lines = [
        "# Результаты поиска",
        "",
        "Время — медиана 501 запуска. Память — пик выделений Python за отдельный запуск.",
        "",
        "| Стратегия | Шаги | Посещено состояний | Время, мкс | Память, байт |",
        "|---|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| {result['strategy']} | {result['steps']} | {result['visited']} | "
            f"{result['median_us']:.3f} | {result['peak_bytes']} |"
        )
    lines += ["", "## Найденные пути", ""]
    for result in results:
        path = " → ".join(f"({x}, {y})" for x, y in result["path"])
        lines.append(f"- **{result['strategy']}** — {path or 'путь отсутствует'}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Каталог экспорта измерений и графа")
    args = parser.parse_args()
    methods = {
        "DFS": lambda: blind(START, "DFS"),
        "BFS": lambda: blind(START, "BFS"),
        "A*": lambda: astar(START),
        "Обратный BFS": lambda: reverse_search(START),
        "Смешанный": lambda: blind(START, "mixed"),
    }
    results = []
    for name, search in methods.items():
        path, visited = search()
        samples = []
        for _ in range(501):
            started = perf_counter_ns()
            search()
            samples.append(perf_counter_ns() - started)
        tracemalloc.start()
        search()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        results.append(dict(strategy=name, path=path, visited=visited, steps=len(path)-1,
                            median_us=round(median(samples) / 1000, 3), peak_bytes=peak))
    print(benchmark_markdown(results), end="")
    if args.output is not None:
        output = args.output
        output.mkdir(parents=True, exist_ok=True)
        (output / "benchmark.md").write_text(benchmark_markdown(results), encoding="utf-8")
        (output / "graph.md").write_text(
            "# Граф пространства состояний\n\n"
            "F — наполнить, E — опустошить, P — перелить. Цифры обозначают объёмы кружек.\n\n"
            + graph(), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
