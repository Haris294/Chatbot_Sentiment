from flask import Flask, render_template, request, flash, url_for, request, session, redirect
import requests
import json
import calendar
from core import Classify


from gtts import gTTS
import speech_recognition as sr
from urllib.request import FancyURLopener
import pyttsx3
import requests
import threading



question_list = []
answer_list = []


qandalist = []

    
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

   

    if request.method == 'POST':

        if request.form['question'] != 'NULL':
            qanda = {}
            question = request.form['question']

            question_list.append(question)

            answer = Classify.classifyCommand(question)
            # print(question)
            answer_list.append(answer)

            qanda.update({question:answer})
            

            replied_answer = {
                'user_question': question_list,
                'question': answer_list
            }

            print(qandalist)
        qandalist.append(qanda)
        

        return render_template('index.html', qanda=qandalist)
    else:

        return render_template('index.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


# //background process happening without any refreshing
@app.route('/', methods=['GET', 'POST'])
@app.route('/background_process_test')
def background_process_test():
    
    #question = command
    question, answer = Classify.classifyListenCommand()
    # print(question)

    replied_answer = {
        'user_question': question,
        'question': answer
    }
    print(replied_answer)

    return render_template('index.html', replied_answer=replied_answer)
    # return command


if __name__ == '__main__':
    app.run(debug=True)
