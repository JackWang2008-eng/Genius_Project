from flask import Flask, render_template, request, redirect, url_for, session
from scoring import calculate_triage_score
from database import init_db, add_request, get_all_requests, add_volunteer, get_all_volunteers, find_matches, assign_match, resolve_request, save_disaster_status, get_disaster_status

app = Flask(__name__)
init_db()

COORDINATOR_ACCESS_CODE = "COMMUNITY123"
PROFESSIONAL_ACCESS_CODE = "RESPONDER123"
app.secret_key = "676767"



def is_community():
    return session.get("user_type") == "coordinator"

def is_professional():
    return session.get("professional_access") == "approved"

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        
        access_code = request.form.get("access_code")

        if access_code == COORDINATOR_ACCESS_CODE:
            session["user_type"] = "coordinator"
            return redirect(url_for("community"))

        error = "Invalid access code."

    return render_template("login.html", error=error)



@app.route("/")
def home():
    return render_template("home.html")


@app.route("/resident")
def resident():
    return render_template("resident.html")

@app.route("/professional-login", methods=["GET", "POST"])
def professional_login():
    error = None

    if request.method == "POST":
        access_code = request.form.get("access_code")

        if access_code == PROFESSIONAL_ACCESS_CODE:
            session["professional_access"] = "approved"
            return redirect(url_for("professional"))

        error = "Invalid professional responder code."

    return render_template("professional_login.html", error=error)


@app.route("/request", methods=["POST", "GET"])
def request_page():
    submitted_request = None

    # Get data from form
    if request.method == "POST":
        resident_name = request.form.get("resident_name")
        zone = request.form.get("zone")
        need_type = request.form.get("need_type")
        phone_number = request.form.get("phone_number")

        red_flags = request.form.getlist("red_flags")
        injury_level = request.form.get("injury_level")
        mobility_status = request.form.get("mobility_status")
        vulnerable_person = request.form.get("vulnerable_person")
        evacuation_need = request.form.get("evacuation_need")
        safe_shelter = request.form.get("safe_shelter")

        urgency, priority_score, triage_reasons = calculate_triage_score(
            red_flags,
            injury_level,
            mobility_status,
            vulnerable_person,
            evacuation_need,
            safe_shelter,
        )
        
        # Process data and save to database
        submitted_request = {
            "resident_name": resident_name,
            "phone_number": phone_number,
            "zone": zone,
            "need_type": need_type,
            "injury_level": injury_level,
            "mobility_status": mobility_status,
            "vulnerable_person": vulnerable_person,
            "evacuation_need": evacuation_need,
            "safe_shelter": safe_shelter,
            "red_flags": red_flags,
            "urgency": urgency,
            "priority_score": priority_score,
            "triage_reasons": triage_reasons,
        }

        add_request(submitted_request)

    return render_template("request.html", submitted_request=submitted_request)


@app.route("/community", methods=["GET", "POST"])
def community():
    if not is_community():                  # Check if the user is a coordinator and automatically redirect to home if not
        return redirect(url_for("login"))

    if request.method == "POST":
        disaster_type = request.form.get("disaster_type")
        stage = request.form.get("stage")

        save_disaster_status(disaster_type, stage)

    requests = get_all_requests()
    volunteers = get_all_volunteers()
    matches = find_matches()

    return render_template(
        "community.html",
        current_disaster=get_disaster_status(),
        requests=requests,
        volunteers=volunteers,
        matches=matches
    )

@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    submitted_volunteer = None

    if request.method == "POST":
        volunteer_name = request.form.get("volunteer_name")
        phone_number = request.form.get("phone_number")
        zone = request.form.get("zone")
        resource_type = request.form.get("resource_type")
        availability = request.form.get("availability")

        submitted_volunteer = {
            "volunteer_name": volunteer_name,
            "phone_number": phone_number,
            "helper_type": "Community Volunteer",
            "zone": zone,
            "resource_type": resource_type,
            "availability": availability
        }

        add_volunteer(submitted_volunteer)

    return render_template("volunteer.html", submitted_volunteer=submitted_volunteer)

@app.route("/professional", methods=["GET", "POST"])
def professional():
    if not is_professional():
        return redirect(url_for("professional_login"))

    submitted_professional = None

    if request.method == "POST":
        volunteer_name = request.form.get("volunteer_name")
        phone_number = request.form.get("phone_number")
        zone = request.form.get("zone")
        resource_type = request.form.get("resource_type")
        availability = request.form.get("availability")

        submitted_professional = {
            "volunteer_name": volunteer_name,
            "phone_number": phone_number,
            "helper_type": "Professional Responder",
            "zone": zone,
            "resource_type": resource_type,
            "availability": availability
        }

        add_volunteer(submitted_professional)

    return render_template("professional.html", submitted_professional=submitted_professional)

@app.route("/assign", methods=["POST"])
def assign():
    if not is_community():
        return redirect(url_for("login"))

    request_id = request.form.get("request_id")
    volunteer_id = request.form.get("volunteer_id")

    assign_match(request_id, volunteer_id)

    return redirect(url_for("community"))

@app.route("/resolve", methods=["POST"])
def resolve():
    if not is_community():
        return redirect(url_for("login"))

    request_id = request.form.get("request_id")

    resolve_request(request_id)

    return redirect(url_for("community"))

if __name__ == "__main__":
    app.run(debug=True)
