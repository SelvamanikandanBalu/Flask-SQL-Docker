import random

from flask import Flask, render_template, url_for, request, redirect, jsonify
import mysql.connector
import time

app = Flask(__name__)

def init_db(con):
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            checked BOOLEAN DEFAULT FALSE
        );
    """)
    con.commit()
    cursor.close()

# Retry connection loop
for i in range(10):
    try:
        con = mysql.connector.connect(
            host="db",
            user="flaskuser",
            password="flaskpass",
            database="mydatabase"
        )
        print("✅ Connected to MySQL!")
        init_db(con)  # <-- ADD THIS LINE
        break
    except mysql.connector.Error as err:
        print(f"⚠️ Attempt {i + 1}: MySQL not ready yet ({err})")
        time.sleep(5)
else:
    raise Exception("❌ Could not connect to MySQL after 10 attempts")

todos = []

@app.route("/")
@app.route("/home", methods = ["GET", "POST"])
def home():
    cursor = con.cursor(dictionary=True)
    if (request.method == "POST"):
        global todos
        todo_name = request.form["todo_name"];
        cur_id = random.randint(1, 1000);
        todos.append(
            { "id": cur_id,
              "name": todo_name,
              "checked": False
            }
        )
        sql_query="INSERT INTO todos (id, name, checked) VALUES (%s, %s, %s)"
        values = (cur_id, todo_name, False)
        cursor.execute(sql_query, values)
        con.commit()

    cursor.execute("select * from todos;")
    todos=cursor.fetchall()
    cursor.close()
    return render_template("index.html", items=todos)

@app.route("/checked/<int:todo_id>/<status>", methods = ["POST"])
def checked_todo(todo_id, status):
    cursor = con.cursor(dictionary=True)
    for todo in todos:
        if todo['id'] == todo_id:
            new_status = 0 if status == "True" else 1
            query="update todos set checked = %s where id = %s;"
            cursor.execute(query, (new_status, todo_id))
            con.commit()
            cursor.close()
            break
    return redirect(url_for('home'))

@app.route("/delete/<int:todo_id>", methods = ["POST"])
def delete_todo(todo_id):
    cursor = con.cursor(dictionary=True)
    for todo in todos:
        if todo['id'] == todo_id:
            sql="delete from todos where id = %s;"
            cursor.execute(sql, (todo_id,))
            con.commit()
            cursor.close()
            break
    return redirect(url_for('home'))

@app.route("/edit_input/<int:todo_id>", methods = ["POST"])
def edit_todo_input(todo_id):
    todo_edit_name = request.form["todo_edit_name"]
    cursor = con.cursor(dictionary=True)
    for todo in todos:
        if todo['id'] == todo_id:
            sql_q="update todos set name = %s where id = %s;"
            cursor.execute(sql_q,(todo_edit_name, todo_id))
            con.commit()
            cursor.close()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
