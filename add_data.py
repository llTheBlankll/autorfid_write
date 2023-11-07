import os
import json
import dotenv
import requests
import pandas as pd

dotenv.load_dotenv(".env")

class doublequote_dictionary(dict):
    def __str__(self):
        return json.dumps(self)


# HOST: str = "roundhouse.proxy.rlwy.net"
HOST: str = "roundhouse.proxy.rlwy.net"
PORT: int = 42552


def clear():
    """
    Clears the console screen.

    Clears the console screen by executing the appropriate command based on the 
    operating system. If the operating system is Windows, the command 'cls' is 
    executed. Otherwise, the command 'clear' is executed.

    Parameters:
        None

    Returns:
        None
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
        

def send_data(student_data) -> None:
    """
    Sends student data to the specified API endpoint.
    
    Args:
        student_data (dict): A dictionary containing the student data to be sent.
        
    Returns:
        None: This function does not return anything.
    """
    session: requests.Session = requests.Session()
    data = session.post(f"http://{HOST}:{PORT}/api/v1/student/create", json=student_data, auth=("teacher", 1234))
    if data.status_code == 200:
        print("Request Success!")
    else:
        print("Request Failed!")
        print("Status Code: %s" % data.status_code)


def main():
    """
    This function is the main entry point of the program.
    It reads data from an Excel file and sends the data to an API.
    
    Parameters:
    None
    
    Return:
    None
    """
    clear()
    section_id = 1 # Section ID of Casimiro Del Reosario
    grade_level = 11 # Grade 11
    data_set = pd.read_excel("id_info.xlsx")
    for index, row in data_set.iterrows():
        last_name = row["LAST NAME"].title()
        first_name = row["FIRST NAME"].title()
        middle_initial = None if isinstance(row["MIDDLE INITIAL"], float) else row["MIDDLE INITIAL"]
        lrn = row["LRN"]
        guardian_name = row["GUARDIAN NAME"].title()
        guardian_contact = row["CONTACT NUMBER OF GUARDIAN"]
        address = row["ADDRESS"].title()
        sex = row["SEX"].capitalize()
        birthdate = str(row["BIRTH DATE(YYYY-MM-DD)"].date())
        request_data: dict = {
            "lrn": lrn,
            "firstName": first_name,
            "middleName": middle_initial,
            "lastName": last_name,
            "birthdate": birthdate,
            "studentGradeLevel": {
                "id": grade_level
            },
            "sex": sex,
            "studentSection": {
                "sectionId": section_id 
            },
            "guardian": [
                {
                    "fullName": guardian_name,
                    "contactNumber": guardian_contact 
                }
            ],
            "address": address
        }
        print("Sending the data of %s %s %s..." % (first_name, middle_initial, last_name))
        print("Birthdate: %s" % birthdate)
        send_data(doublequote_dictionary(request_data))


if __name__ == "__main__":
    main()
