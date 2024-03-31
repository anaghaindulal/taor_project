import copy
import random
from utility_functions import calculate_conflicts, get_unused_classrooms_count
import matplotlib.pyplot as plt
# Assuming previously defined functions and variables are still valid

def fitness(timetable, hours_per_course, students_per_course, room_capacities, rooms):
    conflicts = 0
    time_slot_counts = {}
    used_rooms = set()
    
    for course, room, day, hour in timetable:
        # Track used classrooms
        used_rooms.add(room)

        # Count time slot conflicts
        if (day, hour) not in time_slot_counts:
            time_slot_counts[(day, hour)] = 1
        else:
            time_slot_counts[(day, hour)] += 1

    conflicts = sum(count > 1 for count in time_slot_counts.values())
    
    # Calculate the number of unused classrooms
    unused_rooms = len(set(rooms) - used_rooms)
    
    # Add a small penalty for each unused classroom, choose a very small weight (e.g., 0.01) to ensure the main focus is on the number of conflicts
    room_penalty = 0.01 * unused_rooms
    
    # Fitness is primarily determined by the number of conflicts, while also considering the number of unused classrooms
    return -conflicts - room_penalty
    
def calculate_fitness(timetable, hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours):
    conflict_score = -fitness(timetable, hours_per_course, students_per_course, room_capacities, rooms)
    unused_rooms_count = get_unused_classrooms_count(timetable, rooms)
    # Increase the penalty weight for the number of conflicts
    return conflict_score - 0.1 * unused_rooms_count - 5 * conflict_score

class Individual:
    def __init__(self, timetable, hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours):
        self.timetable = timetable
        self.max_lecture_hours = max_lecture_hours
        self.hours_per_course = hours_per_course
        self.students_per_course = students_per_course
        self.room_capacities = room_capacities
        self.rooms = rooms
        # Call calculate_fitness using all necessary parameters
        self.fitness = calculate_fitness(timetable, hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours)

# Tournament selection
def tournament_selection(population, k=3):
    selected = random.sample(population, k)
    selected.sort(key=lambda x: x.fitness, reverse=True)
    return selected[0]

# Roulette wheel selection
def roulette_wheel_selection(population):
    # Calculate the minimum fitness
    min_fitness = min(individual.fitness for individual in population)
    # If the minimum fitness is negative, adjust all fitness values to be positive
    adjust_fitness = 0
    if min_fitness < 0:
        adjust_fitness = -min_fitness
    max = sum(individual.fitness + adjust_fitness for individual in population)
    pick = random.uniform(0, max)
    current = 0
    for individual in population:
        current += individual.fitness + adjust_fitness
        if current > pick:
            return individual
    return population[0]  # As a fallback, return the first individual in the population

def crossover(parent1, parent2, crossover_rate=0.85):
    if random.random() < crossover_rate:
        crossover_point = random.randint(1, len(parent1.timetable) - 2)
        child_timetable1 = parent1.timetable[:crossover_point] + parent2.timetable[crossover_point:]
        child_timetable2 = parent2.timetable[:crossover_point] + parent1.timetable[crossover_point:]
        return (
            Individual(child_timetable1, parent1.hours_per_course, parent1.students_per_course, parent1.room_capacities, parent1.rooms, parent1.max_lecture_hours),
            Individual(child_timetable2, parent2.hours_per_course, parent2.students_per_course, parent2.room_capacities, parent2.rooms, parent2.max_lecture_hours)
        )
    return parent1, parent2

def mutate(individual, mutation_rate=0.05):
    if random.random() < mutation_rate:
        mutate_index = random.randint(0, len(individual.timetable) - 1)
        course, room, day, hour = individual.timetable[mutate_index]
        mutated_hour = random.randint(1, individual.max_lecture_hours)
        individual.timetable[mutate_index] = (course, room, day, mutated_hour)
        individual.fitness = calculate_fitness(individual.timetable, individual.hours_per_course, individual.students_per_course, individual.room_capacities, individual.rooms, individual.max_lecture_hours)

# def genetic_algorithm_optimize(initial_timetable, hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours, population_size=1000, generations=200):
#     population = [
#         Individual(copy.deepcopy(initial_timetable), hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours)
#         for _ in range(population_size)
#     ]
#     for generation in range(generations):
#         new_population = []

#         while len(new_population) < population_size:
#             parent1 = tournament_selection(population)
#             parent2 = roulette_wheel_selection(population)
#             child1, child2 = crossover(parent1, parent2)
#             mutate(child1)
#             mutate(child2)
#             new_population.extend([child1, child2])

#         population = new_population[:population_size]
#         population.sort(key=lambda x: x.fitness, reverse=True)

#         # At the end of each generation, print the number of unused classrooms and conflicts
#         best_solution = population[0].timetable
#         conflicts = calculate_conflicts(best_solution)
#         unused_rooms_count = get_unused_classrooms_count(best_solution, rooms)
#         print(f"Generation {generation + 1}: Conflicts = {conflicts}, Unused Classrooms = {unused_rooms_count}")

#     return population[0].timetable

def genetic_algorithm_optimize(initial_timetable, hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours, population_size=1000, generations=200):
    population = [
        Individual(copy.deepcopy(initial_timetable), hours_per_course, students_per_course, room_capacities, rooms, max_lecture_hours)
        for _ in range(population_size)
    ]
    
    # 初始化存储历史数据的列表
    conflicts_history = []
    unused_rooms_history = []

    for generation in range(generations):
        new_population = []

        while len(new_population) < population_size:
            parent1 = tournament_selection(population)
            parent2 = roulette_wheel_selection(population)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1)
            mutate(child2)
            new_population.extend([child1, child2])

        population = new_population[:population_size]
        population.sort(key=lambda x: x.fitness, reverse=True)

        best_solution = population[0].timetable
        conflicts = calculate_conflicts(best_solution)
        unused_rooms_count = get_unused_classrooms_count(best_solution, rooms)
        
        # 更新历史数据
        conflicts_history.append(conflicts)
        unused_rooms_history.append(unused_rooms_count)

        # print(f"Generation {generation + 1}: Conflicts = {conflicts}, Unused Classrooms = {unused_rooms_count}")

    # 绘图
    plt.figure(figsize=(10, 5))
    plt.plot(conflicts_history, label='Conflicts')
    plt.plot(unused_rooms_history, label='Unused Rooms')
    plt.xlabel('Generation')
    plt.ylabel('Count')
    plt.title('Genetic Algorithm Optimization Process')
    plt.legend()
    plt.grid(True)
    plt.show()

    return population[0].timetable
