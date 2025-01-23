from flask import Flask,render_template,request,session,redirect,url_for
import requests,json
import os 
from dotenv import load_dotenv
import random
from html import unescape
load_dotenv



app = Flask(__name__) 

app.secret_key = os.getenv('FLASK_SECRET_KEY')


TOTAL_QUESTIONS = 50

def fetch_question():
    response = requests.get('https://opentdb.com/api.php?amount=50&category=11&type=multiple')
    data = response.json()
    question_info = data['results'][0]
    question = unescape(question_info['question'])
    correct_answer = unescape(question_info['correct_answer'])
    incorrect_answers = [unescape(ans) for ans in question_info['incorrect_answers']]
    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)
    return question,correct_answer,all_answers
    

@app.route('/',methods=['GET','POST'])
def index():
    session.setdefault('attempted_count',0)
    session.setdefault('correct_count',0)
    
    if session['atempted_count']>=TOTAL_QUESTIONS:
        return render_template('quiz_completed.html',correct_count=session['correct_cont'],total_questions=TOTAL_QUESTIONS)
    
    if request.method=='POST':
        user_answer = request.form.get('answers')
        correct_answer = session.get('correct_answer')
        if user_answer == correct_answer:
            session['correct_count']+=1
            message= "Correct!"
        else:
            message= f"Incorrect!, The correct answer is {correct_answer}."
    else:
        message=None
    
    if request.method == 'Get' or session.get('fetch_new',True):
        question,correct_answer,all_answers = fetch_question()
        session['correct_answer']=correct_answer
        session['current_question']=question
        session['current_answers']=all_answers
        session['fetch_new']=False
    else:
        question=session['current_question']
        all_answers = session['current_answers']
        
    return render_template('index.html',question=question,answers=all_answers,message=message,correct_count=session['correct_count'],attempted_count=session['attempt'])       
     
          
@app.route('/next')
def next_question():
    if session.get('attempted_count',0) < TOTAL_QUESTIONS:
        session['attempted_count'] +=1
        session['fetch_new'] = True
    return redirect(url_for('index'))   

@app.route('/restart')
def restart_quiz():
    session['attempted_count'] = 0
    session['correct_count'] = 0
    session['fetch_new'] = True
    return redirect(url_for('index'))           
    
      


if __name__ == '__main__':
    app.run(debug=True)
