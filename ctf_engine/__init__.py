from flask import Flask
from flask import render_template

app = Flask(__name__)
#app.config.from_object("config") 
app.config.from_pyfile("config.py")


@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/boomer')
def boomer():
	return render_template("boomer.html")
	
if __name__ == '__main__':
    app.run(debug=True)