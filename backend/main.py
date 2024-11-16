from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>Use the /api endpoint</p>"


# MySQL connection configuration
mysql_config = {
    'host': '<endpoint>',
    'user': 'admin',
    'password': '<password>',
    'database': 'sample',
}

# Function to create a MySQL connection
def create_connection():
    return mysql.connector.connect(**mysql_config)

# Read endpoint to get all employees
@app.route('/api/vi/transcript', methods=['GET'])
def get_transcript():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('SELECT * FROM TRANSCRIPT')
        transcript = cursor.fetchall()

        return jsonify(transcript)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()

# Write endpoint to add a new employee
@app.route('/api/v1/transcript', methods=['POST'])
def set_transcipt():
    noop
    try:
        connection = create_connection()
        cursor = connection.cursor()

        data = request.get_json()
        date = data['date']
        string = data['string']

        cursor.execute('INSERT INTO TRANSCRIPT (DATE, STRING) VALUES (%s, %s)', (date, string))
        connection.commit()

        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        connection.close()

# @app.route('/api/v1/transcript', methods=['POST'])
# def add_employee():
#     noop

if __name__ == '__main__':
    app.run(debug=True)
