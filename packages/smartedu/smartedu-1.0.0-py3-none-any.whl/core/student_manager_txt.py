from student import Student
from logger_config import logger
import os

class StudentManager:
    def __init__(self,filename ='students.txt'):
        self.filename = filename
        self.students = self.load_students()

    def load_students(self):
        students= {}
        try:
            
            if os.path.exists(self.filename):
                with open(self.filename,'r') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) == 3:
                            student_id = int(parts[0])
                            name = parts[1].strip()
                            email = parts[2].strip()
                            students[student_id] = Student(student_id,name,email)
            logger.info(f"Loaded {len(students)} students.")
        except FileNotFoundError:
            logger.warning(f"No existing student file found at {self.filename}. Starting fresh.")
        return students

    def get_next_id(self):
        if not self.students:
            return 1
        else:
            return max(self.students.keys()) + 1 

    def register_student(self,name,email):
        for student_id, student in self.students.items():
            if student._email.lower() == email.lower():
               return print(f" Student with email id {email} already registered") 
        
        student_id = self.get_next_id()
        student = Student(student_id,name,email)
        self.students[student_id] = student
        self.save_students()
        logger.info(f"Registered student: ID={student_id}, Name={name}")
        print(f"✔ Student '{student._name}' registered successfully with ID: {student_id}")

    
    def save_students(self):
        with open(self.filename,'w') as f:
            for student_id, student in self.students.items():
                line = f"{student_id},{student._name},{student._email}\n"
                f.write(line)
        logger.info(f"Saved {len(self.students)} students to file.")

    def list_students(self):
        if not self.students:
            print("No students are registered.")
            return
            
        logger.info("Listing all students.")
        print("\nRegistered Students:")
        for student_id, student in self.students.items():
            print(f"ID: {student_id}, Name: {student._name}, Email: {student._email}")          
        
        


        
    
