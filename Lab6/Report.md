# Лабораторная работа №6. Представление задачи и поиск в пространстве состояний

Молдавский государственный университет · Искусственный интеллект

Петр Мартынюк · IA2404 · 2026

Вариант 1. Две кружки объёмом 4 и 3 литра.

## Цель и теоретические сведения

Представить задачу измерения объёма как ориентированный граф, реализовать несколько стратегий поиска и сравнить их. Вершина графа хранит объёмы воды в обеих кружках. Дуга соответствует одной допустимой операции. Стоимость пути равна числу операций.

## Формальное описание

$Z=(S,S_0,S_G,R,C,f)$, где:

- $S=\{(x,y)\mid x\in\{0,1,2,3,4\},\ y\in\{0,1,2,3\}\}$. Первая координата относится к кружке 4 л, вторая — к кружке 3 л. Состояния с дробными, отрицательными или превышающими вместимость объёмами недопустимы. Внутренние состояния в пределах вместимости допустимы формально, хотя из исходного состояния не все достижимы.
- $S_0=\{(0,0)\}$. Обе кружки изначально пусты.
- $S_G=\{(2,0),(2,1),(2,2),(2,3)\}$. Нужно получить 2 л в большой кружке.
- $R$ — множество переходов из таблицы ниже.
- $C(s,t)=1$ для любого разрешённого перехода.
- $f$ задаёт порядок обхода. Для DFS и BFS он определяется стеком и очередью. Для A* используется $f(s)=g(s)+h(s)$.

Кортеж из двух целых непосредственно кодирует объёмы, сравнивается по значению и может быть ключом словаря посещённых состояний. Граф представлен функцией соседства и материализуется для обратного поиска и визуализации.

## Правила переходов

| Метка | Условие | Операция | Новое состояние |
|---|---|---|---|
| F4 | x < 4 | Наполнить большую кружку | (4, y) |
| F3 | y < 3 | Наполнить малую кружку | (x, 3) |
| E4 | x > 0 | Опустошить большую кружку | (0, y) |
| E3 | y > 0 | Опустошить малую кружку | (x, 0) |
| P43 | x > 0 и y < 3 | Перелить в малую, d = min(x, 3 − y) | (x − d, y + d) |
| P34 | y > 0 и x < 4 | Перелить в большую, d = min(y, 4 − x) | (x + d, y − d) |

При переливании общий объём сохраняется и либо опустошается кружка-источник, либо заполняется кружка-приёмник. Правила исключают пустые операции. Действительные обратные дуги получены обращением списка прямых дуг. [Визуализация полного графа](results/graph.md)

## Стратегии и псевдокоды

**BFS и DFS.** Обе стратегии отмечают вершину при добавлении во фронт поиска. Для BFS извлекается старейший элемент, для DFS — последний. BFS возвращает оптимальный путь при единичной стоимости.

```text
пометить старт и добавить его во фронт поиска
пока фронт не пуст:
    взять состояние из начала очереди BFS или вершины стека DFS
    если состояние целевое: восстановить путь по родителям
    для каждого допустимого перехода:
        если сосед ещё не отмечен: записать родителя и добавить соседа
вернуть отсутствие пути
```

**A*.** $h(s)=0$ для цели, $h(s)=1$ при прямой дуге к цели, иначе $h(s)=2$. В последнем случае одного шага недостаточно, поэтому оценка допустима. На любой дуге к цели значение источника равно 1 или 0. Для остальных дуг значение уменьшается максимум на 1. Значит, эвристика согласована.

```text
записать g(старт) = 0 и добавить старт в очередь по g+h
пока очередь не пуста:
    извлечь минимальное g+h, при равенстве предпочесть меньшее h
    пропустить запись, если её g устарело
    если состояние целевое: восстановить путь
    для каждого соседа:
        если g(текущее) + 1 улучшает g(соседа):
            обновить расстояние, родителя и очередь
вернуть отсутствие пути
```

**Обратный BFS.** Поиск начинается одновременно из всех целей. Он использует предшественников по допустимым прямым переходам. У найденного предшественника записывается следующий шаг к цели.

```text
построить список входящих дуг для каждой вершины
пометить все цели и добавить их в очередь
пока очередь не пуста:
    извлечь вершину
    если она равна старту: пройти по записанным следующим шагам
    для каждого непомеченного предшественника:
        пометить его, записать следующую вершину и добавить в очередь
вернуть отсутствие пути
```

**Смешанный поиск.** Используется BFS и прямое правило для подпространства с суммарным объёмом 2 л. Если малая кружка содержит воду, переливание из неё даёт цель $(2,0)$. Правило заменяет дальнейший обход с этой вершины одним вычисляемым шагом. При единичной стоимости, если ранее из очереди не извлечена цель, путь через правило может иметь ту же длину или быть на один шаг длиннее другого решения того же слоя. Для выбранного старта длина сверена с BFS.

