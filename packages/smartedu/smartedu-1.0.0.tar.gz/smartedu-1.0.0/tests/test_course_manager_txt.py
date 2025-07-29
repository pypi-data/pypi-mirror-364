import os
import unittest
from course_manager_txt import CourseManager


class TestCourseManager(unittest.TestCase):
    TEST_FILENAME = 'test_courses.txt'

    def setUp(self):
        # Clean up before each test
        if os.path.exists(self.TEST_FILENAME):
            os.remove(self.TEST_FILENAME)
        self.manager = CourseManager(filename=self.TEST_FILENAME)

    def tearDown(self):
        # Clean up after each test
        if os.path.exists(self.TEST_FILENAME):
            os.remove(self.TEST_FILENAME)

    def test_create_course(self):
        self.manager.create_course('Python Basics', 'Mr. John')
        self.assertEqual(len(self.manager.courses), 1)
        course = list(self.manager.courses.values())[0]
        self.assertEqual(course.title, 'Python Basics')
        self.assertEqual(course.instructor, 'Mr. John')

    def test_get_next_id_empty(self):
        next_id = self.manager.get_next_id()
        self.assertEqual(next_id, 1)

    def test_get_next_id_increment(self):
        self.manager.create_course('Course 1', 'Instructor A')
        self.manager.create_course('Course 2', 'Instructor B')
        next_id = self.manager.get_next_id()
        self.assertEqual(next_id, 3)

    def test_save_and_load_courses(self):
        self.manager.create_course('Data Science', 'Dr. Alice')
        # Re-create manager to reload from file
        new_manager = CourseManager(filename=self.TEST_FILENAME)
        self.assertEqual(len(new_manager.courses), 1)
        course = list(new_manager.courses.values())[0]
        self.assertEqual(course.title, 'Data Science')
        self.assertEqual(course.instructor, 'Dr. Alice')


if __name__ == '__main__':
    unittest.main()
