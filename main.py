from flask import Flask, render_template, redirect, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import requests
import json
from datetime import datetime, timedelta
from flask import  jsonify
from gemini_api import generate_gemini_response  
from data_fetcher import alert_store, wether_store,cleanup_old_alerts, cleanup_old_weather



app = Flask(__name__)

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# MongoDB connection
app.config["MONGO_URI"] = params["mongo_uri"]  
mongo = PyMongo(app)

# Routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        complaint = {
            "name": request.form['name'],
            "contact": request.form['contact'],
            "emergency_type": request.form['emergency'],
            "location": request.form['location'],
            "description": request.form['description'],
            "timestamp": datetime.utcnow()
        }
        mongo.db.complaints.insert_one(complaint)
        return redirect('/register')
    return render_template('Home.html')


@app.route('/c', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        contact_data = {
            "name": request.form['name'],
            "contact": request.form['contact'],
            "location": request.form['location'],
            "description": request.form['description'],
            "timestamp": datetime.utcnow()
        }
        mongo.db.contacts.insert_one(contact_data)
        return redirect('/contactus')
    return render_template('Home.html')


@app.route("/tagline/<string:Emergency_id>")
def tagline(Emergency_id):
    emergency = mongo.db.emergencies.find_one({"_id": ObjectId(Emergency_id)})
    return render_template('tagline.html', emergency=emergency)


@app.route("/home")
def home():
    return render_template('Home.html')


@app.route("/register")
def register():
    return render_template('register.html')


@app.route("/service/<string:card_id>")
def first_aid(card_id):
    card = mongo.db.card.find_one({"_id": ObjectId(card_id)})
    print(card_id)
    # card = mongo.db.card.find_one({"_id": card_id})

    
    if not card:
        return "Card not found", 404  # Or render a custom error page

    firstaid_para = card.get('description', '')
    firstaid_list = firstaid_para.split('.')
    return render_template('first_aid.html', card=card, firstaid_list=firstaid_list)



@app.route("/service")
def service():
    cards = mongo.db.card.find()
    return render_template('service.html', cards=cards)


@app.route("/contactus")
def contactus():
    return render_template('contact.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/Admin")
def Admin():
    contacts = list(mongo.db.contacts.find())
    print(contacts)

    return render_template('Admin.html',contacts=contacts)


@app.route("/policy")
def policy():
    return render_template('policy.html')


@app.route('/alerts')
def show_recent_global_alerts():
    recent_alerts = list(mongo.db.alerts.find().sort("date", -1))

    seen = set()
    filtered_alerts = []
    for alert in recent_alerts:
        key = (alert['title'], alert['date'])
        if key not in seen:
            seen.add(key)
            filtered_alerts.append(alert)
        if len(filtered_alerts) == 5:
            break

    recent_alerts = filtered_alerts
    return render_template('alerts.html', events=recent_alerts)


@app.route('/weather')
def show_weather():
    weather=mongo.db.weather.find_one(sort=[("time", -1)])  
    return render_template('weather.html', weather=weather)


@app.route('/g')
def indexb():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_response():
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    # Simulated AI response
    response = generate_gemini_response(prompt)
    # print(response)

    return jsonify({'response': response})
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
    alert_store()
    wether_store()
    cleanup_old_alerts(days=7)    
    cleanup_old_weather(days=1) 
