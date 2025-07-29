import os
import unittest
from grade_manager_txt import GradeManager
from enrollment_manager_txt import EnrollmentManager


class TestGradeManager(unittest.TestCase):
    TEST_STUDENT_FILE = 'test_students.txt'
    TEST_COURSE_FILE = 'test_courses.txt'
    TEST_ENROLLMENT_FILE = 'test_enrollments.txt'
    TEST_GRADE_FILE = 'test_grades.txt'

    def setUp(self):
        # Prepare dummy student file
        with open(self.TEST_STUDENT_FILE, 'w') as f:
            f.write('1,John Doe,john@example.com\n')
            f.write('2,Jane Smith,jane@example.com\n')

        # Prepare dummy course file
        with open(self.TEST_COURSE_FILE, 'w') as f:
            f.write('1,Python Basics,Mr. John\n')
            f.write('2,Data Science,Ms. Alice\n')

        # Prepare dummy enrollments
        with open(self.TEST_ENROLLMENT_FILE, 'w') as f:
            f.write('1,1\n')
            f.write('1,2\n')
            f.write('2,1\n')

        # Clean up any previous grades file
        if os.path.exists(self.TEST_GRADE_FILE):
            os.remove(self.TEST_GRADE_FILE)

        self.manager = GradeManager(
            enrollment_file=self.TEST_ENROLLMENT_FILE,
            grade_file=self.TEST_GRADE_FILE
        )

    def tearDown(self):
        # Clean up all files
        for file in [self.TEST_STUDENT_FILE, self.TEST_COURSE_FILE,
                     self.TEST_ENROLLMENT_FILE, self.TEST_GRADE_FILE]:
            if os.path.exists(file):
                os.remove(file)

    def test_update_grade_success(self):
        self.manager.update_grade(1, 1, 'A')
        self.assertEqual(self.manager.grades[(1, 1)], 'A')

    def test_update_grade_for_non_enrolled_student(self):
        self.manager.update_grade(2, 2, 'B')  # Student 2 is not in course 2
        self.assertNotIn((2, 2), self.manager.grades)

    def test_persistence_of_grades(self):
        self.manager.update_grade(1, 1, 'A')
        self.manager.update_grade(1, 2, 'B+')
        # Reload manager to verify persistence
        new_manager = GradeManager(
            enrollment_file=self.TEST_ENROLLMENT_FILE,
            grade_file=self.TEST_GRADE_FILE
        )
        self.assertEqual(new_manager.grades[(1, 1)], 'A')
        self.assertEqual(new_manager.grades[(1, 2)], 'B+')

    def test_generate_student_report(self):
        self.manager.update_grade(1, 1, 'A')
        self.manager.update_grade(1, 2, 'B+')
        try:
            self.manager.generate_student_report(1)
        except Exception as e:
            self.fail(f"generate_student_report raised an exception unexpectedly: {e}")

    def test_generate_course_report(self):
        self.manager.update_grade(1, 1, 'A')
        self.manager.update_grade(2, 1, 'B')
        try:
            self.manager.generate_course_report(1)
        except Exception as e:
            self.fail(f"generate_course_report raised an exception unexpectedly: {e}")


if __name__ == '__main__':
    unittest.main()
