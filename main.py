from flask import Flask, render_template
from froms import RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():

	form = RegistrationForm()
	return render_template('register.html')


if __name__=='__main__':
	app.run(debug=True)
