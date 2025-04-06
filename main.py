from flask import Flask, render_template, redirect,request
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime


app = Flask(__name__)


with open('config.json', 'r') as c:
    params = json.load(c)["params"]



app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']


db = SQLAlchemy(app)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    emergency_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Emergency = db.Column(db.String(80), nullable=False)
    img=db.Column(db.String(1000))
    helpline= db.Column(db.String(20), nullable=False)
    firstaid= db.Column(db.Text)

class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tital = db.Column(db.String(80), nullable=False)
    helpline= db.Column(db.String(20), nullable=False)
    des= db.Column(db.Text)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        emergency_type = request.form['emergency']
        location = request.form['location']
        description = request.form['description']

        new_complaint = Complaint(
            name=name,
            contact=contact,
            emergency_type=emergency_type,
            location=location,
            description=description
        )
        
        db.session.add(new_complaint)
        db.session.commit()
        return redirect('/register')

    return render_template('Home.html')

@app.route('/c', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        location = request.form['location']
        description = request.form['description']

        new_contact = Contact(
            name=name,
            contact=contact,
            location=location,
            description=description
        )
        
        db.session.add(new_contact)
        db.session.commit()
        return redirect('/contactus')

    return render_template('Home.html')

@app.route("/tagline/<int:Emergency_id>")
def tagline(Emergency_id):
    emergency = Emergency.query.get(Emergency_id)

    return render_template('tagline.html',emergency=emergency)

@app.route("/home")
def home():
    return render_template('Home.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/service/<int:card_id>")
def first_aid(card_id):
    card = Card.query.get(card_id)
     

    firstaid_para= card.firstaid
    firstaid_list=firstaid_para.split('.')
    print(firstaid_para)
    return render_template('first_aid.html',card=card, firstaid_list= firstaid_list)


@app.route("/service")
def service():

    cards = Card.query.all()

    return render_template('service.html',cards=cards)

@app.route("/contactus")
def contactus():
    return render_template('contact.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/Admin")
def Admin():
    return render_template('Admin.html')





















































if __name__ == "__main__":
    app.run(debug=True)
