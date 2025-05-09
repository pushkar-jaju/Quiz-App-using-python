import tkinter as tk
from tkinter import messagebox, font, ttk
import random
import pygame
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

# SQLite Database Initialization
def init_db():
    conn = sqlite3.connect('quiz_app.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        username TEXT,
                        score INTEGER)''')
    conn.commit()
    conn.close()

# User registration function
def register_user(username, password):
    conn = sqlite3.connect('quiz_app.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# User verification function
def verify_user(username, password):
    conn = sqlite3.connect('quiz_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Save quiz result
def save_quiz_result(username, score):
    conn = sqlite3.connect('quiz_app.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (username, score) VALUES (?, ?)", (username, score))
    conn.commit()
    conn.close()

# Generate Certificate
def generate_certificate(user_name, score):
    # Define the file name for the certificate
    certificate_file = f"{user_name}_certificate.pdf"
    
    # Create a PDF canvas
    c = canvas.Canvas(certificate_file, pagesize=letter)
    width, height = letter

    # Draw a border for the certificate
    c.setStrokeColor(colors.black)
    c.setLineWidth(4)
    c.rect(0.5 * inch, 0.5 * inch, width - inch, height - inch)

    # Add Certificate Title
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2.0, height - 1.5 * inch, "Certificate of Achievement")

    # Add a congratulatory message
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 2.5 * inch, f"Presented to {user_name}")

    # Add description text
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2.0, height - 3.5 * inch, "For successfully completing the quiz")

    # Add the score
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.green if score >= 3 else colors.red)
    c.drawCentredString(width / 2.0, height - 4.5 * inch, f"Your Score: {score} out of 5")

    # Add the current date
    current_date = datetime.now().strftime("%B %d, %Y")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 5.5 * inch, f"Date: {current_date}")

    # Optional: Add a signature area or logo (example of adding a logo image)
    # c.drawImage("logo.png", 1 * inch, height - 7 * inch, width=1.5 * inch, preserveAspectRatio=True, mask='auto')

    # Optionally, add a line for a signature
    c.setFont("Helvetica", 14)
    c.drawString(1.5 * inch, 1.5 * inch, "________________________")
    c.drawString(1.5 * inch, 1.2 * inch, "Signature")

    # Save the PDF
    c.save()
    
    print(f"Certificate saved as {certificate_file}")

# Main Quiz Application Class
class QuizApp:
    def __init__(self, root):
        pygame.init()
        self.click_sound = pygame.mixer.Sound("next_sound.wav")  # Load your sound file

        self.root = root
        self.root.title("Quiz Application")
        self.root.geometry('1024x768')
        self.root.state('zoomed')  
        self.root.configure(bg='lightblue')

        # Initialize database
        init_db()

        # Custom font styles
        self.title_font = font.Font(family='Helvetica', size=36, weight='bold')
        self.label_font = font.Font(family='Helvetica', size=18)
        self.button_font = font.Font(family='Helvetica', size=18, weight='bold')

        # Login Screen Frame
        self.frame_login = tk.Frame(self.root, bg='lightblue', bd=10, relief='raised')
        self.frame_login.pack(fill='both', expand=True, padx=20, pady=20)

        self.label_title = tk.Label(self.frame_login, text="Welcome to the Quiz App!", bg='lightblue', font=self.title_font)
        self.label_title.pack(pady=20)

        self.label_user = tk.Label(self.frame_login, text="Username:", bg='lightblue', font=self.label_font)
        self.label_user.pack(pady=10)
        self.entry_user = tk.Entry(self.frame_login, font=self.label_font, width=20)
        self.entry_user.pack(pady=10)

        self.label_pass = tk.Label(self.frame_login, text="Password:", bg='lightblue', font=self.label_font)
        self.label_pass.pack(pady=10)
        self.entry_pass = tk.Entry(self.frame_login, show='*', font=self.label_font, width=20)
        self.entry_pass.pack(pady=10)

        self.show_pass = False
        self.toggle_button = tk.Button(self.frame_login, text="Show", command=self.toggle_password, font=self.button_font)
        self.toggle_button.pack(pady=5)

        self.login_button = tk.Button(self.frame_login, text="Login", command=self.login, font=self.button_font, bg='green', fg='white', width=10)
        self.login_button.pack(pady=20)

        self.register_button = tk.Button(self.frame_login, text="Register", command=self.show_registration_frame, font=self.button_font, bg='blue', fg='white', width=10)
        self.register_button.pack(pady=10)

        self.cancel_button = tk.Button(self.frame_login, text="Cancel", command=self.cancel, font=self.button_font, bg='red', fg='white', width=10)
        self.cancel_button.pack(pady=10)

        # Registration Frame
        self.frame_registration = tk.Frame(self.root, bg='lightblue', bd=10, relief='raised')

        self.label_reg_title = tk.Label(self.frame_registration, text="Create an Account", bg='lightblue', font=self.title_font)
        self.label_reg_title.pack(pady=20)

        self.label_reg_user = tk.Label(self.frame_registration, text="Username:", bg='lightblue', font=self.label_font)
        self.label_reg_user.pack(pady=10)
        self.entry_reg_user = tk.Entry(self.frame_registration, font=self.label_font, width=20)
        self.entry_reg_user.pack(pady=10)

        self.label_reg_pass = tk.Label(self.frame_registration, text="Password:", bg='lightblue', font=self.label_font)
        self.label_reg_pass.pack(pady=10)
        self.entry_reg_pass = tk.Entry(self.frame_registration, show='*', font=self.label_font, width=20)
        self.entry_reg_pass.pack(pady=10)

        self.show_reg_pass = False
        self.toggle_reg_button = tk.Button(self.frame_registration, text="Show", command=self.toggle_reg_password, font=self.button_font)
        self.toggle_reg_button.pack(pady=5)

        self.register_button = tk.Button(self.frame_registration, text="Register", command=self.register, font=self.button_font, bg='green', fg='white', width=10)
        self.register_button.pack(pady=20)

        self.back_button = tk.Button(self.frame_registration, text="Back to Login", command=self.back_to_login, font=self.button_font, bg='blue', fg='white', width=10)
        self.back_button.pack(pady=10)

        # Quiz Frame
        self.frame_quiz = tk.Frame(self.root, bg='lightblue', bd=10, relief='raised')

        self.label_question = tk.Label(self.frame_quiz, text="", bg='lightblue', font=self.label_font, wraplength=700)
        self.label_question.pack(pady=20)

        self.var_option = tk.StringVar()
        self.options_frame = tk.Frame(self.frame_quiz, bg='lightblue')
        self.options_frame.pack(pady=20)

        self.options = []
        for i in range(4):
            option = tk.Radiobutton(self.options_frame, text="", variable=self.var_option, value="", font=self.label_font, bg='lightblue')
            option.pack(anchor='w')
            self.options.append(option)

        # Add Previous and Next buttons
        self.prev_button = tk.Button(self.frame_quiz, text="Previous", command=self.previous_question, font=self.button_font, bg='orange', fg='white', width=10)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.next_button = tk.Button(self.frame_quiz, text="Next", command=self.next_question, font=self.button_font, bg='green', fg='white', width=10)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.submit_button = tk.Button(self.frame_quiz, text="Submit", command=self.submit_answer, font=self.button_font, bg='blue', fg='white', width=10)
        self.submit_button.pack(pady=20)

        self.progress = ttk.Progressbar(self.frame_quiz, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)


        # Shuffle and select 5 questions each time
        self.current_question_index = 0
        self.score = 0

        # Add Result Frame for showing answers and explanations
        self.frame_result = tk.Frame(self.root, bg='lightblue', bd=10, relief='raised')

        self.label_result_title = tk.Label(self.frame_result, text="Quiz Results", font=self.title_font, bg='lightblue')
        self.label_result_title.pack(pady=20)

        self.result_text = tk.Text(self.frame_result, font=self.label_font, bg='lightblue', width=90, height=20)
        self.result_text.pack(pady=10)

        self.button_certificate = tk.Button(self.frame_result, text="View Certificate", command=self.show_certificate, font=self.button_font, bg='green', fg='white', width=15)
        self.button_certificate.pack(pady=20)

        # Other initializations
        self.user_answers = []
        self.score = 0

    def toggle_password(self):
        if self.show_pass:
            self.entry_pass.config(show="*")
            self.toggle_button.config(text="Show")
        else:
            self.entry_pass.config(show="")
            self.toggle_button.config(text="Hide")
        self.show_pass = not self.show_pass

    def toggle_reg_password(self):
        if self.show_reg_pass:
            self.entry_reg_pass.config(show="*")
            self.toggle_reg_button.config(text="Show")
        else:
            self.entry_reg_pass.config(show="")
            self.toggle_reg_button.config(text="Hide")
        self.show_reg_pass = not self.show_reg_pass

    def cancel(self):
        self.root.quit()

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        # Validation checks
        if not username or not password:
            messagebox.showerror("Login Failed", "Username and password cannot be empty.")
            return
        if len(username) <= 5 or len(password) <= 5:
            messagebox.showerror("Login Failed", "Username and password must be more than 5 characters.")
            return
  
        if verify_user(username, password):
            messagebox.showinfo("Login Successful", "Welcome to the quiz!")
            self.frame_login.pack_forget()
            self.frame_quiz.pack(fill='both', expand=True)
            self.start_quiz()  # Start the quiz and load questions
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.entry_reg_user.get()
        password = self.entry_reg_pass.get()

        # Validation checks
        if not username or not password:
            messagebox.showerror("Registration Failed", "Username and password cannot be empty.")
            return
        if len(username) <= 5 or len(password) <= 5:
            messagebox.showerror("Registration Failed", "Username and password must be more than 5 characters.")
            return

        if register_user(username, password):
            messagebox.showinfo("Registration Successful", "Account created successfully!")
            self.back_to_login()
        else:
            messagebox.showerror("Registration Failed", "Username already exists.")

    def show_registration_frame(self):
        self.frame_login.pack_forget()
        self.frame_registration.pack(fill='both', expand=True)

    def back_to_login(self):
        self.frame_registration.pack_forget()
        self.frame_login.pack(fill='both', expand=True)

    def start_quiz(self):
        self.questions = self.load_questions()
        self.shuffle_questions()
        self.load_question()

    def load_questions(self):
    # Sample questions with explanations
        return [
            {"question": "What is the output of print(2 ** 3)?",
            "options": ["6", "8", "9", "10"],
            "answer": "8",
            "explanation": "The ** operator in Python is used for exponentiation. So, 2 ** 3 means 2 raised to the power of 3, which equals 8."},

            {"question": "Which of the following is not a programming language?",
            "options": ["Python", "Java", "HTML", "C#"],
            "answer": "HTML",
            "explanation": "HTML is a markup language used to structure web content, but it is not a programming language."},

            {"question": "What does HTML stand for?",
            "options": ["Hypertext Markup Language", "Hightext Machine Language", "Hyperloop Machine Language", "None of the above"],
            "answer": "Hypertext Markup Language",
            "explanation": "HTML stands for Hypertext Markup Language, which is used to create the structure of web pages."},

            {"question": "Which symbol is used for comments in Python?",
            "options": ["//", "#", "/*", "<!--"],
            "answer": "#",
            "explanation": "The # symbol is used to create comments in Python."},

            {"question": "What is the correct file extension for Python files?",
            "options": [".py", ".pt", ".pyt", ".pyth"],
            "answer": ".py",
            "explanation": "Python files have the .py extension."},

            {"question": "Which company developed Java?",
            "options": ["Microsoft", "Sun Microsystems", "Apple", "Oracle"],
            "answer": "Sun Microsystems",
            "explanation": "Java was developed by Sun Microsystems, which was later acquired by Oracle."},

            {"question": "Which of the following is a Python framework?",
            "options": ["Flask", "Django", "Both", "None"],
            "answer": "Both",
            "explanation": "Flask and Django are popular web frameworks for building applications in Python."},

            {"question": "What does CSS stand for?",
            "options": ["Creative Style Sheets", "Colorful Style Sheets", "Computer Style Sheets", "Cascading Style Sheets"],
            "answer": "Cascading Style Sheets",
            "explanation": "CSS stands for Cascading Style Sheets and is used to style the layout of web pages."},

            {"question": "Which of the following is a correct variable name in Python?",
            "options": ["myVar", "my-var", "my var", "my.var"],
            "answer": "myVar",
            "explanation": "Variable names in Python cannot contain spaces, dashes, or dots. Only alphanumeric characters and underscores are allowed."},

            {"question": "What does SQL stand for?",
            "options": ["Structured Query Language", "Structured Question Language", "Style Query Language", "None of the above"],
            "answer": "Structured Query Language",
            "explanation": "SQL stands for Structured Query Language and is used to communicate with databases."},

            {"question": "Which of the following is not a data type in Python?",
            "options": ["List", "Tuple", "Dictionary", "Character"],
            "answer": "Character",
            "explanation": "Python does not have a character data type; single characters are treated as strings of length 1."},

            {"question": "What keyword is used to define a function in Python?",
            "options": ["define", "function", "def", "fun"],
            "answer": "def",
            "explanation": "The def keyword is used to define a function in Python."},

            {"question": "Which of the following is used to handle exceptions in Python?",
            "options": ["try", "catch", "finally", "all of the above"],
            "answer": "all of the above",
            "explanation": "In Python, try, except, and finally blocks are used to handle exceptions."},

            {"question": "Which operator is used to compare two values in Python?",
            "options": ["==", "=", "===", "!="],
            "answer": "==",
            "explanation": "The == operator checks if two values are equal, while = is used for assignment."},

            {"question": "What is the main purpose of a loop in programming?",
            "options": ["To repeat a block of code", "To perform conditional checks", "To define variables", "To store data"],
            "answer": "To repeat a block of code",
            "explanation": "A loop allows you to repeat a block of code multiple times."},

            {"question": "Which keyword is used to exit a loop in Python?",
            "options": ["exit", "break", "stop", "end"],
            "answer": "break",
            "explanation": "The break keyword is used to exit a loop prematurely."},

            {"question": "What does API stand for?",
            "options": ["Application Programming Interface", "Application Protocol Interface", "Advanced Programming Interface", "None of the above"],
            "answer": "Application Programming Interface",
            "explanation": "API stands for Application Programming Interface, which allows different software systems to communicate with each other."},

            {"question": "Which method is used to add an element to the end of a list in Python?",
            "options": ["add()", "append()", "insert()", "extend()"],
            "answer": "append()",
            "explanation": "The append() method is used to add an element to the end of a list."},

            {"question": "What is the correct syntax to create a variable in Python?",
            "options": ["variable_name = value", "create variable_name = value", "var variable_name = value", "None of the above"],
            "answer": "variable_name = value",
            "explanation": "In Python, variables are created by assigning a value using the = operator."},

            {"question": "Which of the following is used to import modules in Python?",
            "options": ["import module_name", "require module_name", "include module_name", "load module_name"],
            "answer": "import module_name",
            "explanation": "The import keyword is used to include external modules or libraries in Python."}
    ]


    def shuffle_questions(self):
        random.shuffle(self.questions)
        self.questions = self.questions[:5]  # Select only 5 questions

    def load_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.label_question.config(text=question["question"])
            for i, option in enumerate(self.options):
                option.config(text=question["options"][i], value=question["options"][i])
            self.progress['value'] = (self.current_question_index / len(self.questions)) * 100
            self.update_buttons_state()  # Update button states when loading a question
        else:
            self.show_results()


    def previous_question(self):
            if self.current_question_index > 0:
                self.current_question_index -= 1
                self.load_question()
                self.update_buttons_state()

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()
            self.update_buttons_state()

    def update_buttons_state(self):
        # Disable Previous button if on the first question
        if self.current_question_index == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)

        # Disable Next button if on the last question
        if self.current_question_index == len(self.questions) - 1:
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)


    def submit_answer(self):
        selected_option = self.var_option.get()
        correct_answer = self.questions[self.current_question_index]["answer"]
        self.user_answers.append({
            "question": self.questions[self.current_question_index]["question"],
            "selected_option": selected_option,
            "correct_answer": correct_answer,
            "explanation": self.questions[self.current_question_index]["explanation"]
        })

        if selected_option == correct_answer:
            self.score += 1

        # Load next question or show results
        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            self.load_question()
        else:
            self.show_results_with_explanation()

    def show_results_with_explanation(self):
        self.frame_quiz.pack_forget()
        self.frame_result.pack(fill='both', expand=True)

        # Clear previous content in the result text area
        self.result_text.delete(1.0, tk.END)

        # Display user's answers, correct answers, and explanations
        for i, result in enumerate(self.user_answers):
            result_summary = (f"Q{i+1}: {result['question']}\n"
                              f"Your Answer: {result['selected_option']}\n"
                              f"Correct Answer: {result['correct_answer']}\n"
                              f"Explanation: {result['explanation']}\n\n")
            self.result_text.insert(tk.END, result_summary)

    

    def show_certificate(self):
        # Generate the certificate
        generate_certificate(self.entry_user.get(), self.score)
        # Display the certificate
        certificate_window = tk.Toplevel(self.root)
        certificate_window.title("Certificate")
        certificate_window.geometry("600x400")
        certificate_window.attributes("-fullscreen", True)
        certificate_window.configure(bg='lightblue')

        label_certificate = tk.Label(certificate_window, text="Congratulations!", font=self.title_font, bg='lightblue')
        label_certificate.pack(pady=20)

        label_score = tk.Label(certificate_window, text=f"Your Score: {self.score} out of 5", font=self.label_font, bg='lightblue')
        label_score.pack(pady=10)

        label_message = tk.Label(certificate_window, text="Your certificate has been generated.", font=self.label_font, bg='lightblue')
        label_message.pack(pady=10)

        button_exit = tk.Button(certificate_window, text="Exit", command=self.root.quit, font=self.button_font, bg='red', fg='white', width=10)
        button_exit.pack(pady=20)

        save_result = tk.Button(
        certificate_window,
        text="Save Result",
        command=lambda: self.save_and_notify(self.entry_user.get(), self.score),
        font=self.button_font,
        bg='blue',
        fg='white',
        width=10
    )
        save_result.pack(pady=10)

    def save_and_notify(self, username, score):
        save_quiz_result(username, score)  # Save the result to the database
        messagebox.showinfo("Save Successful", "Your certificate has been saved successfully!")  # Show confirmation message
        self.root.quit()  # Exit the application
        
# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    quiz_app = QuizApp(root)
    root.mainloop()

