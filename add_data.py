import os
import asyncio
import json
import random
import dotenv
import requests
import pandas as pd
from websockets.client import connect

dotenv.load_dotenv(".env")

class DoubleQuoteDictionary(dict):
    def __str__(self):
        return json.dumps(self)


HOST: str = "roundhouse.proxy.rlwy.net"
PORT: int = 42552
# HOST: str = "localhost"
# PORT: int = 8080

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
        

async def send_data(student_data) -> bool:
    """
    Sends student data to the specified API endpoint.
    
    Args:
        student_data (dict): A dictionary containing the student data to be sent.
        
    Returns:
        None: This function does not return anything.
    """
    session: requests.Session = requests.Session()
    data = session.post(f"http://{HOST}:{PORT}/v1/student/create", json=student_data, auth=("teacher", 1234))
    if data.status_code == 200:
        return True
    else:
        return False
        
        
async def generate_random(val1, val2) -> int:
    return random.randint(val1, val2)


async def main():
    """
    This function is the main entry point of the program.
    It reads data from an Excel file and sends the data to an API.
    
    Parameters:
    None
    
    Return:
    None
    """
    clear()
    # section_id = 1 # Section ID of Casimiro Del Reosario
    # grade_level = 11 # Grade 11
    data_set = pd.read_excel("Students.xlsx")
    ws = await connect(f"ws://esp32:1234@{HOST}:{PORT}/websocket/student")
    for _, row in data_set.iterrows():
        section_id = await generate_random(260, 282)
        while 266 < section_id < 272:
            section_id = await generate_random(260, 282)
        grade_level = await generate_random(11, 12)
        last_name = row["LAST NAME"].title()
        first_name = row["FIRST NAME"].title()
        middle_initial = None if isinstance(row["MIDDLE INITIAL"], float) else row["MIDDLE INITIAL"]
        lrn = row["LRN"]
        guardian_name = row["GUARDIAN NAME"].title()
        guardian_contact = row["CONTACT NUMBER OF GUARDIAN"]
        address = row["ADDRESS"].title()
        sex = row["SEX"].capitalize()
        birthdate = str(row["BIRTH DATE(YYYY-MM-DD)"])
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
        
        await ws.send(str(json.dumps(request_data)))
        print(f"\n{first_name} {middle_initial} {last_name}, {lrn} \n{await ws.recv()}")
        

if __name__ == "__main__":
    asyncio.run(main())
