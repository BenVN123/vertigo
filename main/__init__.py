from socket import timeout

from cft.cft import StudTeachSheet

from sheets.sheets import ClassRosterSheet
from datetime import datetime


class SheetsManager:
    def update_setup_class_sheet(self):
        """
        Retrieves data from Student Responses and tries to pair
        the students with the teachers by writing the students
        and their respective info onto their requested courses.
        """
        print("updating and writing to class sheet")
        try:
            start_t = datetime.now()

            original_sheet = ClassRosterSheet(
                StudTeachSheet.SHEET_ID,
                StudTeachSheet.SHEET_NAME,
                StudTeachSheet.SCOPES,
                StudTeachSheet.PATH_TO_CREDS,
                first_time_setup=True,
            )
            original_sheet.write_classes()

            updated_sheet = ClassRosterSheet(
                StudTeachSheet.SHEET_ID,
                StudTeachSheet.SHEET_NAME,
                StudTeachSheet.SCOPES,
                StudTeachSheet.PATH_TO_CREDS,
            )
            updated_sheet.write_placements()

            print(
                f"finished doing so in {(datetime.now() - start_t).total_seconds()}"
                + " seconds."
            )
        except timeout:
            print("socket.timeout exception caught")
        except IndexError as e:
            print("Someone was editing the sheet while enoch was")
            print("trying to fetch values (Student Teacher Sheet).")
            raise e
        except Exception as e:
            print("uh oh, something went seriously wrong.")
            print(type(e), e)
            raise e  # can be commented out


SheetsManager = SheetsManager()
