class Email:
    NOREPLY = "noreply@code4tomorrow.org"


class StudTeachSheet:
    """
    Represents data used to access the Google Sheet which contains
    class, student, teacher, and parent information
    If modifying the scopes, delete the file token.pickle
    """

    # stuff in the Google Sheet URL between d/ and /edit
    SHEET_ID = "1k_Q44jvBg1C6zUOJs20c7wo8We3quiGHOsWScpS3piI"

    # name of the tab on the bottom of the spreadsheet you want to use
    SHEET_NAME = "Classes"

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # file path to credentials.json file
    PATH_TO_CREDS = "./data/credentials.json"


class StudResponses:
    """
    This is the sheet with the data of student responses to the
    scheduling form
    """

    SHEET_ID = "1g3fW7F8NO4JIFuKn9lFSJz44wzoNIbgabJNZer51SP4"

    SHEET_NAME = "Form Responses 1"

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    PATH_TO_CREDS = "./data/credentials.json"


class TeacherData:
    """
    This is the sheet with the data about teachers
    """

    # this is the test one. TODO: when deploying, change
    # to the actual sheet
    SHEET_ID = "14WLgEBD4nGP5z7L804obj55Q3eyWR8thKkvZSkIscuY"

    SHEET_NAME = "Sheet1"

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    PATH_TO_CREDS = "./data/credentials.json"


class Codes:
    # See https://code4tomorrow.org/class-codes
    COURSES = {
        "1": "Java",
        "2": "Python",
        "3": "Scratch",
        "4": "Web Development",
        "5": "Machine Learning",
        "6": "JavaScript",
        "7": "C",
        "8": "iOS App Development",
    }

    LEVELS = {"1": "Beginner", "2": "Intermediate", "3": "Advanced", "4": "Games"}

    DAYS = {
        "1": "Mon & Wed",
        "2": "Tue & Thur",
        "3": "Wed & Sat",
        "4": "Thur & Sun",
    }

    TIMES = {
        "1": "12-1 PM Pacific Time",
        "2": "2-3 PM Pacific Time",
        "3": "3-4 PM Pacific Time",
        "4": "4-5 PM Pacific Time",
        "5": "5-6 PM Pacific Time",
        "6": "6-7 PM Pacific Time",
        "7": "7-8 PM Pacific Time",
        "8": "8-9 PM Pacific Time",
        "9": "9-10 PM Pacific Time",
    }
