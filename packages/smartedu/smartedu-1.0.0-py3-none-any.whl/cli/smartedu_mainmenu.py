from cli import register_student_cli, list_students_cli
from cli import create_course_cli, list_course_cli
from cli import enroll_student_cli, list_enrollments_cli
from cli import update_grade_cli, student_report_cli, course_report_cli

import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def main_menu():
    clear_console()
    while True:
        
        print("\n--- SmartEdu Menu ---")
        print("1.Register Student")
        print("2.List Students")
        print("3.Create Course")
        print("4.List Courses")
        print("5.Enroll Student to Course")
        print("6.List Student's Enrollments")
        print("7.Update Grade")
        print("8.Generate Student Report")
        print("9.Generate Course Report")
        print("10.Exit")

        choice = input("Enter your choice:").strip()

        if choice == "1":
            clear_console()
            register_student_cli()
        elif choice == "2":
            clear_console()
            list_students_cli()
        elif choice == "3":
            clear_console()
            create_course_cli()
        elif choice == "4":
            clear_console()
            list_course_cli()
        elif choice == "5":
            clear_console()
            enroll_student_cli()
        elif choice == "6":
            clear_console()
            list_enrollments_cli()
        elif choice == "7":
            clear_console()
            update_grade_cli()
        elif choice == "8":
            clear_console()
            student_report_cli()
        elif choice == "9":
            clear_console()
            course_report_cli()
        elif choice == "10":
            clear_console()
            break
        else:
           print("Invalid option entered")
            

if __name__ == "__main__":
    main_menu()
        
