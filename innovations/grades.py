from signup.groups import in_group, employees, students


def calculate_innovation_grade(grades):
    values_grades_pairs = [(grade.value, get_grade_weight(grade)) for grade in grades]
    sum_of_grades = sum(v * w for v, w in values_grades_pairs)
    sum_of_weights = sum(w for _, w in values_grades_pairs)
    return sum_of_grades / sum_of_weights if sum_of_weights else None


def get_grade_weight(grade):
    if in_group(grade.user, employees):
        return grade.innovation.employee_grade_weight
    elif in_group(grade.user, students):
        return grade.innovation.student_grade_weight
    else:
        return 0
