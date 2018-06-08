def calculate_innovation_grade(grades, student_grade_weight, employee_grade_weight):
    aggregate_grade = 0
    number_of_votes = len(grades)
    print(number_of_votes)
    if number_of_votes > 0:
        for grade in grades:
            aggregate_grade += get_user_grade(grade,  student_grade_weight, employee_grade_weight)
        return aggregate_grade/number_of_votes
    else:
        return None


def get_user_grade(grade, student_grade_weight, employee_grade_weight):
    if grade.user.groups.filter(name='students'):
        return float(student_grade_weight * grade.value)
    elif grade.user.groups.filter(name='committee_members'):
        return float(employee_grade_weight * grade.value)
    else:
        raise ValueError('Grade given by user without privileges')
