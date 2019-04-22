from flask import Flask, render_template, request
from core import test1
app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/process',methods = ['POST'])
def process():
	user_input = request.form['user_input']
	bot_response = test1.chatbotMain(user_input)
	return render_template('index.html',user_input=user_input,bot_response=bot_response)
if __name__ == '__main__':
    app.run(debug=True, port=5002)