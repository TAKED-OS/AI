"""Four-bit genetic optimization for variant 7."""

import argparse
import csv
import math
import random
import tempfile
from pathlib import Path
from statistics import mean


L = 4
LIMIT = (1 << L) - 1


def fitness(gene):
    return math.exp(-(gene / LIMIT - 0.5) ** 2)


def run(n, pc, pm, generations, seed, output):
    rng = random.Random(seed)
    population = [rng.randrange(LIMIT + 1) for _ in range(n)]
    output.mkdir(parents=True, exist_ok=True)
    maxima = []
    best = population[0]
    first_optimum = None
    with (
        (output / "evolution.csv").open("w", newline="", encoding="utf-8") as evolution,
        (output / "statistics.csv").open("w", newline="", encoding="utf-8") as stats,
        (output / "operations.txt").open("w", encoding="utf-8") as log,
    ):
        rows, summary = csv.writer(evolution), csv.writer(stats)
        rows.writerow(["generation", "individual", "chromosome", "decimal", "x", "fitness"])
        summary.writerow(["generation", "minimum", "mean", "maximum"])
        print(f"N={n}, L={L}, pc={pc}, pm={pm}, G={generations}, seed={seed}", file=log)
        for generation in range(generations + 1):
            scores = [fitness(gene) for gene in population]
            maximum = max(scores)
            maxima.append(maximum)
            candidate = population[scores.index(maximum)]
            if maximum > fitness(best):
                best = candidate
            if candidate in (7, 8) and first_optimum is None:
                first_optimum = generation
            print(f"\nПоколение {generation}", file=log)
            for index, (gene, score) in enumerate(zip(population, scores), 1):
                rows.writerow([generation, index, f"{gene:04b}", gene, gene / LIMIT, score])
                print(f"  Особь {index}: {gene:04b}, b={gene}, x={gene / LIMIT:.8f}, fitness={score:.8f}", file=log)
            summary.writerow([generation, min(scores), mean(scores), maximum])
            print(f"  min={min(scores):.8f}, mean={mean(scores):.8f}, max={maximum:.8f}", file=log)
            if generation == generations:
                break
            children = []
            while len(children) < n:
                # Two-way tournament, with replacement, works for every population size.
                parents = [max(rng.choices(range(n), k=2), key=scores.__getitem__) for _ in range(2)]
                left, right = (population[index] for index in parents)
                print(f"  Селекция: особи №{parents[0]+1} и №{parents[1]+1}", file=log)
                if rng.random() < pc:
                    point = rng.randrange(1, L)
                    mask = (1 << (L - point)) - 1
                    left, right = (left & ~mask) | (right & mask), (right & ~mask) | (left & mask)
                    print(f"  Кроссовер: да, после бита {point}, потомки {left:04b}, {right:04b}", file=log)
                else:
                    print(f"  Кроссовер: нет, потомки {left:04b}, {right:04b}", file=log)
                for child in (left, right)[:n-len(children)]:
                    changed = []
                    for bit in range(1, L + 1):
                        if rng.random() < pm:
                            mask = 1 << (L - bit)
                            previous = int(bool(child & mask))
                            child ^= mask
                            changed.append(f"бит {bit}: {previous} → {1-previous}")
                    print(f"  Мутация, особь №{len(children)+1}: {', '.join(changed) or 'нет'}", file=log)
                    children.append(child)
            population = children
        result = (
            f"Лучшая хромосома: {best:04b}; x*={best / LIMIT:.8f}; f(x*)={fitness(best):.8f}; "
            f"первое поколение с оптимумом: {first_optimum if first_optimum is not None else '—'}"
        )
        print(result, file=log)
    plot(maxima, output / "maximum.svg")
    print(result)
    return best, first_optimum


def plot(values, path):
    low = fitness(0)
    points = " ".join(
        f"{72 + 622 * i / (len(values) - 1):.2f},{220 - 180 * (v - low) / (1 - low):.2f}"
        for i, v in enumerate(values)
    )
    labels = "".join(
        f'<text x="62" y="{224 - 45*i}" text-anchor="end">{low + (1-low)*i/4:.3f}</text>'
        f'<path d="M72 {220-45*i}H694" stroke="#d8e1e9"/>'
        for i in range(5)
    )
    path.write_text(f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="275" viewBox="0 0 720 275">
<rect width="720" height="275" fill="white"/>
<g font-family="sans-serif" font-size="13" fill="#26384b">
<text x="72" y="23">Максимальный fitness в популяции</text>{labels}
<path d="M72 40V220H694" fill="none" stroke="#26384b"/>
<polyline fill="none" stroke="#245cb5" stroke-width="2.5" points="{points}"/>
<text x="72" y="240">0</text><text x="694" y="240" text-anchor="end">{len(values) - 1}</text>
<text x="383" y="261" text-anchor="middle">Поколение</text></g></svg>""", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=int, default=4)
    parser.add_argument("--pc", type=float, default=0.8)
    parser.add_argument("--pm", type=float, default=0.05)
    parser.add_argument("--generations", type=int, default=30)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--output", type=Path, help="Каталог экспорта (по умолчанию временный)")
    parser.add_argument("--experiments", action="store_true")
    args = parser.parse_args()
    if not (2 <= args.population <= 20 and args.generations >= 30 and 0 <= args.pc <= 1 and 0 <= args.pm <= 1):
        parser.error("Требуется 2 ≤ N ≤ 20, G ≥ 30, 0 ≤ pc, pm ≤ 1")
    output = args.output if args.output is not None else Path(tempfile.mkdtemp(prefix="lab5-"))
    print(f"Каталог экспорта: {output}")
    if args.experiments:
        for name, n, pc, pm in [
            ("exp1", 4, .8, .05), ("exp2", 4, .4, .01),
            ("exp3", 4, .9, .15), ("exp4", 12, .8, .05),
        ]:
            print(name)
            run(n, pc, pm, args.generations, args.seed, output / name)
    else:
        run(args.population, args.pc, args.pm, args.generations, args.seed, output)


if __name__ == "__main__":
    main()
