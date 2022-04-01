import datetime
from enum import Enum


class SemesterType(Enum):
    FALL = '秋季学期'
    SPRING = '春季学期'
    SUMMER = '夏季学期'
    UNKNOWN = '未知学期'


class CourseType(Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'


class CourseInfo:
    def __init__(self, c_id: str, name: str, englishName: str, timeAndLocation: [str], url: str, teacherName: str,
                 teacherNumber: str, courseNumber: str, courseIndex: int, courseType: CourseType):
        self.courseType = courseType
        self.courseIndex = courseIndex
        self.courseNumber = courseNumber
        self.teacherNumber = teacherNumber
        self.teacherName = teacherName
        self.url = url
        self.timeAndLocation = timeAndLocation
        self.englishName = englishName
        self.name = name
        self.id = c_id

    def __repr__(self):
        return rf'CourseINFO: ID = {self.id}, Name = {self.name}'


class HomeworkStatus:
    def __init__(self, submitted: bool, graded: bool):
        self.graded = graded
        self.submitted = submitted

    def __repr__(self):
        if self.submitted and self.graded:
            return r'HomeworkStatus: Graded'
        elif self.submitted:
            return r'HomeworkStatus: Ungraded'
        else:
            return r'HomeworkStatus: Not submitted'


class Homework:
    def __init__(self, c_id: str, studentHomeworkID: str, title: str, deadline: datetime.date, status: HomeworkStatus):
        self.status = status
        self.deadline = deadline
        self.title = title
        self.studentHomeworkID = studentHomeworkID
        self.c_id = c_id
        # 这里没有严格按照thu-learn-lib进行实现，因为功能上大概率无需其他属性。

    def __repr__(self):
        return f'Homework: Title = {self.title}, Deadline = {self.deadline}, Status = {self.status}'
