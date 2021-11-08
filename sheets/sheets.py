import os
import pickle
from dotenv import load_dotenv
from sheets._class import Class
from sheets.emails import Emails
from sheets.people import Parent, Student, Teacher
from cft.cft import StudTeachSheet, StudResponses, Email, Codes, TeacherData
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from typing import Union


class FormResponse:
    def __init__(
        self,
        student_first: str,
        student_last: str,
        parent1_first: str,
        parent1_last: str,
        parent1_email: str,
        choices: list,
        student_email: str = None,
        student_note: str = None,
        parent2_first: str = None,
        parent2_last: str = None,
        parent2_email: str = None,
    ):
        """
        Initializes a FormResponse object, represents an individual
            registration form submission
        Args:
            student_first (str): The first name of the student according
                to their form response
            student_last (str): The last name of the student according
                to their form response
            student_email (str): The email of the student according
                to their form response, Default: None
            student_note (str): The note of the student left during their
                form submission, Default: None
            parent1_first (str): The first name of the first parent according
                to their form response
            parent1_last (str): The last name of the first parent according
                to their form response
            parent1_email (str): The email of the first parent according
                to their form response
            parent2_first (str): The first name of the second parent according
                to their form response, Default: None
            parent2_last (str): The last name of the second parent according
                to their form response, Default: None
            parent2_email (str): The email of the second parent according
                to their form response, Default: None
            choices (list): A list of the first choice, second choice, and
                third choice class codes (class codes are of type int)
        """
        self.student_first = student_first
        self.student_last = student_last
        self.student_email = student_email
        self.student_note = student_note

        self.parent1_first = parent1_first
        self.parent1_last = parent1_last
        self.parent1_email = parent1_email

        self.parent2_first = parent2_first
        self.parent2_last = parent2_last
        self.parent2_email = parent2_email

        self.choices = choices

    def get_student(self):
        """
        Returns a Student object based on the student's first, last,
            email, and note. DOES NOT PLACE THE STUDENT ANYWHERE.
        """
        return (
            Student(
                self.student_first,
                self.student_last,
                email=self.student_email,
                note=self.student_note,
                parents=[],
                classes=[],
            ),
            self.choices,
        )

    def get_parent1(self, children=[]):
        """
        Returns a Parent object based on the first parent's first, last,
            email, and inputted children. Does not place the parent anywhere.
        """
        return Parent(
            self.parent1_first,
            self.parent1_last,
            self.parent1_email,
            children,
        )

    def get_parent2(self, children=[]):
        """
        Returns a Parent object based on the second parent's first, last,
            email, and inputted children. Does not place the parent anywhere.
        """
        return Parent(
            self.parent2_first,
            self.parent2_last,
            self.parent2_email,
            children,
        )


