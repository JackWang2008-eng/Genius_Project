from flask import Flask, render_template, request, redirect, url_for, session
from scoring import calculate_triage_score

app = Flask(__name__)

current_disaster = {
    "disaster_type": None,
    "stage": None
}

COORDINATOR_ACCESS_CODE = "COMMUNITY123"
app.secret_key = "676767"

def is_community():
    return session.get("user_type") == "coordinator"

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


@app.route("/request", methods=["POST", "GET"])
def request_page():
    submitted_request = None

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

    return render_template("request.html", submitted_request=submitted_request)


@app.route("/community", methods=["GET", "POST"])
def community():
    if not is_community():                  # Check if the user is a coordinator and automatically redirect to home if not
        return redirect(url_for("login"))

    if request.method == "POST":
        disaster_type = request.form.get("disaster_type")
        stage = request.form.get("stage")

        current_disaster["disaster_type"] = disaster_type
        current_disaster["stage"] = stage

    return render_template("community.html", current_disaster=current_disaster)

if __name__ == "__main__":
    app.run(debug=True)
