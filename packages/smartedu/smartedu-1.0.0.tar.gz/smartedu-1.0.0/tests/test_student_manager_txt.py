import os
import unittest
from student_manager_txt import StudentManager


class TestStudentManager(unittest.TestCase):
    TEST_FILENAME = 'test_students.txt'

    def setUp(self):
        # Before each test, ensure test file is empty
        if os.path.exists(self.TEST_FILENAME):
            os.remove(self.TEST_FILENAME)
        self.manager = StudentManager(filename=self.TEST_FILENAME)

    def tearDown(self):
        # After each test, remove the test file
        if os.path.exists(self.TEST_FILENAME):
            os.remove(self.TEST_FILENAME)

    def test_register_student(self):
        self.manager.register_student('John Doe', 'john@example.com')
        self.assertEqual(len(self.manager.students), 1)
        student = list(self.manager.students.values())[0]
        self.assertEqual(student._name, 'John Doe')
        self.assertEqual(student._email, 'john@example.com')

    def test_get_next_id_empty(self):
        next_id = self.manager.get_next_id()
        self.assertEqual(next_id, 1)

    def test_get_next_id_increment(self):
        self.manager.register_student('A', 'a@example.com')
        self.manager.register_student('B', 'b@example.com')
        next_id = self.manager.get_next_id()
        self.assertEqual(next_id, 3)

    def test_save_and_load_students(self):
        self.manager.register_student('Alice', 'alice@example.com')
        # Create a fresh manager to force reloading from file
        new_manager = StudentManager(filename=self.TEST_FILENAME)
        self.assertEqual(len(new_manager.students), 1)
        student = list(new_manager.students.values())[0]
        self.assertEqual(student._name, 'Alice')
        self.assertEqual(student._email, 'alice@example.com')


if __name__ == '__main__':
    unittest.main()
