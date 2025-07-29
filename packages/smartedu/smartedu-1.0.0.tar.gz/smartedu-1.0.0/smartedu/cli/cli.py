from student_manager_txt import StudentManager
from course_manager_txt import CourseManager
from enrollment_manager_txt import EnrollmentManager
from grade_manager_txt import GradeManager
from inputvalidators import validate_non_empty, validate_email, validate_int

def register_student_cli():
    try:
        name = validate_non_empty(input("Enter student name:"), "Name")
        email = validate_email(input("Enter student email:"))
    except ValueError as e:
        print(f"✖ Error: {e}")
        return
    
    manager = StudentManager()
    manager.register_student(name,email)
    
def list_students_cli():
    manager = StudentManager()
    manager.list_students()
    
def create_course_cli():
    try:
        title = validate_non_empty(input("Enter course name:"), "Course Title")
        instructor = validate_non_empty(input("Enter instructor name:"), "Instructor")
    except ValueError as e:
        print(f"✖ Error: {e}")
        return   

    manager = CourseManager()
    manager.create_course(title,instructor)

def list_course_cli():
    manager = CourseManager()
    manager.list_courses()

def enroll_student_cli():
    try:
        student_id = validate_int(input("Enter Student ID to enroll: "), "Student ID")
        course_id = validate_int(input("Enter Course ID to enroll: "), "Course ID")
        
    except ValueError as e:
        print(f"✖ Error: {e}")
        return

    manager = EnrollmentManager()
    manager.enroll_student(student_id, course_id)

def list_enrollments_cli():
    try:
        student_id = validate_int(input("Enter Student ID to view enrollments: "), "Student ID")
    except ValueError as e:
        print(f"✖ Error: {e}")
        return

    manager = EnrollmentManager()
    manager.list_enrollments_for_student(student_id)

def update_grade_cli():
    try:
        student_id = validate_int(input("Enter Student ID: "), "Student ID")
        course_id = validate_int(input("Enter Course ID: "), "Course ID")
        grade = validate_non_empty(input("Enter Grade (e.g., A, B+): "), "Grade")
    except ValueError as e:
        print(f"✖ Error: {e}")
        return
    manager = GradeManager()
    manager.update_grade(student_id, course_id, grade)


def student_report_cli():
    try:
        student_id = validate_int(input("Enter Student ID to view report: "), "Student ID")
    except ValueError as e:
        print(f"✖ Error: {e}")
        return

    manager = GradeManager()
    manager.generate_student_report(student_id)

def course_report_cli():
    try:
        course_id = validate_int(input("Enter Course ID to view report: "), "Course ID")
    except ValueError as e:
        print(f"✖ Error: {e}")
        return

    manager = GradeManager()
    manager.generate_course_report(course_id)

    