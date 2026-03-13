import random
import string
from dataclasses import dataclass
from typing import List


TARGET = "Привет, мир!"  # целевая фраза
POPULATION_SIZE = 200    # размер популяции
MUTATION_RATE = 0.05     # вероятность мутации символа
ELITE_SIZE = 5           # сколько лучших особей сохраняем без изменений
MAX_GENERATIONS = 10_000 # максимум поколений, чтобы не зациклиться


# Разрешённые символы (можно менять под задачу)
ALPHABET = (
    string.ascii_letters
    + string.digits
    + " ,.!?ёЁабвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
)


@dataclass
class Individual:
    genome: str
    fitness: float

    def __str__(self) -> str:
        return f"{self.genome} (fitness={self.fitness:.4f})"


def random_genome(length: int) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(length))


def calculate_fitness(genome: str, target: str) -> float:
    """
    Фитнес — доля совпавших символов по позиции.
    Можно придумать и другие функции приспособленности.
    """
    score = 0
    for g, t in zip(genome, target):
        if g == t:
            score += 1
    return score / len(target)


def create_individual(target: str) -> Individual:
    genome = random_genome(len(target))
    fitness = calculate_fitness(genome, target)
    return Individual(genome, fitness)


def initialize_population(size: int, target: str) -> List[Individual]:
    return [create_individual(target) for _ in range(size)]


def select_parent(population: List[Individual]) -> Individual:
    """
    Рулеточный отбор: чем лучше фитнес, тем выше шанс быть выбранным.
    """
    total_fitness = sum(ind.fitness for ind in population)

    # если вдруг вся популяция с нулевым фитнесом — выбираем случайно
    if total_fitness == 0:
        return random.choice(population)

    r = random.uniform(0, total_fitness)
    cumulative = 0.0
    for ind in population:
        cumulative += ind.fitness
        if cumulative >= r:
            return ind
    return population[-1]  # на всякий случай


def crossover(parent1: Individual, parent2: Individual) -> str:
    """
    Одноточечное скрещивание: часть от первого родителя, часть от второго.
    """
    cut = random.randint(0, len(parent1.genome))
    return parent1.genome[:cut] + parent2.genome[cut:]


def mutate(genome: str, mutation_rate: float) -> str:
    """
    Случайно изменяем некоторые символы.
    """
    genome_list = list(genome)
    for i in range(len(genome_list)):
        if random.random() < mutation_rate:
            genome_list[i] = random.choice(ALPHABET)
    return "".join(genome_list)


def evolve_population(
    population: List[Individual],
    target: str,
    mutation_rate: float,
    elite_size: int,
) -> List[Individual]:
    """
    Создаёт новое поколение на основе текущего.
    """
    # Сортируем по фитнесу (от лучшего к худшему)
    sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)

    # Элита: переносим лучших без изменений
    new_population: List[Individual] = sorted_pop[:elite_size]

    # Остальных создаём скрещиванием и мутацией
    while len(new_population) < len(population):
        parent1 = select_parent(sorted_pop)
        parent2 = select_parent(sorted_pop)
        child_genome = crossover(parent1, parent2)
        child_genome = mutate(child_genome, mutation_rate)
        child_fitness = calculate_fitness(child_genome, target)
        new_population.append(Individual(child_genome, child_fitness))

    return new_population


def run_evolution():
    random.seed()  # можете зафиксировать сид для воспроизводимости

    population = initialize_population(POPULATION_SIZE, TARGET)

    for generation in range(1, MAX_GENERATIONS + 1):
        # Смотрим на лучшего в текущем поколении
        best = max(population, key=lambda ind: ind.fitness)

        # Печать прогресса каждые N поколений
        if generation == 1 or generation % 50 == 0 or best.genome == TARGET:
            print(
                f"Поколение {generation:5d} | "
                f"Лучший: {best.genome!r} | "
                f"fitness={best.fitness:.4f}"
            )

        # Если достигли цели — заканчиваем
        if best.genome == TARGET:
            print("\nЦелевая фраза найдена!")
            print(best)
            break

        # Порождаем новое поколение
        population = evolve_population(
            population,
            TARGET,
            mutation_rate=MUTATION_RATE,
            elite_size=ELITE_SIZE,
        )
    else:
        print("\nДостигнут предел поколений. Лучший результат:")
        best = max(population, key=lambda ind: ind.fitness)
        print(best)


if __name__ == "__main__":
    run_evolution()

