from flask import Blueprint, render_template, redirect, request, session, url_for
from extension import mongo
from collections import Counter
import plotly.graph_objs as go
import plotly
import json

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/Admin")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("admin.login"))
    return render_template('Admin.html')


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "Admin" and password == "1234":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("admin.dashboard"))
        else:
            print("Invalid credentials")
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.route("/admin/complaints")
def ad_complaints():
    if not session.get("logged_in"):
        return redirect(url_for("admin.login"))

    complaints = list(mongo.db.complaints.find())
    complaints.reverse()
    title="Complaints Registered"
    return render_template('complaint.html', complaints=complaints)

@admin_bp.route("/admin/contact_request")
def ad_contact_request():
    if not session.get("logged_in"):
        return redirect(url_for("admin.login"))

    complaints = list(mongo.db.contacts.find())
    complaints.reverse()
    title="Contact Request Registered"
    return render_template('complaint.html', complaints=complaints,title=title)


@admin_bp.route('/admin/data-graph')

def data_graph():
    if not session.get("logged_in"):
        return redirect(url_for("admin.login"))

    data = list(mongo.db.complaints.find())

    # --- Emergency Type Frequency Chart ---
    emergency_types = [entry.get('emergency_type') for entry in data if entry.get('emergency_type')]
    type_counts = dict(Counter(emergency_types))
    labels = list(type_counts.keys())
    values = list(type_counts.values())

    bar_chart = go.Bar(x=labels, y=values, marker_color='rgb(66, 135, 245)')
    layout = go.Layout(title='Emergency Type Frequency',
                       xaxis=dict(title='Emergency Type'),
                       yaxis=dict(title='Count'))
    fig_type = go.Figure(data=[bar_chart], layout=layout)
    graphJSON_type = json.dumps(fig_type, cls=plotly.utils.PlotlyJSONEncoder)

    # --- Complaints Per Day Chart ---
    date_counts = Counter(
        entry['timestamp'].strftime('%Y-%m-%d')
        for entry in data if entry.get('timestamp')
    )
    date_labels = sorted(date_counts)
    date_values = [date_counts[date] for date in date_labels]

    line_chart = go.Scatter(x=date_labels, y=date_values, mode='lines+markers',
                            marker=dict(color='rgb(255, 100, 100)'))
    layout_date = go.Layout(title='Complaints Per Day',
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Number of Complaints'))
    fig_date = go.Figure(data=[line_chart], layout=layout_date)
    graphJSON_date = json.dumps(fig_date, cls=plotly.utils.PlotlyJSONEncoder)

    # --- Location vs Number of Emergencies Chart ---
    locations = [entry.get('location') for entry in data if entry.get('location')]
    location_counts = dict(Counter(locations))
    location_labels = list(location_counts.keys())
    location_values = list(location_counts.values())

    location_chart = go.Bar(x=location_labels, y=location_values, marker_color='rgb(100, 200, 100)')
    layout_location = go.Layout(title='Emergencies by Location',
                                xaxis=dict(title='Location'),
                                yaxis=dict(title='Number of Emergencies'))
    fig_location = go.Figure(data=[location_chart], layout=layout_location)
    graphJSON_location = json.dumps(fig_location, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "datagraph.j2",
        graphJSON_type=graphJSON_type,
        graphJSON_date=graphJSON_date,
        graphJSON_location=graphJSON_location
    )


# Prevent cached pages after logout (very important for session security)
@admin_bp.after_app_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@admin_bp.route("/admin/Service_Register")
def service_register():
    if not session.get("logged_in"):
        return redirect(url_for("admin.login"))

    # complaints = list(mongo.db.contacts.find())
    # complaints.reverse()
    # title="Contact Request Registered"
    # return render_template('complaint.html', complaints=complaints,title=title)
    return render_template("Adservice.html")



@admin_bp.route('/add-service', methods=['POST'])
def add_service():

    if request.method == 'POST':
        service={
            "title" :request.form['serviceTitle'],
            "image_url": request.form['serviceImage'],  # ✔ using form input (URL)

            "number" : request.form['helpline'],
            "description" : request.form['firstAid']
        }
        mongo.db.card.insert_one(service)
        return redirect('/admin/Service_Register')
    return redirect("/admin")

