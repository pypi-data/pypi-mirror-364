from course import Course
from logger_config import logger
import os

class CourseManager:
    def __init__(self,filename = 'courses.txt'):
        self.filename = filename
        self.courses = self.load_courses()

    def load_courses(self):
        courses = {}
        try:
            
            if os.path.exists(self.filename):
                with open(self.filename,'r') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) == 3:
                            course_id = int(parts[0])
                            title = parts[1]
                            instructor = parts[2]
                            courses[course_id] = Course(course_id,title,instructor)
                logger.info(f"Loaded {len(courses)} courses.")
        except FileNotFoundError:
            logger.warning(f"No existing course file found at {self.filename}. Starting fresh.")
        return courses

    def get_next_id(self):
        if not self.courses:
            return 1
        else:
            return max(self.courses.keys()) + 1 

    def create_course(self,title,instructor):
        for course_id, course in self.courses.items():
            if course._title.lower() == title.lower():
               return print(f" Course {title.lower()} already created") 
        course_id = self.get_next_id()
        course = Course(course_id,title,instructor)
        self.courses[course_id] = course
        self.save_courses()
        logger.info(f"Created new course: ID={course_id}, Title={title}, Instructor={instructor}")
        print(f" Course {course._title} registered successfully with ID: {course_id}")

    def save_courses(self):
        with open(self.filename,'w') as f:
            for course_id, course in self.courses.items():
                line = f"{course_id},{course._title},{course._instructor}\n"
                f.write(line)
        logger.info(f"Saved {len(self.courses)} courses to file.")
                
    def list_courses(self):
        if not self.courses:
            print("No courses available.")
            return
        logger.info("Listing registered courses.")
        #for course in self.courses.values():
            #print(course)
        for course_id, course in self.courses.items():
            print(f"ID: {course_id}, Title: {course.title}, Instructor: {course.instructor}")