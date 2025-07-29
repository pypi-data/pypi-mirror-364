import os
from enrollment_manager_txt import EnrollmentManager
from logger_config import logger


class GradeManager:
    def __init__(self, enrollment_file='enrollments.txt', grade_file='grades.txt'):
        self.enrollment_manager = EnrollmentManager(enrollment_file=enrollment_file)
        self.grade_file = grade_file
        self.grades = self.load_grades()

    def load_grades(self):
        grades = {}
        try:
            if os.path.exists(self.grade_file):
                with open(self.grade_file, 'r') as f:
                    for line in f:
                        student_id, course_id, grade = line.strip().split(',')
                        grades[(int(student_id), int(course_id))] = grade.strip()
                logger.info(f"Loaded {len(grades)} grades.")
        except FileNotFoundError:
            logger.warning(f"No existing grades file found at {self.grade_file}. Starting fresh.")
        return grades

    def save_grades(self):
        with open(self.grade_file, 'w') as f:
            for (student_id, course_id), grade in self.grades.items():
                f.write(f"{student_id},{course_id},{grade}\n")
        logger.info(f"Saved {len(self.grades)} grades to file.")

    def update_grade(self, student_id, course_id, grade):
        if student_id not in self.enrollment_manager.enrollments:
            logger.warning(f"Grade update failed: Student {student_id} is not enrolled.")
            print(f"Student {student_id} is not enrolled in any course.")
            return

        if course_id not in self.enrollment_manager.enrollments[student_id]:
            logger.warning(f"Grade update failed: Course {course_id} is not enrolled for Student {student_id}.")
            print(f"Student {student_id} is not enrolled in course {course_id}.")
            return

        self.grades[(student_id, course_id)] = grade.strip().upper()
        self.save_grades()
        print(f"Grade {grade} updated for Student {student_id} in Course {course_id}.")

    def generate_student_report(self, student_id):
        logger.info(f"Generating performance report for Student ID {student_id}.")
        print(f"\nPerformance Report for Student ID: {student_id}")
        for (s_id, c_id), grade in self.grades.items():
            if s_id == student_id:
                course = self.enrollment_manager.course_manager.courses.get(c_id)
                if course:
                    print(f"{course.title} (Instructor: {course.instructor}): Grade {grade}")
        print()

    def generate_course_report(self, course_id):
        logger.info(f"Generating performance report for Course ID {course_id}.")
        print(f"\nPerformance Report for Course ID: {course_id}")
        for (s_id, c_id), grade in self.grades.items():
            if c_id == course_id:
                student = self.enrollment_manager.student_manager.students.get(s_id)
                if student:
                    print(f"{student._name} ({student._email}): Grade {grade}")
        print()