class Sheet:
    def __init__(
        self,
        id: str,
        name: str,
        scopes: list,
        path_to_credentials: str,
    ):
        """
        Initializes a Sheet object
        Args:
            id (str): the long alphanumerical found in the Google Sheets URL
                in between 'docs.google.com/spreadsheets/d/' and '/edit...'
            name (str): the name of the sheet (the little tabs at the bottom)
                inside your spreadsheet you want to access. For example, if you have
                an 'Email' and a 'Parent' subsheet inside your sheet, you need to
                specify which one you want to access. Ex: 'Email'
            scopes (list): a list of a link to the authorization that you want to
                give this SheetAccessor. You can find all scopes at
                https://developers.google.com/identity/protocols/oauth2/scopes.
                If you just want it to be able to read, use
                https://www.googleapis.com/auth/spreadsheets.readonly.
            path_to_credentials (str): the relative path towards the credentials.json
                file
        """
        self.id = id
        self.name = name
        self.scopes = scopes
        self.path_to_credentials = path_to_credentials

        self.creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.path_to_creds, self.scopes
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(self.creds, token)

        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

        # a very large range to make sure that we get all data
        range_name = self.name + "!A1:ZZ1000"
        result = (
            self.sheet.values().get(spreadsheetId=self.id, range=range_name).execute()
        )

        self.spreadsheet = result.get("values", [])

        # used if ever a prepareBatchWrite is used
        self.batch_write_request = {"requests": []}

    def get_column(self, index: int):
        """
        returns a List[str] of each item in the column at the given index position.
        The list is in order from top to bottom.
        Args:
            index (int): position of the column on the spreadsheet. An index of 0
                indicates the first column on the left.
        """
        result = []

        for row in self.spreadsheet:
            try:
                result.append(row[index])
            except IndexError:
                result.append(None)

        if result == [None] * len(self.spreadsheet):
            return
        else:
            return result

    def get_row(self, index: int):
        """
        returns a List[str] of each item in the row at the given index position.
        The list is in order from left to right.
        Args:
            index (int): position of the row on the spreadsheet. An index of 0
                indicates the first row at the top.
        """
        try:
            return self.spreadsheet[index]
        except IndexError:
            print(f"Index {index} not in range.")
            return None

    def write_column(self, data: list, index: int):
        """
        Writes the given data to a column at the given index position.
        Each element in the data list occupies one cell in the column.
        Data is written from top to bottom.
        Args:
            data (list): a list of strings that you want to write onto the sheet
            index (int): position of the column on the spreadsheet. An index of 0
                indicates the first column on the left.
        """
        value = {"values": [list(cell) for cell in data]}
        range_name = self.name + f"!{chr(index + 65)}{1}:{chr(index + 65)}{len(data)}"

        try:
            self.sheet.values().update(
                spreadsheetId=self.id,
                range=range_name,
                valueInputOption="RAW",
                body=value,
            ).execute()
        except HttpError:
            self.sheet.values().append(
                spreadsheetId=self.id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=value,
            ).execute()

    def write_row(self, data: list, index: int):
        """
        Writes the given data to a row at the given index position.
        Each element in the data list occupies one cell in the row.
        Data is written from left to right.
        Args:
            data (list): a list of strings that you want to write onto the sheet
            index (int): position of the row on the spreadsheet. An index of 0
                indicates the first row at the top.
        """
        value = {"values": [list(data)]}
        range_name = self.name + f"!A{index + 1}:{chr(len(data) + 64)}{index + 1}"

        try:
            self.sheet.values().update(
                spreadsheetId=self.id,
                range=range_name,
                valueInputOption="RAW",
                body=value,
            ).execute()
        except HttpError:
            self.sheet.values().append(
                spreadsheetId=self.id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=value,
            ).execute()

    def prepare_batch_write_row(self, writing_data: list, code: str):
        """
        AS OF NOW, THIS ONLY APPENDS DATA ROWS.
        If you want to do a more targeted operation,
        like writing to a specific row, just use
        write_row

        Arguments:
            writing_data: list - a 1D list to write
            code : str - the class code
        """
        for item in self.batch_write_request["requests"]:
            if item["appendCells"]["sheetId"] == int(code):
                item["appendCells"]["rows"].append(
                    {
                        "values": [
                            {"userEnteredValue": {"stringValue": str(column)}}
                            for column in writing_data
                        ]
                    }
                )
                break
        else:
            self.batch_write_request["requests"].append(
                {
                    "appendCells": {
                        "sheetId": code,
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": str(column)}}
                                    for column in writing_data
                                ]
                            }
                        ],
                        "fields": "userEnteredValue",
                    }
                }
            )

    def run_batch_update(self):
        """
        runs the prepared batch_write request
        """
        self.sheet.batchUpdate(
            spreadsheetId=self.id, body=self.batch_write_request
        ).execute()
        self.batch_write_request = {"requests": []}


class ReadOnlyError(Exception):
    pass


class SheetLike(Sheet):
    """
    A SheetLike object is an object that works just like a sheet,
    but is READONLY
    """

    def __init__(self, sheet_data):
        """
        Initializes a SheetLike object. It has all the read methods of a
        Sheet object, but is READONLY!! Attempting to call write_row or
        write_column will raise a ReadOnlyError
        Args
            sheet_data (dict) : the basic data for the sheet. It should be in
            the raw form (ie a dictionary with keys like 'range',
            'values', 'majorDimension'). This is what is returned from a single
            get request
        """
        self.spreadsheet = sheet_data.get("values", [])

    def write_row(self, data: list, index: int):
        raise ReadOnlyError

    def simulate_write_row(self, data: list, index: int):
        """
        Updtes the simulated sheet's values.
        DOES NOT UPDATE THE REMOTE SHEET'S VALUES
        """
        lst = []
        for i in range(len(self.spreadsheet[0])):
            if i < len(data):
                lst.append(data[i])
            else:
                lst.append(None)  # just in case len(data) != len(self.spreadsheet[0])
        if index < len(self.spreadsheet):
            self.spreadsheet[index] = lst
        else:
            while len(self.spreadsheet) <= index:
                self.spreadsheet.append([])
            self.spreadsheet[index] = lst

    def write_column(self, data: list, index: int):
        raise ReadOnlyError  # yeah TODO maybe implement