```text
начать BFS
при извлечении состояния проверить достижение цели
если x+y=2 и y>0: добавить к найденному пути операцию P34 и завершить
иначе добавить ещё не отмеченных соседей по правилам BFS
```

## Последовательности состояний

| Стратегия | Путь от старта к цели |
|---|---|
| DFS | (0,0) → (0,3) → (3,0) → (3,3) → (4,2) → (0,2) → (2,0) |
| BFS | (0,0) → (4,0) → (1,3) → (1,0) → (0,1) → (4,1) → (2,3) |
| A* | (0,0) → (4,0) → (1,3) → (1,0) → (0,1) → (4,1) → (2,3) |
| Обратный BFS | (0,0) → (0,3) → (3,0) → (3,3) → (4,2) → (0,2) → (2,0) |
| Смешанный | (0,0) → (0,3) → (3,0) → (3,3) → (4,2) → (0,2) → (2,0) |

## Сравнительный анализ

Посещёнными считаются узлы, извлечённые из фронта. Цель, добавленная напрямую в смешанном методе, отдельно не извлекается. Время — медиана 501 вызова через `perf_counter_ns`. Память — пик отслеживаемых Python выделений на отдельном запуске через `tracemalloc`. Для обратного BFS оба замера включают построение входящих дуг. Измерения выполнены в Python 3.14.7 на Windows.

| Стратегия | Шаги | Посещено | Время, мкс | Пик, байт | Оптимальность из (0,0) |
|---|---:|---:|---:|---:|---|
| DFS | 6 | 7 | 10.1 | 1504 | Да, проверено по BFS. В общем случае без гарантии |
| BFS | 6 | 13 | 18.6 | 1912 | Да |
| A* | 6 | 11 | 47.6 | 2152 | Да |
| Обратный BFS | 6 | 19 | 38.3 | 3208 | Да |
| Смешанный | 6 | 12 | 17.8 | 1912 | Да, проверено по BFS |

[Измерения и пути, записанные программой](results/benchmark.md)

## Заключение

DFS оказался самым быстрым и посетил меньше всего вершин при данном порядке переходов. BFS даёт гарантию кратчайшего пути. A* посетил на две вершины меньше BFS, но на этом графе проверка соседей для эвристики и обслуживание очереди с приоритетом увеличили время. Обратный BFS подтвердил оптимальную длину, а обход от нескольких целей и построение входящих дуг увеличили затраты. Смешанная стратегия выполнила последний переход по прямому правилу и извлекла на одну вершину меньше BFS.

## Контрольные вопросы

1. **Что такое пространство состояний?** Это множество конфигураций задачи вместе с переходами, заданными операциями.
2. **Что такое переход и стратегия контроля?** Переход меняет состояние при выполнении условия. Стратегия контроля задаёт порядок выбора следующих состояний.
3. **Чем прямые методы отличаются от поисковых?** Прямое правило вычисляет действие для известного случая. Поиск перебирает допустимые варианты до цели.
4. **Чем различаются BFS и DFS?** BFS обходит слои и даёт кратчайший путь при одинаковой цене рёбер, но может хранить большой фронт. DFS углубляется по ветви и чувствителен к порядку переходов. Он не гарантирует кратчайший путь.
5. **Что такое эвристика?** Это оценка расстояния до цели, которая влияет на приоритет. Для A* допустимая оценка не превышает истинную остаточную стоимость.
6. **Почему важно представление?** Оно определяет затраты на сравнение состояний, хранение и генерацию переходов.
7. **Как предотвратить зацикливание?** Хранить уже обнаруженные состояния. При поиске по стоимости повторно обрабатывать вершину только тогда, когда найдена меньшая стоимость.

## Приложение. Исходный код

Для запуска из корня репозитория нужен Python 3.10 или новее. Внешних зависимостей нет.

```sh
python Lab6/main.py
```

Программа выводит пути и замеры и обновляет файлы в `Lab6/results`.

[Исходный файл](main.py)

<details>
<summary>Полный листинг программы</summary>

```python
"""Compare state-space search strategies for the 4 L and 3 L jug problem."""

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
    output = Path(__file__).with_name("results")
    output.mkdir(exist_ok=True)
    (output / "benchmark.md").write_text(benchmark_markdown(results), encoding="utf-8")
    (output / "graph.md").write_text(
        "# Граф пространства состояний\n\n"
        "F — наполнить, E — опустошить, P — перелить. Цифры обозначают объёмы кружек.\n\n"
        + graph(), encoding="utf-8"
    )
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
```

</details>
