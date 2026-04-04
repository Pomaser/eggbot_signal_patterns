import random

from individual import Individual


class Generation:
    def __init__(
        self,
        num_individuals: int = 12,
        mutation_prob: float = 0.1,
        crossover_prob: float = 0.75,
    ):
        assert num_individuals % 2 == 0, "num_individuals must be even"
        self.mutation_prob = mutation_prob
        self.crossover_prob = crossover_prob
        self.individuals: list[Individual] = [Individual() for _ in range(num_individuals)]

    # ------------------------------------------------------------------
    # GA steps
    # ------------------------------------------------------------------

    def evaluate(self) -> None:
        """Sort individuals by rating ascending (worst → best)."""
        self.individuals.sort(key=lambda ind: ind.rating)

    def evolve(self, parent: "Generation") -> None:
        """Fill this generation by selecting from *parent* (already evaluated)."""
        parent.evaluate()
        n = len(self.individuals)
        q1 = n // 4
        q2 = n // 2
        q3 = n - n // 4
        src = parent.individuals

        # Guard against all-zero ratings causing an infinite loop
        eligible = [i for i, ind in enumerate(src) if ind.rating != 0]
        if not eligible:
            # No one was rated — just clone random parents
            eligible = list(range(n))

        def pick_index() -> int:
            spin = random.random()
            if spin <= 0.10:
                return random.randint(0, q1 - 1)
            elif spin <= 0.30:
                return random.randint(q1, q2 - 1)
            elif spin <= 0.60:
                return random.randint(q2, q3 - 1)
            else:
                return random.randint(q3, n - 1)

        # Selection
        for i in range(n):
            for _ in range(1000):  # max retries to avoid infinite loop
                idx = pick_index()
                if src[idx].rating != 0:
                    break
            else:
                idx = random.choice(eligible)

            self.individuals[i] = src[idx].clone()
            self.individuals[i].parents = [idx]

        # Single-point crossover on consecutive pairs
        for i in range(0, n, 2):
            if random.random() <= self.crossover_prob:
                point = random.randint(1, Individual.NUM_PARAMS - 1)
                a, b = self.individuals[i], self.individuals[i + 1]
                for p in range(point):
                    a.params[p], b.params[p] = b.params[p], a.params[p]
                # Record second parent
                if a.parents:
                    b.parents.append(a.parents[0])
                if b.parents:
                    a.parents.append(b.parents[0])

        # Mutation
        for ind in self.individuals:
            ind.mutate(self.mutation_prob)

    def reset_ratings(self) -> None:
        for ind in self.individuals:
            ind.rating = Individual.DEFAULT_RATING
