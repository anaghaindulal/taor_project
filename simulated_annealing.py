import random
import math

from utility_functions import calculate_conflicts, get_unused_classrooms_count

random.seed(43)

def generate_sample(courses, hours_per_course, students_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours):
    timetable = []
    for course in courses:
        hours_needed = hours_per_course[course]
        for _ in range(hours_needed):
            found_slot = False
            random.shuffle(rooms)  # Add randomness
            for room in rooms:
                if room_capacities[room] >= students_per_course[course]:  # Check capacity constraints
                    for day in range(1, weekdays_num + 1):
                        for hour in range(1, max_lecture_hours + 1):
                            if not any((entry[1], entry[2], entry[3]) == (room, day, hour) for entry in timetable):
                                timetable.append((course, room, day, hour))
                                found_slot = True
                                break
                        if found_slot:
                            break
                if found_slot:
                    break
            if not found_slot:
                print(f"Unable to find a suitable classroom and time for course {course}.")
    return timetable


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



# Mutation function, randomly changes the time or classroom of a course
def mutate(timetable, courses, hours_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours):
    course_to_mutate = random.choice(list(courses))
    mutated_timetable = [entry for entry in timetable if entry[0] != course_to_mutate]

    for _ in range(hours_per_course[course_to_mutate]):
        found_slot = False
        random.shuffle(rooms)
        for room in rooms:
            if room_capacities[room] >= students_per_course[course_to_mutate]:
                for day in range(1, weekdays_num + 1):
                    for hour in range(1, max_lecture_hours + 1):
                        if not any((entry[1], entry[2], entry[3]) == (room, day, hour) for entry in mutated_timetable):
                            mutated_timetable.append((course_to_mutate, room, day, hour))
                            found_slot = True
                            break
                    if found_slot:
                        break
            if found_slot:
                break
        if not found_slot:
            print(f"Unable to find a suitable classroom and time for course {course_to_mutate} during mutation.")
    
    return mutated_timetable

# Simulated annealing process
# Parameter adjustment during the simulated annealing process

def simulated_annealing(timetable, hours_per_course, students_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours, max_iterations=100000):
    initial_temp = 10000000
    final_temp = 0.0001
    alpha = 0.92
    current_temp = initial_temp

    current_solution = timetable
    current_fitness = fitness(current_solution, hours_per_course, students_per_course, room_capacities, rooms)
    best_solution = current_solution
    best_fitness = current_fitness

    iteration = 0
    while current_temp > final_temp and iteration < max_iterations:
        new_solution = mutate(current_solution, courses, hours_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours)
        new_fitness = fitness(new_solution, hours_per_course, students_per_course, room_capacities, rooms)

        if new_fitness > current_fitness or random.random() < math.exp((new_fitness - current_fitness) / current_temp):
            current_solution = new_solution
            current_fitness = new_fitness
            if current_fitness > best_fitness:
                best_solution = current_solution
                best_fitness = current_fitness

        current_temp *= alpha
        iteration += 1  # Update iteration count

        # Separately calculate the number of unused classrooms
        unused_rooms_count = get_unused_classrooms_count(best_solution, rooms)
        # Directly calculate the number of conflicts
        conflicts = calculate_conflicts(best_solution)
        print(f"Iteration: {iteration}, Current best solution conflicts: {conflicts}, Unused classrooms count: {unused_rooms_count}")
    
    return best_solution
