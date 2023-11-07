import serial
import psycopg2
import dotenv

ser = serial.Serial(
    "/dev/ttyACM6", 115200 
)


def db_cursor() -> psycopg2.extensions.cursor:
    username = dotenv.get_key(".env", "DB_USER")
    password = dotenv.get_key(".env", "DB_PASS")
    host = dotenv.get_key(".env", "DB_HOST")
    port = dotenv.get_key(".env", "DB_PORT")
    database = dotenv.get_key(".env", "DB_NAME")
    db = psycopg2.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=database
    )
    cursor = db.cursor()
    return cursor


def main():
    if ser.is_open:
        print("Serial is open")
        cur = db_cursor()
        cur.execute("SELECT students.first_name, students.middle_name, students.last_name, rfid_credentials.hashed_lrn FROM students INNER JOIN rfid_credentials ON students.lrn = rfid_credentials.lrn")
        write_complete: bool = False
        for row in cur.fetchall():
            first_name = row[0]
            middle_name = row[1]
            last_name = row[2]
            hashed_lrn: str = row[3]
            print("\n-------------------")
            print("Writing the data of %s %s %s with an RFID hash of %s" % (first_name, middle_name, last_name, hashed_lrn))
            if write_complete:
                ser.write(hashed_lrn.encode("utf-8"))
                print("Put your card.")
            while True:
                data = ser.read(ser.inWaiting())
                if data != b'':
                    data_str = str(data)
                    if "another write" in data_str:
                        print("Write Complete!")
                        write_complete = True
                        break
                    elif "Waiting" in data_str:
                        print("Device now ready!")
                        ser.write(hashed_lrn.encode("utf-8"))
                        print("\nData sent!\n")
                    elif "Put" in data_str:
                        print("Put his/her card on the scanner to write his/her data..")

if __name__ == "__main__":
    main()