class SheetBatchGet:
    LARGE_RANGE = "A1:ZZ1000"
    MASTER_SHEET_NAME = "Classes"

    def __init__(
        self,
        id: str,
        names: list = [],
        scopes: list = ["https://www.googleapis.com/auth/spreadsheets.readonly"],
        path_to_credentials: str = "./data/credentials.json",
    ):
        """
        Uses batchGet to create data in self.sheet_data. This is used to get
        all the data used to instantiate SheetLike objects.
        """
        self.id = id

        ranges_provided = len(names) > 0
        if ranges_provided:
            # very large ranges to make sure we get all data
            self.names = [
                f"{code}!{SheetBatchGet.LARGE_RANGE}"
                for code in names
                if code is not None
            ]
        else:
            self.names = SheetBatchGet.LARGE_RANGE
        self.scopes = scopes
        self.path_to_credentials = path_to_credentials

        self.creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                self.creds = pickle.load(token)
        # no (valid) credentials available
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.path_to_credentials, self.scopes
                )
                self.creds = flow.run_local_server(port=0)
            # save the credentials for next run
            with open("token.pickle", "wb") as token:
                pickle.dump(self.creds, token)

        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

        extra_data = None
        if ranges_provided:
            result = (
                self.sheet.values()
                .batchGet(spreadsheetId=self.id, ranges=self.names)
                .execute()
            )
        else:
            extra_data = (
                self.sheet.values()
                .get(
                    spreadsheetId=self.id,
                    range=SheetBatchGet.MASTER_SHEET_NAME + "!" + self.names,
                )
                .execute()
            )
            all_names = SheetLike(extra_data).get_column(0)[1:]
            self.names = [code + "!" + SheetBatchGet.LARGE_RANGE for code in all_names]
            result = (
                self.sheet.values()
                .batchGet(spreadsheetId=self.id, ranges=self.names)
                .execute()
            )

        # all_data contains individual sheet data, which
        # can be accessed using the readonly SheetLike class
        # by doing `a = SheetLike((SheetBatchGet object).all_data[code])`
        all_data = result.get("valueRanges")
        self.sheet_data = {
            self.names[i].rstrip(SheetBatchGet.LARGE_RANGE).rstrip("!"): all_data[i]
            for i in range(len(self.names))
        }
        self.sheet_data["Classes"] = extra_data


