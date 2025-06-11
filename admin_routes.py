# admin_routes.py
from flask import Blueprint, render_template
from extension import mongo
from flask import Flask, render_template, redirect, request, session, url_for, jsonify
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
            return redirect(url_for("admin.dashboard"))  # or correct endpoint
        else:
            # Optional: flash or log message
            print("Invalid credentials")
            return render_template("login.html", error="Invalid credentials")  # 💡 Show error

    return render_template("login.html")  # ✅ This handles GET requests

@admin_bp.route("/logout")
def logout():
    session.clear()
    #flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))




@admin_bp.route("/admin/complaints")
def ad_complaints():
        complaints = list(mongo.db.complaints.find())
        complaints.reverse()
        if not session.get("logged_in"):
            return redirect(url_for("admin.login"))
        return render_template('complaint.html',complaints=complaints)

from flask import render_template
from collections import Counter
import plotly.graph_objs as go
import plotly
import json
@admin_bp.route('/admin/data-graph')
def data_graph():
    data = list(mongo.db.complaints.find())

    # --- Emergency Type Frequency Chart ---
    emergency_types = [entry['emergency_type'] for entry in data if entry.get('emergency_type')]
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
    if not session.get("logged_in"):
            return redirect(url_for("admin.login"))
    return render_template("datagraph.j2", graphJSON_type=graphJSON_type, graphJSON_date=graphJSON_date)
