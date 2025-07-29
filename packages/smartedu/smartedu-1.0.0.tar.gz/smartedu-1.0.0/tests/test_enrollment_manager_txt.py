import os
import unittest
from enrollment_manager_txt import EnrollmentManager


class TestEnrollmentManager(unittest.TestCase):
    TEST_STUDENT_FILE = 'test_students.txt'
    TEST_COURSE_FILE = 'test_courses.txt'
    TEST_ENROLLMENT_FILE = 'test_enrollments.txt'

    def setUp(self):
        # Setup dummy student file
        with open(self.TEST_STUDENT_FILE, 'w') as f:
            f.write('1,John Doe,john@example.com\n')
            f.write('2,Jane Smith,jane@example.com\n')

        # Setup dummy course file
        with open(self.TEST_COURSE_FILE, 'w') as f:
            f.write('1,Python Basics,Mr. John\n')
            f.write('2,Data Science,Ms. Alice\n')

        # Remove any previous enrollments
        if os.path.exists(self.TEST_ENROLLMENT_FILE):
            os.remove(self.TEST_ENROLLMENT_FILE)

        self.manager = EnrollmentManager(
            student_file=self.TEST_STUDENT_FILE,
            course_file=self.TEST_COURSE_FILE,
            enrollment_file=self.TEST_ENROLLMENT_FILE
        )

    def tearDown(self):
        # Clean up files after each test
        for file in [self.TEST_STUDENT_FILE, self.TEST_COURSE_FILE, self.TEST_ENROLLMENT_FILE]:
            if os.path.exists(file):
                os.remove(file)

    def test_enroll_student_success(self):
        self.manager.enroll_student(1, 1)
        self.assertIn(1, self.manager.enrollments)
        self.assertIn(1, self.manager.enrollments[1])

    def test_enroll_student_nonexistent_student(self):
        self.manager.enroll_student(99, 1)  # Student ID 99 doesn't exist
        self.assertNotIn(99, self.manager.enrollments)

    def test_enroll_student_nonexistent_course(self):
        self.manager.enroll_student(1, 99)  # Course ID 99 doesn't exist
        self.assertNotIn(99, self.manager.enrollments.get(1, set()))

    def test_enroll_duplicate(self):
        self.manager.enroll_student(1, 1)
        self.manager.enroll_student(1, 1)  # Should not duplicate
        self.assertEqual(len(self.manager.enrollments[1]), 1)

    def test_save_and_load_enrollments(self):
        self.manager.enroll_student(1, 2)
        # Re-load to ensure data is saved and loaded correctly
        new_manager = EnrollmentManager(
            student_file=self.TEST_STUDENT_FILE,
            course_file=self.TEST_COURSE_FILE,
            enrollment_file=self.TEST_ENROLLMENT_FILE
        )
        self.assertIn(1, new_manager.enrollments)
        self.assertIn(2, new_manager.enrollments[1])


if __name__ == '__main__':
    unittest.main()
