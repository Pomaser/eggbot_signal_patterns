from individual import Individual


class Generation:
    def __init__(self, num_individuals: int = 12):
        self.individuals: list[Individual] = [Individual() for _ in range(num_individuals)]
