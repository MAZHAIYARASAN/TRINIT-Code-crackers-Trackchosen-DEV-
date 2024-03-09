from flask import Flask, render_template, request, flash
import PyPDF2
import re
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page in range(num_pages):
            text += reader.pages[page].extract_text()
    return text

def generate_mcq(question, options):
    options.append(question)
    random.shuffle(options)
    return options

def generate_questions(text, max_questions=10):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    questions = []
    for sentence in sentences:
        if len(questions) >= max_questions:
            break
        if sentence.strip() != "":
            words = re.findall(r'\b\w+\b', sentence)
            if len(words) > 2:
                options = [f"Option {i}" for i in range(1, 5)]
                question = f"What can be inferred from the statement '{sentence}'?"
                mcq = generate_mcq(question, options)
                questions.append(mcq)
    return questions[:max_questions]

def grade_attempt(user_answers, answer_key):
    correct_answers = 0
    total_questions = len(answer_key)

    for user_ans, correct_ans in zip(user_answers, answer_key):
        if user_ans == correct_ans:
            correct_answers += 1

    percentage_correct = (correct_answers / total_questions) * 100
    return percentage_correct

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        pdf_file = request.files['file']
        answer_key_file = request.files['answer_key']
        num_questions = int(request.form['num_questions'])

        if pdf_file.filename != '' and answer_key_file.filename != '':
            pdf_content = pdf_file.read()
            answer_key_content = answer_key_file.read()

            with open('uploaded_file.pdf', 'wb') as file:
                file.write(pdf_content)
            
            with open('answer_key.pdf', 'wb') as file:
                file.write(answer_key_content)

            extracted_txt = extract_text_from_pdf('uploaded_file.pdf')
            generated_questions = generate_questions(extracted_txt, max_questions=num_questions)

            return render_template('result.html', questions=generated_questions)
    
    flash('Please upload both the question paper and the answer key.')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
