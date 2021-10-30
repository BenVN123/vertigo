from cft.cft import Codes


class Class:
    CLASS_CAP = 15  # max number of students per default class

    def __init__(
        self,
        code: str,
        location: str,
        teachers: list = [],
        students: list = [],
        class_cap: int = -1,
    ):
        """
        Initializes a Class object
        Args:
            code (int): 5 digit unique class code
            location (str): meeting link or voice channel name
            teachers (list, optional): list of this class's Teacher objects.
                Defaults to [].
            students (list, optional): list of this class's Student objects.
                Defaults to [].
        Raises:
            ValueError: If there are more than 2 teachers in this class
            ClassFullException: If the number of students exceeds the class cap
        """
        if class_cap == -1:
            class_cap = Class.CLASS_CAP  # if class cap isn't provided, assume 15

        # if it is, then the provided class_cap is the cap.
        self.CLASS_CAP = class_cap

        self.code = code

        # set course, level, days, time, and session based on the class code
        # TODO assume PR #38 is merged
        code = str(self.code)

        self.course = Codes.COURSES[code[0]]
        self.level = Codes.LEVELS[code[1]]
        self.days = Codes.DAYS[code[2]]
        self.time = Codes.TIMES[code[3]]
        self.session = int(code[4])

        self.location = location

        self.set_teachers(teachers)
        self.set_students(students)

    def set_teachers(self, teachers: list):
        if len(teachers) > 2:
            raise ValueError(
                "A Class cannot have more than 2 teachers.\n"
                f"\tTeachers list: {teachers}\n"
            )

        self.teachers = teachers

    def set_students(self, students: list):
        if len(students) > self.CLASS_CAP:
            raise ClassFullException(self.code)

        self.students = students

    def equals_ignore_session(self, class_obj):
        """
        Returns True if the first 4 digits of the given Class object is
        equal to the first 4 digits of this Class's class code.
        Args:
            class_obj (Class): another Class object to compare to this Class object
        Returns:
            bool: True if the 2 class codes are the same ignoring the session number
        """
        return self.code_equals_ignore_session(class_obj.code, self.code)

    def code_equals_ignore_session(self, code: int):
        """
        Returns True if the first 4 digits of the given class code is
        equal to the first 4 digits of this Class's class code.
        This is a convenience function and a helper function for
        equals_ignore_session.
        Args:
            code (int): 5 digit unique class code
        Returns:
            bool: True if the 2 class codes are the same ignoring the session number
        """
        return str(code)[:4] == str(self.code)[:4]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Class):
            return o.code == self.code
        else:
            return False

    def __ne__(self, o: object) -> bool:
        if isinstance(o, Class):
            return o.code != self.code
        else:
            return True

    def __lt__(self, o: object) -> bool:
        if isinstance(o, Class):
            return self.code < o.code
        else:
            return False

    def __gt__(self, o: object) -> bool:
        if isinstance(o, Class):
            return self.code > o.code
        else:
            return False

    def __le__(self, o: object) -> bool:
        if isinstance(o, Class):
            return self.code <= o.code
        else:
            return False

    def __ge__(self, o: object) -> bool:
        if isinstance(o, Class):
            return self.code >= o.code
        else:
            return False


class ClassFullException(Exception):
    def __init__(
        self, code: int, max_studs: int = Class.CLASS_CAP, message="Class is full"
    ):
        self.code = code
        self.message = message
        self.max_studs = max_studs
        super().__init__(self.message)

    def __str__(self) -> str:
        return (
            f"Class {self.code} is full. Max # of students "
            f"per class is {self.max_studs}"
        )
