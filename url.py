from type import CourseType, SemesterType

LEARN_PREFIX = r'https://learn.tsinghua.edu.cn'
REGISTRAR_PREFIX = r'https://zhjw.cic.tsinghua.edu.cn'
MAX_SIZE = 200

ID_LOGIN = r'https://id.tsinghua.edu.cn/do/off/ui/auth/login/post/bb5df85216504820be7bba2b0ae1535b/0?/login.do'


def LEARN_AUTH_ROAM(ticket: str):
    return rf'{LEARN_PREFIX}/b/j_spring_security_thauth_roaming_entry?ticket={ticket}'


LEARN_LOGOUT = rf'{LEARN_PREFIX}/f/j_spring_security_logout'
LEARN_STUDENT_COURSE_LIST_PAGE = rf'{LEARN_PREFIX}/f/wlxt/index/course/student/'
LEARN_SEMESTER_LIST = rf'{LEARN_PREFIX}/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq'
LEARN_CURRENT_SEMESTER = rf'{LEARN_PREFIX}/b/kc/zhjw_v_code_xnxq/getCurrentAndNextSemester'


def LEARN_COURSE_LIST(semester: str, courseType: CourseType):
    if courseType == CourseType.STUDENT:
        return rf'{LEARN_PREFIX}/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{semester}'
    else:
        return rf'{LEARN_PREFIX}/b/kc/v_wlkc_kcb/queryAsorCoCourseList/{semester}/0'


def LEARN_COURSE_URL(courseID: str, courseType: CourseType):
    return rf'{LEARN_PREFIX}/f/wlxt/index/course/{courseType}/course?wlkcid={courseID}'


def LEARN_COURSE_TIME_LOCATION(courseID: str):
    return rf'{LEARN_PREFIX}/b/kc/v_wlkc_xk_sjddb/detail?id={courseID}'


def LEARN_TEACHER_COURSE_URL(courseID: str):
    return rf'{LEARN_PREFIX}/f/wlxt/index/course/teacher/course?wlkcid={courseID}'


def LEARN_FILE_LIST(courseID: str, courseType: CourseType):
    if courseType == CourseType.STUDENT:
        return rf'{LEARN_PREFIX}/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent?wlkcid={courseID}&size={MAX_SIZE}'
    else:
        return rf'{LEARN_PREFIX}/b/wlxt/kj/v_kjxxb_wjwjb/teacher/queryByWlkcid?wlkcid={courseID}&size={MAX_SIZE}'


def LEARN_NOTIFICATION_LIST(courseID: str, courseType: CourseType):
    if courseType == CourseType.STUDENT:
        return rf'{LEARN_PREFIX}/b/wlxt/kcgg/wlkc_ggb/student/kcggListXs?wlkcid={courseID}&size={MAX_SIZE}'
    else:
        return rf'{LEARN_PREFIX}/b/wlxt/kcgg/wlkc_ggb/teacher/kcggList?wlkcid={courseID}&size={MAX_SIZE}'


def LEARN_HOMEWORK_LIST_NEW(courseID: str):
    return rf'{LEARN_PREFIX}/b/wlxt/kczy/zy/student/index/zyListWj?wlkcid={courseID}&size={MAX_SIZE}'


def LEARN_HOMEWORK_LIST_SUBMITTED(courseID: str):
    return rf'{LEARN_PREFIX}/b/wlxt/kczy/zy/student/index/zyListYjwg?wlkcid={courseID}&size={MAX_SIZE}'


def LEARN_HOMEWORK_LIST_GRADED(courseID: str):
    return rf'{LEARN_PREFIX}/b/wlxt/kczy/zy/student/index/zyListYpg?wlkcid={courseID}&size={MAX_SIZE}'


def LEARN_HOMEWORK_LIST_SOURCE(courseID: str):
    return [
        {'url': LEARN_HOMEWORK_LIST_NEW(courseID),
         'status': {
             'submitted': False,
             'graded': False,
         }},
        {'url': LEARN_HOMEWORK_LIST_SUBMITTED(courseID),
         'status': {
             'submitted': True,
             'graded': False,
         }},
        {'url': LEARN_HOMEWORK_LIST_GRADED(courseID),
         'status': {
             'submitted': True,
             'graded': True,
         }},
    ]

