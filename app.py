from flask import Flask, render_template, request, redirect, url_for, session

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
    if request.method == "POST":
        resident_name = request.form.get("resident_name")
        zone = request.form.get("zone")
        need_type = request.form.get("need_type")
        urgency = request.form.get("urgency")
        phone_number = request.form.get("phone_number")

        return redirect(url_for("home"))
    return render_template("request.html")


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