class StudentRegistrationSheet(Sheet):
    def __init__(
        self,
        id: str,
        name: str,
        scopes: list,
        path_to_credentials: str,
    ):
        """
        Initializes a StudentRegistrationSheet object
        Args:
            id (str): the long alphanumerical found in the Google Sheets URL
                in between 'docs.google.com/spreadsheets/d/' and '/edit...'
            name (str): the name of the sheet (the little tabs at the bottom)
                inside your spreadsheet you want to access. For example, if you have
                an 'Email' and a 'Parent' subsheet inside your sheet, you need to
                specify which one you want to access. Ex: 'Email'
            scopes (list): a list of a link to the authorization that you want to
                give this SheetAccessor. You can find all scopes at
                https://developers.google.com/identity/protocols/oauth2/scopes.
                If you just want it to be able to read, use
                https://www.googleapis.com/auth/spreadsheets.readonly.
            path_to_credentials (str): the relative path towards the credentials.json
                file
        """
        super().__init__(id, name, scopes, path_to_credentials)

        load_dotenv()
        self.Emailer = Emails(
            Email.NOREPLY,
            os.getenv("NOREPLY_PASSWORD"),
        )

        self.responses = self.get_form_responses()
        self.students, self.parents = self.get_students_parents()

    def get_form_responses(self):
        """
        Returns a List[FormResponse] of ALL student registration form responses.
        """
        responses = []

        for i in range(1, len(self.spreadsheet)):
            row = self.spreadsheet[i]

            if len(row) == 0:
                continue

            info = [
                row[3].strip(),
                row[4].strip(),
                row[6].strip(),
                row[7].strip(),
                row[8].strip(),
                [code.strip() for code in row[25:27] if code.strip() != ""],
                row[5].strip(),
                row[23].strip(),
                row[9].strip(),
                row[10].strip(),
                row[11].strip(),
            ]

            responses.append(FormResponse(*info))

        return responses

    def get_students_parents(self):
        """
        Returns dict[str:Student] and dict[str:Parent] of ALL unique students
        and parents who registered for this class series. The keys are those
        students' and parents' UUID string.
        """
        students = {}
        parents = {}
        info_list = []

        invalid_sheet = Sheet(
            StudTeachSheet.SHEET_ID,
            "Invalid Code Emails",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )

        full_class_sheet = Sheet(
            StudTeachSheet.SHEET_ID,
            "Full Class Emails",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )

        invalid_sheet_info = list(
            zip(
                invalid_sheet.get_column(0),
                invalid_sheet.get_column(1),
                invalid_sheet.get_column(2),
                invalid_sheet.get_column(3),
            )
        )

        full_class_sheet_info = list(
            zip(
                full_class_sheet.get_column(0),
                full_class_sheet.get_column(1),
                full_class_sheet.get_column(2),
                full_class_sheet.get_column(3),
            )
        )

        all_rosters = SheetBatchGet(
            StudTeachSheet.SHEET_ID,
        )
        parent_sheet = Sheet(
            StudTeachSheet.SHEET_ID,
            "Parents",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )

        for i in range(1, len(parent_sheet.get_column(0))):
            parent = parent_sheet.get_row(i)

            if len(parent) < 3:
                continue
            elif len(parent) == 3:
                e = ""
            else:
                e = parent[3]

            parents[parent[0]] = Parent(
                parent[1].strip(),
                parent[2].strip(),
                e,
                [],
            )
            parents[parent[0]].id = parent[0]

        class_to_planned_writes = {code: 0 for code in all_rosters.sheet_data}
        for r in self.responses:
            stud_info = (
                r.student_first,
                r.student_last,
                r.parent1_first,
                r.parent1_last,
            )

            if stud_info not in info_list:
                info_list.append(stud_info)
                student, choices = r.get_student()
                student, unaccepted, invalid = self.place_student(
                    student,
                    choices,
                    stud_info,
                    all_rosters,
                    parent_sheet,
                    class_to_planned_writes,
                )
            else:
                continue

            if len(student.classes) > 0:
                students[student.id] = student

                ne = (r.parent1_first, r.parent1_last, r.parent1_email.lower())
                for parent in parents.values():
                    if (
                        parent.first,
                        parent.last,
                        parent.email,
                    ) == ne:
                        parent.children.append(student.id)
                        break
                else:
                    parent = r.get_parent1(children=[student.id])
                    parents[parent.id] = parent

                student.parents.append(parent.id)

                if r.parent2_first.strip() != "":
                    ne = (r.parent2_first, r.parent2_last, r.parent2_email.lower())
                    for parent in parents.values():
                        if (
                            parent.first,
                            parent.last,
                            parent.email,
                        ) == ne:
                            parent.children.append(student.id)
                            break
                    else:
                        parent = r.get_parent2(children=[student.id])
                        parents[parent.id] = parent

                    student.parents.append(parent.id)

            recipients = [r.parent1_email, r.parent2_email]

            length = len(invalid_sheet_info)
            for code in invalid:
                for i in range(1, length):
                    if student.full_name == invalid_sheet_info[i][0]:
                        if code == invalid_sheet_info[i][3]:
                            if (
                                invalid_sheet_info[i][1] in recipients
                                or invalid_sheet_info[i][2] in recipients
                            ):
                                break
                else:
                    self.Emailer.send_invalid_code_emails(
                        recipients,
                        student.full_name,
                        code,
                    )

                    write_info = [
                        student.full_name,
                        r.parent1_email,
                        r.parent2_email,
                        code,
                    ]

                    invalid_sheet.write_row(write_info, length)
                    invalid_sheet_info.append(tuple(write_info))
                    length += 1

            length = len(full_class_sheet_info)
            for code in unaccepted:
                for i in range(1, length):
                    if student.full_name == full_class_sheet_info[i][0]:
                        if code == full_class_sheet_info[i][3]:
                            if (
                                full_class_sheet_info[i][1] in recipients
                                or full_class_sheet_info[i][2] in recipients
                            ):
                                break
                else:
                    self.Emailer.send_class_full_emails(
                        recipients,
                        student.full_name,
                        code,
                    )

                    write_info = [
                        student.full_name,
                        r.parent1_email,
                        r.parent2_email,
                        code,
                    ]

                    full_class_sheet.write_row(write_info, length)
                    full_class_sheet_info.append(tuple(write_info))
                    length += 1

        return students, parents

    def place_student(
        self,
        student: Student,
        choices: list,
        stud_info,
        all_rosters: SheetBatchGet,
        parent_sheet: Sheet,
        offset_dict: dict,
    ):
        """
        DOES NOT ACTUALLY WRITE STUDENTS
        """
        unaccepted = []
        invalid = []
        found = False

        # this is a readonly operation, so
        # it's ok to use SheetLike objects instead
        # of many Sheet objects
        main_sheet = SheetLike(all_rosters.sheet_data["Classes"])
        for code in choices:
            if code.strip() == "":
                continue

            for c in student.classes:
                if code[:4] == c[:4]:
                    break
            else:
                try:
                    roster = SheetLike(all_rosters.sheet_data[code])
                except KeyError:
                    invalid.append(code)
                    continue

                roster_names = list(
                    zip(
                        roster.get_column(1),
                        roster.get_column(2),
                        roster.get_column(3),
                        roster.get_column(6),
                    )
                )

                # find (or don't find) the student on the existing sheet
                for i in range(1, len(roster_names)):
                    if not found:
                        if stud_info[:2] == roster_names[i][1:3]:
                            index = parent_sheet.get_column(0).index(roster_names[i][3])
                            try:
                                if stud_info[2:4] == tuple(
                                    parent_sheet.get_row(index)[1:3]
                                ):
                                    student.id = roster_names[i][0]
                                    found = True
                            except IndexError:
                                continue

                class_cap = int(
                    main_sheet.get_column(8)[main_sheet.get_column(0).index(code)]
                )
                if len(roster_names) - 1 + offset_dict[code] < class_cap and not found:
                    # if the student isn't on the sheet (not found) and there
                    # is an open space in the class
                    student.classes.append(code)
                    offset_dict[code] += 1
                elif (
                    len(roster_names) - 1 + offset_dict[code] >= class_cap and not found
                ):
                    # student isn't on the sheet, but there isn't an open slot in
                    # the class
                    unaccepted.append(code)
                elif found:
                    # the student is already on the sheet. It doesn't matter if there
                    # is available space or isn't. Just make it so that the student
                    # is on there.
                    student.classes.append(code)

        return student, unaccepted, invalid


