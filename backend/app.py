from flask import Flask, request, jsonify
import sqlite3
import random

app = Flask(__name__)
DB_NAME = "ethics_questions.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # to get dict-like rows
    return conn

# Add a new question
@app.route("/add_question", methods=["POST"])
def add_question():
    data = request.json  # expects JSON input
    required_fields = ["module_number", "type", "question", "correct_answer"]
    
    for field in required_fields:
        if field not in data:
            return {"error": f"{field} is required"}, 400

    # fields for multiple choice questions
    choice_a = data.get("choice_a")
    choice_b = data.get("choice_b")
    choice_c = data.get("choice_c")
    choice_d = data.get("choice_d")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions (module_number, type, question, choice_a, choice_b, choice_c, choice_d, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data["module_number"], data["type"], data["question"],
          choice_a, choice_b, choice_c, choice_d, data["correct_answer"]))
    conn.commit()
    conn.close()

    return {"message": "Question added successfully!"}

# Get all questions for a module (manual selection)
@app.route("/get_all_questions", methods=["GET"])
def get_all_questions():
    module = request.args.get("module_number")
    if not module:
        return {"error": "module_number is required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE module_number = ?", (module,))
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(questions)

# Get random questions for a module and type 
@app.route("/get_random_questions", methods=["GET"])
def get_random_questions():
    module = request.args.get("module_number")
    q_type = request.args.get("type")  # mcq / true_false / identification
    num = int(request.args.get("num_items", 5))  # default 5

    if not module or not q_type:
        return {"error": "module_number and type are required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE module_number=? AND type=?", (module, q_type))
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if len(questions) == 0:
        return {"error": "No questions found"}, 404

    # pick random questions
    selected = random.sample(questions, min(num, len(questions)))
    return jsonify(selected)

#Run the app 
if __name__ == "__main__":
    app.run(debug=True)
