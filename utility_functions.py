def print_unused_classrooms(timetable, rooms):
    used_rooms = {entry[1] for entry in timetable}
    unused_rooms = set(rooms) - used_rooms
    print(f"Number of unused classrooms: {len(unused_rooms)}")
    if unused_rooms:
        print("The following classrooms were not used:")
        for room in unused_rooms:
            print(room)


def check_unassigned_courses(courses, optimized_timetable):
    assigned_courses = set(entry[0] for entry in optimized_timetable)
    unassigned_courses = set(courses) - assigned_courses
    return unassigned_courses

def calculate_conflicts(timetable):
    # Using the previous logic to calculate the number of conflicts individually
    time_slot_counts = {}
    for _, _, day, hour in timetable:
        if (day, hour) not in time_slot_counts:
            time_slot_counts[(day, hour)] = 1
        else:
            time_slot_counts[(day, hour)] += 1
    conflicts = sum(count > 1 for count in time_slot_counts.values())
    return conflicts
