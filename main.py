import time

import requests
from requests import session
import urllib.request
import json
from bs4 import BeautifulSoup
from loguru import logger
import re
from datetime import datetime
from type import CourseType, SemesterType, CourseInfo, HomeworkStatus, Homework
import url
import configs

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}


def parseSemesterType(n: int):
    if n == 1:
        return SemesterType.FALL
    elif n == 2:
        return SemesterType.SPRING
    elif n == 3:
        return SemesterType.SUMMER
    else:
        return SemesterType.UNKNOWN


class Learn2018Helper:
    def __init__(self, username: str, password: str):
        """
        :param username: INFO username
        :param password: INFO password
        """
        self.username = username
        self.password = password
        self.csrfToken = None
        self.session = session()
        self.session.headers = HEADERS

    def login(self):
        """
        Login functions for THU Learning Web
        :return: -1: ERROR_FETCH_FROM_ID
                 -2: BAD_CREDENTIALS
                 -3: ERROR_ROAMING
                 -4: INVALID_RESPONSE
                 0 : SUCCESS_CSRF_TOKEN
        """
        credential = {'i_user': self.username, 'i_pass': self.password, 'atOnce': 'true'}
        ticketResponse = self.session.post(url.ID_LOGIN, credential)
        if not ticketResponse.ok:
            return -1
        body = BeautifulSoup(ticketResponse.text, 'lxml')
        targetURL = body.a['href']
        ticket = targetURL.split('=')[-1]
        logger.info(f'Ticket = {ticket}')
        if ticket == 'BAD_CREDENTIALS':
            return -2
        loginURL = url.LEARN_AUTH_ROAM(ticket)
        logger.info(f'Auth = {loginURL}')
        loginResponse = self.session.get(loginURL)
        if not loginResponse.ok:
            return -3
        courseListPageSource = self.session.get(url.LEARN_STUDENT_COURSE_LIST_PAGE)
        logger.info(f'Course List = {courseListPageSource.status_code}')
        tokenRegex = r'.*&_csrf=(\S*)".*'
        matches = re.findall(tokenRegex, courseListPageSource.text)
        if len(matches) == 0:
            return -4
        self.csrfToken = matches[1]
        logger.info(f'csrfToken = {self.csrfToken}')
        return 0

    def logout(self):
        logoutResponse = self.session.post(url.LEARN_LOGOUT)
        logger.info(f'Logout = {logoutResponse.status_code}')

    def fetchWithToken(self, url):
        if self.csrfToken is None:
            self.login()
        url_with_token = ''
        if '?' in url:
            url_with_token += (url + f'&_csrf={self.csrfToken}')
        else:
            url_with_token += (url + f'?_csrf={self.csrfToken}')
        return self.session.get(url_with_token)

    def getCurrentSemester(self):
        """
        Get current semester information
        :return: -1: INVALID_RESPONSE.
                 {Dict} : SUCCESS_GET_CURRENT_SEMESTER.
                    return a dictionary containing current semester's information
        """
        json_obj = self.fetchWithToken(url.LEARN_CURRENT_SEMESTER).json()
        if json_obj['message'] != 'success':
            return -1
        result = json_obj['result']
        return {
            'id': result['id'],
            'startDate': datetime.strptime(result['kssj'], "%Y-%m-%d").date(),
            'endDate': datetime.strptime(result['jssj'], "%Y-%m-%d").date(),
            'startYear': int(result['xnxq'][0:4]),
            'endYear': int(result['xnxq'][5:9]),
            'type': parseSemesterType(int(result['xnxq'][10:11]))
        }

    def getCourseList(self, semesterID: str, courseType: CourseType = CourseType.STUDENT):
        """
        Get specific semester's course list
        :param semesterID: semesterID returned by getCurrentSemester() method
        :param courseType: CourseType.STUDENT or CourseType.TEACHER.
        :return: -1: INVALID_RESPONSE.
                 courses : SUCCESS_GET_COURSE_LIST.
                    return a list containing all course information in specific semester
        """
        json_obj = self.fetchWithToken(url.LEARN_COURSE_LIST(semesterID, courseType)).json()
        if json_obj['message'] != 'success' or not isinstance(json_obj['resultList'], list):
            return -1
        result = json_obj['resultList'] if len(json_obj['resultList']) > 0 else []
        courses = []
        for c in result:
            courses.append(CourseInfo(
                c_id=c['wlkcid'],
                name=c['kcm'],
                englishName=c['ywkcm'],
                timeAndLocation=self.fetchWithToken(url.LEARN_COURSE_TIME_LOCATION(c['wlkcid'])).json(),
                url=url.LEARN_COURSE_URL(c['wlkcid'], courseType),
                teacherName=c['jsm'] if c['jsm'] is not None else '',
                teacherNumber=c['jsh'],
                courseNumber=c['kch'],
                courseIndex=int(c['kxh']),
                courseType=courseType
            ))
        return courses

    def getHomeworkListAtURL(self, homeworkURL: str, status: HomeworkStatus):
        """
        Get Homework list by specific URL (there are three URL for three types homeworks: Not submitted, Submitted, Graded)
        :param homeworkURL: homework URL provided by getHomeworkList() method
        :param status: A HomeworkStatus class object, containing submitted and graded information of sigle homework
        :return: -1: INVALID_RESPONSE
                 homeworks: SUCCESS_GET_HOMEWORK_LIST_URL
                    return a list containing all homework under input URL
        """
        logger.info(rf'Get Homework list at URL. URL = {homeworkURL}')
        json_obj = self.fetchWithToken(homeworkURL).json()
        if json_obj['result'] != 'success':
            return -1
        result = json_obj['object']['aaData'] if json_obj['object']['aaData'] is not None else []
        homeworks = [Homework(c_id=h['zyid'], studentHomeworkID=h['xszyid'], title=h['bt'],
                              deadline=datetime.strptime(h['jzsjStr'], '%Y-%m-%d %H:%M'), status=status)
                     for h in result]
        return homeworks

    def getHomeworkList(self, courseID: str, courseType: CourseType = CourseType.STUDENT):
        """
        Get all homework in specific course
        :param courseID: courseID returned by getCourseList() method
        :param courseType: CourseType.STUDENT or CourseType.TEACHER.
        :return: -1: NOT_IMPLEMENTED_ERROR
                 allHomework : SUCCESS_GET_HOMEWORK_LIST
        """
        if courseType == CourseType.TEACHER:
            return -1
        allHomework = []
        alLHomeworkURL = url.LEARN_HOMEWORK_LIST_SOURCE(courseID)
        for homeworkURL in alLHomeworkURL:
            status = HomeworkStatus(submitted=homeworkURL['status']['submitted'],
                                    graded=homeworkURL['status']['graded'])
            allHomework += self.getHomeworkListAtURL(homeworkURL['url'], status)

        return allHomework


if __name__ == '__main__':
    helper = Learn2018Helper(configs.USERNAME, configs.PASSWORD)
    helper.login()
    currentSemester = helper.getCurrentSemester()
    logger.info(f'Current Semester = {currentSemester}')
    courses = helper.getCourseList(currentSemester['id'])
    logger.info(f'Course List = {courses}')
    homeworkList = helper.getHomeworkList('2019-2020-2140259642')
    logger.info(f'Home work list = {homeworkList}')
    helper.logout()
