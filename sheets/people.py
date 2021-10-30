from uuid import uuid4


class Person:
    def __init__(self, first: str, last: str, email: str = None):
        """
        Initializes a Person object
        Args:
            first (str): person's first name
            last (str): person's last name
            email (str, optional): person's email. Defaults to None.
        """
        self.first = first.strip()
        self.last = last.strip()
        self.full_name = self.first + " " + self.last

        if email is not None:
            self.email = email.strip().lower()
        else:
            self.email = email

        # Generates a random (v4) universally unique identifier
        self.id = str(uuid4())

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Person):
            return o.id == self.id
        else:
            return False

    def __ne__(self, o: object) -> bool:
        if isinstance(o, Person):
            return o.id != self.id
        else:
            return False

    def __str__(self) -> str:
        return f"Full name: {self.full_name}, Email: {self.email}, UUID: {self.id}"


class Student(Person):
    MAX_ENROLLMENTS = 3

    def __init__(
        self,
        first: str,
        last: str,
        email: str = None,
        note: str = None,
        parents: list = [],
        classes: list = [],
    ):
        """
        Initializes a Student object
        Args:
            first (str): student's first name
            last (str): student's last name
            email (str, optional): student's email. Defaults to None.
            note (str, optional): extra info on the student. Defaults to None.
            parents (list, optional): list of the student's parents' UUIDs.
                Defaults to an empty list.
            classes (list, optional): list of the student's class codes.
                Defaults to an empty list.
        """
        super().__init__(first, last, email)

        self.note = note
        self.set_parents(parents)
        self.set_classes(classes)

    def set_parents(self, parents: list):
        """
        Sets this student's parents attribute
        Args:
            parents (list): list of the student's parents' UUIDs
        Raises:
            ValueError: If the student has more than 2 parents
        """
        if len(parents) > 2:
            raise ValueError(
                "A Student cannot have more than 2 parents.\n"
                f"\tParent list: {parents}\n"
                f"\tStudent: {self}\n"
            )

        self.parents = parents

    def set_classes(self, classes: list):
        """
        Sets this student's the classes attribute
        Args:
            classes (list): list of this student's class codes
        Raises:
            ValueError: If the student is enrolled in more than MAX_ENROLLMENTS classes
        """
        if len(classes) > Student.MAX_ENROLLMENTS:
            raise ValueError(
                f"A Student cannot have more than {Student.MAX_ENROLLMENTS} classes.\n"
                f"\tStudent: {self}"
            )

        self.classes = classes


class Parent(Person):
    def __init__(self, first: str, last: str, email: str, children: list = []):
        """
        Initializes a Parent object
        Args:
            first (str): parent's first name
            last (str): parent's last name
            email (str): parent's email
            children (list, optional): list of student string UUIDs for each child
        """
        super().__init__(first, last, email)

        self.children = children


class Teacher(Person):
    MAX_CLASSES = 3

    def __init__(
        self,
        first: str,
        last: str,
        email: str,
        phone: str,
        classes: list = [],
    ):
        """
        Initializes a Teacher object
        Args:
            first (str): teacher's first name
            last (str): teacher's last name
            email (str): teacher's email
            phone (str): teacher's phone number
            classes (list, optional): class codes this teacher is teaching
        """
        super().__init__(first, last, email)

        self.phone = phone
        self.set_classes(classes)

    def set_classes(self, classes: list):
        """
        Sets this teacher's classes attribute
        Args:
            classes (list): list of this teacher's class codes
        Raises:
            ValueError: If the teacher is teaching more than MAX_CLASSES classes
        """
        if len(classes) > Teacher.MAX_CLASSES:
            raise ValueError(
                f"A Teacher cannot have more than {Teacher.MAX_CLASSES} classes.\n"
                f"\tClasses list: {classes}\n"
                f"\tTeacher: {self}\n"
            )

        self.classes = classes


class Member(Person):
    def __init__(
        self,
        first: str,
        last: str,
        email: str,
        phone: str,
        departments: list = [str],
        projects: list = [str],
    ):
        """
        Initializes a Parent object
        Args:
            first (str): member's first name
            last (str): member's last name
            email (str): member's email
            departments (list[str]): list of this member's departments
            projects (list[str]): list of this member's projects
        """
        super().__init__(first, last, email)

        self.phone = phone
        self.departments = departments
        self.projects = projects


class Ambassador(Person):
    def __init__(
        self,
        first: str,
        last: str,
        email: str,
        pronouns: str,
    ):
        self.pronouns = pronouns
