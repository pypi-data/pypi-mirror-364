import os
from student_manager_txt import StudentManager
from course_manager_txt import CourseManager
from logger_config import logger

class EnrollmentManager:
    def __init__(self,student_file = 'students.txt',course_file='courses.txt',enrollment_file='enrollments.txt'):
        self.student_manager = StudentManager(student_file)
        self.course_manager = CourseManager(course_file)
        self.enrollment_file = enrollment_file
        self.enrollments = self.load_enrollments()

    def load_enrollments(self):
        enrollments = {}
        try:
            
            if os.path.exists(self.enrollment_file):
                with open(self.enrollment_file,'r') as f:
                    for line in f:
                        student_id,course_id = map(int,line.strip().split(','))
                        enrollments.setdefault(student_id, set()).add(course_id)
                logger.info(f"Loaded enrollments for {len(enrollments)} students.")
        except FileNotFoundError:
            logger.warning(f"No existing enrollment file found at {self.enrollment_file}. Starting fresh.")
        return enrollments

    def enroll_student(self,student_id,course_id):
        if student_id not in self.student_manager.students:
            logger.warning(f"Enrollment failed: Student ID {student_id} does not exist.")
            print(f"Student with ID {student_id} not registered")
            return
        if course_id not in self.course_manager.courses:
            logger.warning(f"Enrollment failed: Course ID {course_id} does not exist.")
            print(f"No Course with ID {course_id}")
            return

        self.enrollments.setdefault(student_id,set())
        if course_id in self.enrollments[student_id]:
            print(f"Student {student_id} is already enrolled in course {course_id}")
            return
        self.enrollments[student_id].add(course_id)
        self.save_enrollments()
        logger.info(f"Enrolled Student ID {student_id} to Course ID {course_id}.")
        print(f"Student {student_id} successfully enrolled in course {course_id}")

    def save_enrollments(self):
        with open(self.enrollment_file, 'w') as f:
            for student_id, course_ids in self.enrollments.items():
                for course_id in course_ids:
                    f.write(f"{student_id},{course_id}\n")
        logger.info(f"Saved enrollments for {len(self.enrollments)} students.")

    def list_enrollments_for_student(self,student_id):
        if student_id not in self.student_manager.students:
            print(f"Student with ID {student_id} is not registered")
            return
            
        course_ids = self.enrollments.get(student_id, set())
        if not course_ids:
            print(f"Student {student_id} is not enrolled in any courses.")
            return

        logger.info("Listing student enrollments.")    
        print(f"Student {student_id} enrolled in:")
        for course_id in course_ids:
            course = self.course_manager.courses.get(course_id)
            if course:
                print(f" - {course.title} (Instructor: {course.instructor})")