class Course:
    def __init__(self,course_id,title,instructor):
        self._course_id = course_id
        self._title = title
        self._instructor = instructor

    @property
    def course_id(self):
        return self._course_id

    @property
    def title(self):
        return self._title

    @property
    def instructor(self):
        return self._instructor

    def __str__(self):
        return f"{self._course_id},{self._title},({self._instructor})"
    