import copy
import random
from utility_functions import calculate_conflicts, print_timetable, get_unused_classrooms_count




class Particle:
    def __init__(self, timetable, hours_per_course, students_per_course, room_capacities, rooms):
        self.position = copy.deepcopy(timetable)  # Deep copy to ensure independence
        self.velocity = [0 for _ in timetable]  # Initialize velocity
        self.best_position = copy.deepcopy(timetable)
        self.best_fitness = fitness(timetable, hours_per_course, students_per_course, room_capacities, rooms)
        
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

def update_velocity(particle, global_best_position, w=0.5, c1=1, c2=1, max_velocity=3):
    for i in range(len(particle.velocity)):
        cognitive_component = c1 * random.random() * (particle.best_position[i][3] - particle.position[i][3])
        social_component = c2 * random.random() * (global_best_position[i][3] - particle.position[i][3])
        velocity_change = w * particle.velocity[i] + cognitive_component + social_component
        particle.velocity[i] = max(-max_velocity, min(velocity_change, max_velocity))

def update_position(particle, weekdays_num, max_lecture_hours):
    for i in range(len(particle.position)):
        # Only update the hour
        new_hour = particle.position[i][3] + particle.velocity[i]
        new_hour = max(1, min(new_hour, max_lecture_hours))  # Ensure the new hour is within valid bounds
        particle.position[i] = (particle.position[i][0], particle.position[i][1], particle.position[i][2], new_hour)

def get_unused_classrooms_count(timetable, rooms):
    used_rooms = {entry[1] for entry in timetable}
    unused_rooms_count = len(set(rooms) - used_rooms)
    return unused_rooms_count

def pso_optimize(initial_timetable, hours_per_course, students_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours, num_particles=30, max_iterations=10000, print_frequency=100):
    particles = [Particle(initial_timetable, hours_per_course, students_per_course, room_capacities, rooms) for _ in range(num_particles)]
    global_best_position = copy.deepcopy(initial_timetable)
    # Ensure all necessary parameters are provided when calculating global best fitness
    global_best_fitness = fitness(initial_timetable, hours_per_course, students_per_course, room_capacities, rooms)

    for iteration in range(max_iterations):
        for particle in particles:
            update_velocity(particle, global_best_position)
            update_position(particle, weekdays_num, max_lecture_hours)
            current_fitness = fitness(particle.position, hours_per_course, students_per_course, room_capacities, rooms)

            if current_fitness > particle.best_fitness:
                particle.best_position = copy.deepcopy(particle.position)
                particle.best_fitness = current_fitness

            if current_fitness > global_best_fitness:
                global_best_position = copy.deepcopy(particle.position)
                global_best_fitness = current_fitness

        if iteration % print_frequency == 0 or iteration == max_iterations - 1:
            unused_rooms_count = get_unused_classrooms_count(global_best_position, rooms)
            conflicts_count = calculate_conflicts(global_best_position)
            print(f"Iteration {iteration + 1}, Conflicts: {conflicts_count}, Unused Rooms: {unused_rooms_count}")

    return global_best_position
