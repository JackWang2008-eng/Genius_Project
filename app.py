# The main application file for the Flask app

from flask import Flask, render_template, request
from scoring import calculate_priority
from database import init_db, add_request, count_requests, count_critical, get_recent_requests, add_volunteer, count_volunteers

app = Flask(__name__)
init_db()

#dashboard
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/member")
def member():
    return render_template("member.html")

@app.route("/community")
def community_dashboard():
    return render_template(
        "dashboard.html",
        open_requests_count=count_requests(),
        critical_requests_count=count_critical(),
        available_volunteers_count=count_volunteers(),
        matched_tasks_count=0,
        completed_tasks_count=0,
        escalated_cases_count=0,
        recent_requests=get_recent_requests(),
        resource_gaps=[]
    )

#request page
@app.route("/request", methods=["GET", "POST"])
def request_page():
    submission_data = None
    if request.method == "POST":
        # Handle form submission here
        resident_name = request.form.get("resident_name")
        zone = request.form.get("zone")
        need_type = request.form.get("need_type")
        urgency = request.form.get("urgency")
        factors = request.form.getlist("factors")
        priority_score, reasons = calculate_priority(urgency, factors)

        submission_data = {
            "resident_name": resident_name,
            "zone": zone,
            "need_type": need_type,
            "urgency": urgency,
            "factors": factors,
            "priority_score": priority_score,
            "priority_reasons": reasons
        }

        add_request(resident_name, zone, need_type, urgency, factors, priority_score, reasons)

    return render_template('request.html', submitted_request=submission_data)


@app.route("/volunteer", methods=["GET", "POST"])
def volunteer_page():
    submission_data = None
    if request.method == "POST":
        # Handle volunteer form submission here
        availability = request.form.get("availability")
        volunteer_name = request.form.get("volunteer_name")
        zone = request.form.get("zone")
        resources = request.form.getlist("resources")
        

        submission_data = {
            "volunteer_name": volunteer_name,
            "availability": availability,
            "zone": zone,
            "resources": resources
        }

        add_volunteer(volunteer_name, availability, zone, resources)

    return render_template('volunteer.html', submitted_volunteer=submission_data)

if __name__ == "__main__":
    app.run(debug=True)
