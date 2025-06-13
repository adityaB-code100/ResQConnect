from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from bson.objectid import ObjectId
import requests
import json
from datetime import datetime
from gemini_api import generate_gemini_response
from data_fetcher import alert_store, wether_store, cleanup_old_alerts, cleanup_old_weather
from extension import mongo  # ✅ New import
from admin_routes import admin_bp  # ✅ Now this won't cause circular import
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
app.secret_key = "your_secret_key"

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app.config["MONGO_URI"] = params["mongo_uri"]
mongo.init_app(app)  # ✅ Initialize mongo here

app.register_blueprint(admin_bp)


# ------------------- ROUTES -------------------

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
    if not card:
        return "Card not found", 404
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
    return render_template('alerts.html', events=filtered_alerts)

@app.route('/weather')
def show_weather():
    weather = mongo.db.weather.find_one(sort=[("time", -1)])
    return render_template('weather.html', weather=weather)

@app.route('/g')
def indexb():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_response():
    data = request.get_json()
    prompt = data.get('prompt', '')
    response = generate_gemini_response(prompt)
    return jsonify({'response': response})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ------------------- MAIN -------------------


# 🕒 Schedule your jobs here
scheduler = BackgroundScheduler()

scheduler.add_job(alert_store, 'interval', minutes=10)

scheduler.add_job(wether_store, 'interval', minutes=10)

scheduler.add_job(lambda: cleanup_old_alerts(7), 'cron', hour=0, minute=0)

scheduler.add_job(lambda: cleanup_old_weather(1), 'cron', hour=0, minute=30)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.route('/info/<slug>')
def get_info(slug):
    info = mongo.db.info_sections.find_one({"slug": slug})
    return render_template("policy.html", info=info)



if __name__ == "__main__":
    
    app.run(debug=True)
