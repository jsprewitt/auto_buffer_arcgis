from flask import Flask, render_template, url_for, request, redirect, session
from gis_functions import update_buffers
from record_bird_edits import record_bird_edits
from record_grid_edits import record_grid_edits, record_current_state, email_days_work
from generate_access_token import generate_access_token
from send_email import send_emails

app = Flask(__name__)
app.secret_key = "#######"

@app.route('/')
def index():
    return ({200: "OK"}, 200)

@app.route('/run')
def run_functions():
    token = generate_access_token()
    survey_layer = "https://services8.arcgis.com/###########/FeatureServer/0/"
    buffer_layer = "https://services8.arcgis.com/###########/FeatureServer/0/"
    status_code = 200
    try:
        b = update_buffers(token, survey_layer, buffer_layer)
        pass
    except Exception as e:
        b = e
        status_code = 500
    try:
        r = record_bird_edits(token, survey_layer, "TNC205AutoUpload", "Edits")
    except Exception as e:
        r = e
        status_code = 500
    return ({status_code: f"Deleted {b[0]} buffers, added {b[1]} buffers. Recorded {r} bird survey edits."}, status_code)

@app.route('/grid')
def grid_functions():
    token = generate_access_token()
    field_grid_layer = "https://services8.arcgis.com/###############/FeatureServer/0/"
    try:
        c = record_current_state(token, field_grid_layer, 'TNC205_FieldGrid', 'CurrentGrid')
        e = record_grid_edits(token, field_grid_layer, 'TNC205_FieldGrid', 'Edits')
    except Exception as e:
        return ({500: e}, 500)
    return ({200: f"Grid currently has {c} tiles, recorded {e} edits"}, 200)

@app.route('/grid_status', methods=["GET"])
def grid_status():
    emails = []
    try:
        if request.method == "GET":
            emails = request.args.get('emails').split(',')
        token = generate_access_token()
        field_grid_layer = "https://services8.arcgis.com/###################/FeatureServer/0/"
        subject, body = email_days_work(token, field_grid_layer)
        if emails:
            send_emails(emails, subject, body)
        return ({200: body}, 200)
    except Exception as e:
        return ({500: e}, 500)

if __name__ == "__main__":
    app.run(debug=False)
