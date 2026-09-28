import os

import json
import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


HOST = os.getenv("API_HOST", "127.0.0.1")
PORT = int(os.getenv("API_PORT", "8000"))


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):

        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)

    def read_json(self):

        content_length = int(self.headers.get("Content-Length", 0))

        body = self.rfile.read(content_length)

        return json.loads(body.decode("utf-8"))

    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/health":
            self.send_json(200, {"status": "ok"})
            return

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            if path == "/students":

                cursor.execute(
                    "SELECT * FROM students"
                )

                students = cursor.fetchall()

                self.send_json(
                    200,
                    {
                        "students": students
                    }
                )

                return

            if path.startswith("/students/"):

                student_id = path.split("/")[-1]

                if not student_id.isdigit():
                    self.send_json(
                        400,
                        {"error": "Invalid student ID"}
                    )
                    return

                cursor.execute(
                    "SELECT * FROM students WHERE id = %s",
                    (student_id,)
                )

                student = cursor.fetchone()

                if student is None:
                    self.send_json(
                        404,
                        {"error": "Student not found"}
                    )
                    return

                self.send_json(
                    200,
                    student
                )

                return

            self.send_json(
                404,
                {"error": "Route not found"}
            )

        except Exception as e:

            self.send_json(
                500,
                {"error": str(e)}
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/students":

            self.send_json(
                404,
                {"error": "Route not found"}
            )

            return

        connection = None
        cursor = None

        try:

            data = self.read_json()

            name = data["name"]
            age = data["age"]
            department = data["department"]

            connection = get_db_connection()
            cursor = connection.cursor()

            sql = """
                INSERT INTO students
                (name, age, department)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                sql,
                (name, age, department)
            )

            connection.commit()

            student_id = cursor.lastrowid

            self.send_json(
                201,
                {
                    "message": "Student created",
                    "id": student_id
                }
            )

        except Exception as e:

            if connection:
                connection.rollback()

            self.send_json(
                500,
                {"error": str(e)}
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    def do_PUT(self):

        path = urlparse(self.path).path

        if not path.startswith("/students/"):

            self.send_json(
                404,
                {"error": "Route not found"}
            )

            return

        student_id = path.split("/")[-1]

        if not student_id.isdigit():

            self.send_json(
                400,
                {"error": "Invalid student ID"}
            )

            return

        connection = None
        cursor = None

        try:

            data = self.read_json()

            name = data["name"]
            age = data["age"]
            department = data["department"]

            connection = get_db_connection()
            cursor = connection.cursor()

            sql = """
                UPDATE students
                SET name = %s,
                    age = %s,
                    department = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (name, age, department, student_id)
            )

            connection.commit()

            if cursor.rowcount == 0:

                self.send_json(
                    404,
                    {"error": "Student not found"}
                )

                return

            self.send_json(
                200,
                {
                    "message": "Student updated",
                    "id": int(student_id)
                }
            )

        except Exception as e:

            if connection:
                connection.rollback()

            self.send_json(
                500,
                {"error": str(e)}
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    def do_DELETE(self):

        path = urlparse(self.path).path

        if not path.startswith("/students/"):

            self.send_json(
                404,
                {"error": "Route not found"}
            )

            return

        student_id = path.split("/")[-1]

        if not student_id.isdigit():

            self.send_json(
                400,
                {"error": "Invalid student ID"}
            )

            return

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM students WHERE id = %s",
                (student_id,)
            )

            connection.commit()

            if cursor.rowcount == 0:

                self.send_json(
                    404,
                    {"error": "Student not found"}
                )

                return

            self.send_json(
                200,
                {
                    "message": "Student deleted",
                    "id": int(student_id)
                }
            )

        except Exception as e:

            if connection:
                connection.rollback()

            self.send_json(
                500,
                {"error": str(e)}
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


server = HTTPServer(
    (HOST, PORT),
    APIHandler
)

print(f"API running on {HOST}:{PORT}")

server.serve_forever()
