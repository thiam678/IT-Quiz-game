import tkinter as tk
from tkinter import messagebox
import mysql.connector
import random


# Connect to MySQL and fetch questions
def load_questions():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="quiz"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question, option1, option2, option3, option4, answer, category, difficulty, hints FROM basic_fundamentals
        UNION ALL
        SELECT question, option1, option2, option3, option4, answer, category, difficulty, hints FROM programming
        UNION ALL
        SELECT question, option1, option2, option3, option4, answer, category, difficulty, hints FROM networking
        UNION ALL
        SELECT question, option1, option2, option3, option4, answer, category, difficulty, hints FROM security
        ORDER BY RAND()
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()

    questions = []
    for row in rows:
        questions.append({
            "question": row[0],
            "options": [row[1], row[2], row[3], row[4]],
            "answer": row[5],
            "category": row[6],
            "difficulty": row[7],
            "hints": row[8]
        })
    random.shuffle(questions)
    return questions


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IT Quiz Game 💻")
        self.root.geometry("600x500")
        self.score = 0
        self.q_index = 0
        self.timer_seconds = 10
        self.timer_id = None
        self.questions = load_questions()
        self.user_answers = []

        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 12))
        self.score_label.pack(pady=5)

        self.timer_label = tk.Label(root, text=f"Time left: {self.timer_seconds}", font=("Arial", 12), fg="red")
        self.timer_label.pack(pady=5)

        self.difficulty_label = tk.Label(root, text="", font=("Arial", 11, "italic"), fg="blue")
        self.difficulty_label.pack(pady=2)

        self.category_label = tk.Label(root, text="", font=("Arial", 11, "italic"), fg="green")
        self.category_label.pack(pady=2)

        self.hints_label = tk.Label(root, text="", font=("Arial", 10), fg="purple")
        self.hints_label.pack(pady=2)

        self.question_label = tk.Label(root, text="", wraplength=550, font=("Arial", 14))
        self.question_label.pack(pady=20)

        self.buttons = []
        for i in range(4):
            btn = tk.Button(root, text="", width=60, command=lambda i=i: self.check_answer(i))
            btn.pack(pady=5)
            self.buttons.append(btn)

        self.load_question()

    def load_question(self):
        if self.q_index < len(self.questions):
            self.timer_seconds = 10
            self.update_timer()
            q = self.questions[self.q_index]
            self.question_label.config(text=q["question"])
            self.difficulty_label.config(text=f"Difficulty: {q['difficulty']}")
            self.category_label.config(text=f"Category: {q['category']}")
            self.hints_label.config(text=f"Hints: {q['hints']}")
            for i, option in enumerate(q["options"]):
                self.buttons[i].config(text=option, state=tk.NORMAL)
        else:
            self.show_review()

    def check_answer(self, choice_index):
        self.root.after_cancel(self.timer_id)
        selected = self.buttons[choice_index].cget("text")
        correct = self.questions[self.q_index]["answer"]

        # Store the result
        self.user_answers.append({
            "question": self.questions[self.q_index]["question"],
            "selected": selected,
            "correct": correct
        })

        if selected.lower() == correct.lower():
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")

        self.q_index += 1
        self.load_question()

    def update_timer(self):
        self.timer_label.config(text=f"Time left: {self.timer_seconds}")
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.user_answers.append({
                "question": self.questions[self.q_index]["question"],
                "selected": "No answer (Timed out)",
                "correct": self.questions[self.q_index]["answer"]
            })
            for btn in self.buttons:
                btn.config(state=tk.DISABLED)
            self.root.after(1000, self.next_question)

    def next_question(self):
        self.q_index += 1
        self.load_question()

    def show_review(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Quiz Complete! You scored {self.score} out of {len(self.questions)}",
                 font=("Arial", 14, "bold")).pack(pady=10)

        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for idx, answer in enumerate(self.user_answers):
            q_label = tk.Label(scrollable_frame, text=f"Q{idx + 1}: {answer['question']}", font=("Arial", 12, "bold"),
                               wraplength=550, justify="left")
            q_label.pack(anchor="w", pady=(10, 0))

            selected = answer["selected"]
            correct = answer["correct"]
            result_text = "✅ Correct" if selected.lower() == correct.lower() else "❌ Incorrect"

            tk.Label(scrollable_frame, text=f"Your Answer: {selected}", fg="blue", font=("Arial", 11),
                     justify="left").pack(anchor="w")
            tk.Label(scrollable_frame, text=f"Correct Answer: {correct}", fg="green", font=("Arial", 11),
                     justify="left").pack(anchor="w")
            tk.Label(scrollable_frame, text=result_text, fg="red" if "❌" in result_text else "green",
                     font=("Arial", 11, "italic")).pack(anchor="w", pady=(0, 5))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