class ClassRosterSheet(Sheet):
    def __init__(
        self,
        id: str,
        name: str,
        scopes: list,
        path_to_credentials: str,
        first_time_setup: bool = False,
    ):
        """
        Initializes a ClassRosterSheet object
        Args:
            id (str): the long alphanumerical found in the Google Sheets URL
                in between 'docs.google.com/spreadsheets/d/' and '/edit...'
            name (str): the name of the sheet (the little tabs at the bottom)
                inside your spreadsheet you want to access. For example, if you have
                an 'Email' and a 'Parent' subsheet inside your sheet, you need to
                specify which one you want to access. Ex: 'Email'
            scopes (list): a list of a link to the authorization that you want to
                give this SheetAccessor. You can find all scopes at
                https://developers.google.com/identity/protocols/oauth2/scopes.
                If you just want it to be able to read, use
                https://www.googleapis.com/auth/spreadsheets.readonly.
            path_to_credentials (str): the relative path towards the credentials.json
                file
            first_time_setup (bool): whether or not this is the first time initializing
                a ClassRosterSheet. If it is, don't do any writing or emailing.
                This is because Enoch's __init__ method will update the
                ClassRosterSheet soon. This will not only save time loading cogs
                but also prevent invalid code emails that happened because the
                classes hadn't been written yet.
        """
        super().__init__(id, name, scopes, path_to_credentials)

        if not first_time_setup:
            # the below aren't used in self.write_classes,
            # so they aren't essential and will not be done
            # on first_time_setup
            self.StudRegSheet = StudentRegistrationSheet(
                StudResponses.SHEET_ID,
                StudResponses.SHEET_NAME,
                StudResponses.SCOPES,
                StudResponses.PATH_TO_CREDS,
            )
            self.students = self.StudRegSheet.students
            self.parents = self.StudRegSheet.parents

        # the below methods are independent of a StudentRegistrationSheet
        # and are used in self.write_classes, so they are essential
        # even on first_time_setup
        self.teachers = self.get_teachers()  # dict(uuid: Teacher)
        self.classes = self.get_classes()

        if not first_time_setup:
            self.write_parents()

    def write_classes(self) -> None:
        """
        A method designed to write class/teacher data
        from the Teacher Data sheet to the Class Roster
        sheet.
        This is called in __init__.py after instantiating
        a new ClassRosterSheet
        """
        reader = Sheet(
            TeacherData.SHEET_ID,
            TeacherData.SHEET_NAME,
            TeacherData.SCOPES,
            TeacherData.PATH_TO_CREDS,
        )
        class_writer = Sheet(
            StudTeachSheet.SHEET_ID,
            "Classes",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )
        teacher_writer = Sheet(
            StudTeachSheet.SHEET_ID,
            "Teachers",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )
        # ignore the first row in all these cases
        # since the first row is just labels like "class code" or "teacher name"
        all_classes = reader.get_column(0)[1:]
        all_classes = [cls.strip() for cls in all_classes if cls is not None]
        # might not be necessary strip
        all_teach1_data = list(
            zip(
                reader.get_column(1)[1:],
                reader.get_column(3)[1:],
                reader.get_column(4)[1:],
            )
        )
        all_teach1_data = [
            (i[0].strip(), i[1].strip(), i[2].strip()) for i in all_teach1_data
        ]
        all_teach2_data = list(
            zip(
                reader.get_column(2)[1:],
                reader.get_column(5)[1:],
                reader.get_column(6)[1:],
            )
        )
        all_teach2_data = [
            (i[0].strip(), i[1].strip(), i[2].strip()) for i in all_teach2_data
        ]
        all_caps = reader.get_column(7)[1:]

        # NOTE
        # THIS DOES NOT UPDATE PRE-WRITTEN CLASSES
        # THIS IS THE PART THAT ONLY ADDS NEW CLASSES
        # (ie if the class 11111 was already on the sheet and then a new
        # teacher was added, nothing would change on the master sheet)
        unwritten_classes = set(all_classes).difference(self.classes)
        cur_teachers = []
        new_teachers = []
        code_writing_data = []
        teach_writing_data = []
        for cls in unwritten_classes:
            idx = all_classes.index(cls)

            # decide if teachers are new or already existing
            if all_teach1_data[idx] != tuple([""] * 3) and self.isNewTeacher(
                *all_teach1_data[idx]
            ):
                name_split = all_teach1_data[idx][0].split(" ")
                first, last = (" ".join(name_split[0:-1]), name_split[-1])
                temp_teach = Teacher(
                    first, last, all_teach1_data[idx][1], all_teach1_data[idx][2]
                )
                self.teachers[temp_teach.id] = temp_teach
                cur_teachers.append(temp_teach)
                new_teachers.append(temp_teach)
            else:
                cur_teachers.append(self.getMatchingTeacher(*all_teach1_data[idx]))
            if all_teach2_data[idx] != tuple([""] * 3) and self.isNewTeacher(
                *all_teach2_data[idx]
            ):
                name_split = all_teach2_data[idx][0].split(" ")
                first, last = (" ".join(name_split[0:-1]), name_split[-1])
                temp_teach = Teacher(
                    first, last, all_teach2_data[idx][1], all_teach2_data[idx][2]
                )
                self.teachers[temp_teach.id] = temp_teach
                cur_teachers.append(temp_teach)
                new_teachers.append(temp_teach)
            else:
                cur_teachers.append(self.getMatchingTeacher(*all_teach2_data[idx]))

            # get stuff to write
            course_type = Codes.COURSES[cls[0]]
            course_level = Codes.LEVELS[cls[1]]
            course_days = Codes.DAYS[cls[2]]
            course_times = Codes.TIMES[cls[3]]
            teach1_uuid, teach2_uuid = "", ""
            teach1_uuid = cur_teachers[0].id
            if cur_teachers[1] is not None:
                teach2_uuid = cur_teachers[1].id

            # add the content to the content to write
            code_writing_data.append(
                [
                    cls,  # class code
                    course_type,  # ie "java", "python", etc
                    course_level,
                    course_days,
                    course_times,
                    teach1_uuid,
                    teach2_uuid,
                    "",  # "meeting location" - not given
                    all_caps[idx],
                ]
            )

            # if new teacher(s) was/were added, update teacher sheet
            # since the for loop won't execute if len(new_teachers)==0
            for i in range(len(new_teachers)):
                teach_writing_data.append(
                    [
                        new_teachers[i].id,
                        new_teachers[i].first,
                        new_teachers[i].last,
                        new_teachers[i].email,
                        new_teachers[i].phone,
                    ],
                )

            # reset lists for next iter
            new_teachers = []
            cur_teachers = []

        info = class_writer.sheet.get(
            spreadsheetId=StudTeachSheet.SHEET_ID,
            ranges=["Classes", "Teachers"],
            includeGridData=False,
        ).execute()

        self.batchWrite(
            code_writing_data,
            info["sheets"][0]["properties"]["sheetId"],
            class_writer,
            StudTeachSheet.SHEET_ID,
        )
        self.batchWrite(
            teach_writing_data,
            info["sheets"][1]["properties"]["sheetId"],
            teacher_writer,
            StudTeachSheet.SHEET_ID,
        )
        # use batchUpdate to add new (sub)sheets for each new
        # class code
        self.add_sheets(unwritten_classes, all_classes, all_caps, class_writer)

    def batchWrite(
        self,
        writing_data: list,
        subsheet_id: int,
        writer: Sheet,
        spreadsheetId: str,
    ):
        batch_write_request = {
            "requests": [
                {
                    "appendCells": {
                        "sheetId": subsheet_id,
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": str(column)}}
                                    for column in row
                                ]
                            }
                            for row in writing_data
                        ],
                        "fields": "userEnteredValue",
                    }
                }
            ]
        }
        writer.sheet.batchUpdate(
            spreadsheetId=spreadsheetId, body=batch_write_request
        ).execute()

    def add_sheets(
        self,
        unwritten_classes: set,
        all_classes: list,
        all_caps: list,
        class_writer: Sheet,
    ) -> None:
        """
        Method to create new sheets.
        Errors out w/ HTTP Error if the requested sheets already exist.
        Also, creates the formatted header for the sheet
        """
        if len(unwritten_classes) == 0:
            # don't bother making requests if there are none to be made
            return
        add_requests = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": all_classes[all_classes.index(cls)],
                            # this sheetId refers merely to an id for the sheet
                            "sheetId": all_classes[all_classes.index(cls)],
                            "gridProperties": {
                                "rowCount": int(all_caps[all_classes.index(cls)]) + 1,
                                "columnCount": 26,
                            },
                        }
                    }
                }
                for cls in unwritten_classes
            ]
        }
        class_writer.sheet.batchUpdate(
            spreadsheetId=StudTeachSheet.SHEET_ID, body=add_requests
        ).execute()

        # make headers for each new sheet
        data = [
            "#",
            "UUID",
            "First Name",
            "Last Name",
            "Email",
            "Note",
            "Parent 1 UUID",
            "Parent 2 UUID",
        ]
        header_requests = {
            "requests": [
                {
                    "updateCells": {
                        "start": {
                            "sheetId": all_classes[all_classes.index(cls)],
                            "rowIndex": 0,
                            "columnIndex": 0,
                        },
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": str(thing)}}
                                    for thing in data
                                ]
                            }
                        ],
                        "fields": "userEnteredValue",
                    }
                }
                for cls in unwritten_classes
            ]
        }
        class_writer.sheet.batchUpdate(
            spreadsheetId=StudTeachSheet.SHEET_ID, body=header_requests
        ).execute()

        # format the new headers (green bg, bold black text)
        format_requests = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": all_classes[all_classes.index(cls)],
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 8,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                # rgb(52, 245, 197)
                                "backgroundColor": {
                                    "red": 52 / 255,
                                    "green": 245 / 255,
                                    "blue": 197 / 255,
                                },
                                "horizontalAlignment": "LEFT",
                                "textFormat": {
                                    "foregroundColor": {
                                        "red": 0.0,
                                        "green": 0.0,
                                        "blue": 0.0,
                                    },
                                    "bold": True,
                                },
                            }
                        },
                        "fields": str(
                            "userEnteredFormat(backgroundColor,textFormat,"
                            + "horizontalAlignment)"
                        ),
                    }
                }
                for cls in unwritten_classes
            ]
        }
        class_writer.sheet.batchUpdate(
            spreadsheetId=StudTeachSheet.SHEET_ID, body=format_requests
        ).execute()

        print("created new subsheets for the following class codes", unwritten_classes)

    def isNewTeacher(self, full_name: str, email: str, phone: str) -> bool:
        for teacher in self.teachers.values():
            if (
                teacher.full_name.lower() == full_name.lower()
                and teacher.email == email
                and teacher.phone == phone
            ):
                # old teacher if the full name, email, phone match
                return False
        return True  # new teacher if none of the (names, emails, phones) matched

    def getMatchingTeacher(
        self, full_name: str, email: str, phone: str
    ) -> Union[Teacher, None]:
        for teacher in self.teachers.values():
            if (
                teacher.full_name.lower() == full_name.lower()
                and teacher.email == email
                and teacher.phone == phone
            ):
                return teacher
        return None

    def write_placements(self):
        all_data = SheetBatchGet(StudTeachSheet.SHEET_ID)
        all_rosters = {
            code: SheetLike(all_data.sheet_data[code]) for code in all_data.sheet_data
        }
        writer = Sheet(
            StudTeachSheet.SHEET_ID,
            StudTeachSheet.SHEET_NAME,
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )

        for student in self.students.values():
            for code in student.classes:
                if student.id not in self.classes[code].students:
                    """roster = Sheet(
                        StudTeachSheet.SHEET_ID,
                        code,
                        StudTeachSheet.SCOPES,
                        StudTeachSheet.PATH_TO_CREDS,
                    )"""
                    roster = all_rosters[code]

                    stud_info = [
                        0,
                        student.id,
                        student.first,
                        student.last,
                        student.email,
                        student.note,
                        student.parents[0],
                    ]

                    if len(student.parents) == 2:
                        stud_info.append(student.parents[1])

                    self.classes[code].students.append(student.id)

                    uuids = roster.get_column(1)
                    for i in range(1, len(uuids)):
                        stud_info[0] = i
                        if uuids[i] is None:
                            roster.simulate_write_row(stud_info, i)
                            writer_roster = Sheet(
                                StudTeachSheet.SHEET_ID,
                                code,
                                StudTeachSheet.SCOPES,
                                StudTeachSheet.PATH_TO_CREDS,
                            )
                            writer_roster.write_row(stud_info, i)
                            break
                    else:
                        i = len(self.classes[code].students)
                        stud_info[0] = i
                        roster.simulate_write_row(stud_info, i)
                        writer.prepare_batch_write_row(stud_info, code)

                    recipients = []
                    for p_id in student.parents:
                        recipients.append(self.parents[p_id].email)

                    self.StudRegSheet.Emailer.send_welcome_emails(
                        recipients,
                        student.full_name,
                        code,
                    )

        # if the batch is empty, just don't bother with it
        if len(writer.batch_write_request["requests"]) != 0:
            writer.run_batch_update()

    def write_parents(self):
        roster = Sheet(
            StudTeachSheet.SHEET_ID,
            "Parents",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )
        uuids = roster.get_column(0)
        length = len(uuids)

        for parent in self.parents.values():
            if parent.id not in uuids:
                parent_info = [
                    parent.id,
                    parent.first,
                    parent.last,
                    parent.email,
                ]

                roster.write_row(parent_info, length)
                length += 1

    def get_teachers(self):
        teachers = {}
        teacher_list = Sheet(
            StudTeachSheet.SHEET_ID,
            "Teachers",
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )

        for i in range(1, len(teacher_list.get_column(0))):
            row = teacher_list.get_row(i)

            if len(row) < 5:
                continue

            teachers[row[0]] = Teacher(row[1], row[2], row[3], row[4], [])
            teachers[row[0]].id = row[0]

        return teachers

    def get_classes(self):
        classes = {}

        # only make 1 read request instead of making
        # many individual requests
        all_rosters = SheetBatchGet(
            StudTeachSheet.SHEET_ID,
            self.get_column(0)[1:],
            StudTeachSheet.SCOPES,
            StudTeachSheet.PATH_TO_CREDS,
        )

        for i in range(1, len(self.get_column(0))):
            row = self.get_row(i)

            if len(row) < 9 or row[0] == "":
                continue

            code = row[0]
            classes[code] = Class(code, row[7], [row[5]], [], int(row[8]))
            self.teachers[row[5]].classes.append(code)

            if row[6].strip() != "":
                classes[code].teachers.append(row[6])
                self.teachers[row[6]].classes.append(code)

            # READONLY roster
            roster = SheetLike(all_rosters.sheet_data[code])

            for i in range(1, len(roster.get_column(1))):
                classes[code].students.append(roster.get_column(1)[i])

        return classes
