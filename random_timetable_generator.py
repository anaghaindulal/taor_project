import random

def generate_random_timetable(courses, hours_per_course, students_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours):
    timetable = []
    assigned_courses = set()  # Used to track the courses that have been allocated

    for course in courses:
        if course in assigned_courses:
            # If the course has already been allocated, skip it
            continue

        hours_needed = hours_per_course[course]
        suitable_rooms = [room for room in rooms if room_capacities.get(room, 0) >= students_per_course.get(course, 0)]
        
        for _ in range(hours_needed):
            room = random.choice(suitable_rooms)
            day = random.randint(1, weekdays_num)
            hour = random.randint(1, max_lecture_hours)
            # Ensure the current time slot is not occupied
            while any((existing_course[1], existing_course[2], existing_course[3]) == (room, day, hour) for existing_course in timetable):
                day = random.randint(1, weekdays_num)
                hour = random.randint(1, max_lecture_hours)
            timetable.append((course, room, day, hour))
        
        assigned_courses.add(course)  # Mark the current course as allocated

    return timetable

# Generate initial population
initial_population = [
    generate_random_timetable(courses, hours_per_course, students_per_course, room_capacities, rooms, weekdays_num, max_lecture_hours)
    for _ in range(10)
]
