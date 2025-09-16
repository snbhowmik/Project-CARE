import csv
import random
import time
import uuid
import threading
from datetime import datetime, timedelta
from functools import wraps
from cherrypy import url
from flask import Flask, json, jsonify, request
from flask_cors import CORS
import jwt
import bcrypt
import requests
from pydantic import ValidationError

# FHIR imports
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.bundle import Bundle
from fhir.resources.reference import Reference
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.group import Group, GroupMember
from fhir.resources.flag import Flag
import subprocess

# ==============================================================================
# SETUP
# ==============================================================================
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'sak8uyxslkdpf9udsa9lkfds9.sdsaghyugehdsafhgdsafdytf'
FHIR_SERVER_BASE = "http://localhost:8080/fhir"

# Mock user database
MOCK_USERS = {
    "doctor1": {
        "password_hash": "$2b$12$NCxtuAdBj2HOtSQW19wwrexSPam9mUAV4DwFD5t7p2UJFWnUhMQSu", # Hash for "password123"
        "full_name": "Dr. Ravi Kumar",
    }
}

# ========== NEW: JSON Database for Groups ==========
GROUPS_DB_FILE = 'groups_db.json'
db_lock = threading.Lock()

# Your auth logic is fine, no changes needed here.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None;
        if 'authorization' in request.headers: token = request.headers['authorization'].split(" ")[1]
        if not token: return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]); current_user = data['user']
        except: return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'): return jsonify({'message': 'Could not verify'}), 401
    username = auth.get('username'); password = auth.get('password').encode('utf-8'); user = MOCK_USERS.get(username)
    if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
        token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(hours=8)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials!'}), 401


# NEW: A map of LOINC codes for the vitals we will simulate
LOINC_CODES = {
    "heart_rate": ("8867-4", "bpm"),
    "spo2": ("59408-5", "%"),
    "respiratory_rate": ("9279-1", "/min"),
    "temperature": ("8310-5", "Cel"),
    "bp_systolic": ("8480-6", "mm[Hg]"),
    "bp_diastolic": ("8462-4", "mm[Hg]"),
    "blood_sugar": ("2339-0", "mg/dL"),
    "sodium": ("2951-2", "mmol/L"),
    "potassium": ("2823-3", "mmol/L"),
    "ph": ("11558-4", "{pH}"),
    "paco2": ("2019-8", "mm[Hg]"),
    "pao2": ("2703-7", "mm[Hg]"),
    "gcs": ("9269-2", "{score}")
}

# NEW: More detailed simulation parameters
SIMULATION_PARAMS = {
    "stable": {
        "heart_rate": (70, 100), "spo2": (96, 99), "respiratory_rate": (12, 18),
        "temperature": (36.5, 37.5), "bp_systolic": (110, 130), "bp_diastolic": (70, 85),
        "blood_sugar": (80, 110), "sodium": (135, 145), "potassium": (3.5, 5.0),
        "ph": (7.35, 7.45), "paco2": (35, 45), "pao2": (80, 100), "gcs": (15, 15)
    },
    "critical": {
        "heart_rate": (140, 165), "spo2": (86, 91), "respiratory_rate": (25, 35),
        "temperature": (38.5, 40.0), "bp_systolic": (80, 95), "bp_diastolic": (50, 65),
        "blood_sugar": (180, 250), "sodium": (125, 135), "potassium": (5.5, 6.5),
        "ph": (7.20, 7.30), "paco2": (50, 60), "pao2": (55, 65), "gcs": (3, 8)
    }
}

active_patients = {}
patient_lock = threading.Lock()
start_time = time.time()

# ==============================================================================
# API Routes (/patient for creation, /patients for retrieval)
# ==============================================================================
# ... (Your existing /patient POST route for creation is fine)
# In app.py

@app.route('/patient', methods=['POST'])
@token_required
def create_patient(current_user):
    """
    Receives new patient data, creates an INACTIVE FHIR Patient resource,
    and saves it to the HAPI FHIR server. Does NOT start simulation.
    """
    data = request.json
    new_patient_id = str(uuid.uuid4())
    try:
        name_data = data.get('name', {})
        address_data = data.get('address', {})
        telecom_data = data.get('telecom', {})

        # CHANGE #1: Explicitly create the full name for the 'text' field.
        given_name = name_data.get('given', '')
        family_name = name_data.get('family', '')
        full_name = f"{given_name} {family_name}".strip()

        patient_args = {
            "id": new_patient_id,
            "active": False,  # Patients are created as inactive by default.
            "name": [HumanName(
                use="official",
                family=family_name,
                given=[given_name],
                text=full_name
            )],
            "gender": data.get('gender'),
            "birthDate": data.get('birthDate')
        }

        if telecom_data.get('value'):
            patient_args['telecom'] = [ContactPoint(system='phone', use='home', value=telecom_data.get('value'))]
        if any(address_data.values()):
            patient_args['address'] = [Address(use="home", line=[address_data.get('line')], city=address_data.get('city'), state=address_data.get('state'), postalCode=address_data.get('postalCode'), country=address_data.get('country'))]

        patient = Patient(**patient_args)
        
        response = requests.put(
            f"{FHIR_SERVER_BASE}/Patient/{new_patient_id}",
            data=patient.model_dump_json(exclude_none=True),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        # CHANGE #2: Removed the logic that automatically added the patient
        # to the live simulation. This now happens only upon activation.
        print(f"[INFO] New INACTIVE patient {new_patient_id} created in FHIR database.")
            
        return jsonify({"message": "Patient created successfully", "id": new_patient_id}), 201

    except ValidationError as e: 
        return jsonify({"message": "Invalid data provided for patient.", "details": e.errors()}), 400
    except requests.exceptions.HTTPError as e: 
        return jsonify({"message": "FHIR server rejected the patient data.", "details": e.response.text}), 502
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in create_patient: {type(e).__name__} - {e}")
        return jsonify({"message": "An unexpected server error occurred."}), 500
    

# NEW: Endpoint to update a patient's active status
@app.route('/patient/<patient_id>/status', methods=['POST'])
@token_required
def update_patient_status(current_user, patient_id):
    data = request.json
    new_status = data.get('active')
    if new_status is None:
        return jsonify({"message": "Missing 'active' field"}), 400

    try:
        # 1. Get the current patient resource from the FHIR server
        get_response = requests.get(f"{FHIR_SERVER_BASE}/Patient/{patient_id}")
        get_response.raise_for_status()
        patient_json = get_response.json()
        
        # 2. Update the status
        patient_json['active'] = new_status
        
        # 3. PUT the updated resource back
        put_response = requests.put(
            f"{FHIR_SERVER_BASE}/Patient/{patient_id}",
            json=patient_json,
            headers={'Content-Type': 'application/json'}
        )
        put_response.raise_for_status()
        if new_status: # If patient is being activated 
            with patient_lock:
                if patient_id not in active_patients:
                    active_patients[patient_id] = { "state": "stable" }
                    print(f"[INFO] Patient {patient_id} ACTIVATED and added to simulation.")
        else: # If patient is being deactivated
            with patient_lock:
                if patient_id in active_patients:
                    del active_patients[patient_id]
                    print(f"[INFO] Patient {patient_id} DEACTIVATED and removed from simulation.")
        
        return jsonify({"message": "Patient status updated successfully"}), 200

        print(f"[INFO] Updated patient {patient_id} active status to {new_status}")
        return jsonify({"message": "Patient status updated successfully"}), 200

    except requests.exceptions.HTTPError as e:
        return jsonify({"message": "FHIR server error.", "details": e.response.text}), 502
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in update_patient_status: {e}")
        return jsonify({"message": "An unexpected server error occurred."}), 500

# /patients GET route 

@app.route('/patients')
@token_required
def get_patients_fhir(current_user):
    try:
        url = f"{FHIR_SERVER_BASE}/Patient?active=true&_revinclude=Observation:subject"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to the FHIR data store"}), 500
    

@app.route('/patients/search', methods=['GET'])
@token_required
def search_patients(current_user):
    """Searches for patients by name (case-insensitive, partial match)."""
    search_name = request.args.get('name', '')
    if not search_name:
        # Return an empty bundle if no search term is provided
        return jsonify(Bundle(type="searchset", total=0, entry=[]).model_dump())

    try:
        # Use the FHIR ':contains' modifier for a partial search
        url = f"{FHIR_SERVER_BASE}/Patient?name:contains={search_name}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to the FHIR data store"}), 500
    
# ==============================================================================
# SIMULATION LOGIC (Heavily updated)
# ==============================================================================
def create_observation(patient_id, loinc_code, unit, value):
    """Helper function to create a FHIR Observation resource."""
    obs = Observation(
        status="final", 
        category=[CodeableConcept(coding=[Coding(system="http://terminology.hl7.org/CodeSystem/observation-category", code="vital-signs")])], 
        code=CodeableConcept(coding=[Coding(system="http://loinc.org", code=loinc_code)]), 
        subject=Reference(reference=f"Patient/{patient_id}"), 
        effectiveDateTime=datetime.now().isoformat() + "Z", 
        valueQuantity=Quantity(value=value, unit=unit)
    )
    return obs

def update_vitals_periodically():
    while True:
        with patient_lock:
            # Check for any new patients and initialize their state
            for pat_id in list(active_patients.keys()):
                if "state" not in active_patients[pat_id]:
                    active_patients[pat_id]["state"] = "stable"

            current_patients_to_simulate = list(active_patients.keys())

        if not current_patients_to_simulate:
            time.sleep(1); continue

        # Crisis event logic: sets the first patient's state to "critical"
        first_patient_id = current_patients_to_simulate[0]
        if "state" in active_patients.get(first_patient_id, {}) and active_patients[first_patient_id]["state"] == "stable" and (time.time() - start_time) > 30:
            print(f"[CRISIS EVENT] Triggering crisis for patient {first_patient_id}...")
            with patient_lock:
                active_patients[first_patient_id]["state"] = "critical"
        
        for pat_id in current_patients_to_simulate:
            with patient_lock:
                patient_state = active_patients.get(pat_id, {}).get("state")
            if not patient_state: continue

            params = SIMULATION_PARAMS[patient_state]
            
            # Generate and post an observation for each parameter
            for key, (loinc, unit) in LOINC_CODES.items():
                min_val, max_val = params[key]
                
                # Use float for most values, int for GCS/Resp Rate
                is_float = key not in ["gcs", "respiratory_rate"]
                
                mean = (min_val + max_val) / 2
                std_dev = (max_val - min_val) / 4
                
                if is_float:
                    val = round(random.gauss(mean, std_dev), 1)
                else:
                    val = int(random.gauss(mean, std_dev))

                # Create and post the observation
                obs = create_observation(pat_id, loinc, unit, val)
                try:
                    requests.post(f"{FHIR_SERVER_BASE}/Observation", data=obs.model_dump_json(exclude_none=True), headers={'Content-Type': 'application/json'}).raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"Failed to post {key} for patient {pat_id}: {e}")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Posted new full vital panels for {len(current_patients_to_simulate)} active patient(s).")
        time.sleep(10) # Update every 10 seconds to avoid spamming the server



def read_groups_db():
    with db_lock:
        with open(GROUPS_DB_FILE, 'r') as f:
            return json.load(f)

def write_groups_db(data):
    with db_lock:
        with open(GROUPS_DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
# ==============================================================================
# Group Management API Endpoints
# ==============================================================================
@app.route('/group', methods=['POST'])
@token_required
def create_group(current_user):
    """Creates a new group in the groups_db.json file."""
    data = request.json
    if not data.get("name"):
        return jsonify({"message": "Group name is required."}), 400
    
    new_group = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "type": data.get("type", "general"),
        "active": True,
        "members": [],
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }
    
    db_data = read_groups_db()
    db_data['groups'].append(new_group)
    write_groups_db(db_data)
    
    return jsonify(new_group), 201

@app.route('/groups', methods=['GET'])
@token_required
def get_groups(current_user):
    """Lists all groups from the groups_db.json file, sorted by creation date."""
    db_data = read_groups_db()
    # Sort groups by createdAt timestamp, newest first
    sorted_groups = sorted(db_data['groups'], key=lambda g: g['createdAt'], reverse=True)
    return jsonify({"entry": [{"resource": group} for group in sorted_groups]})

@app.route('/group/<group_id>/status', methods=['POST'])
@token_required
def update_group_status(current_user, group_id):
    """Activates or deactivates a group in the groups_db.json file."""
    data = request.json
    new_status = data.get('active')
    
    db_data = read_groups_db()
    group_found = False
    for group in db_data['groups']:
        if group['id'] == group_id:
            group['active'] = new_status
            group_found = True
            break
    
    if group_found:
        write_groups_db(db_data)
        return jsonify({"message": "Group status updated successfully"}), 200
    else:
        return jsonify({"message": "Group not found"}), 404
        
@app.route('/group/<group_id>/members', methods=['POST'])
@token_required
def add_group_member(current_user, group_id):
    """Adds a patient to an existing FHIR Group in the HAPI FHIR DB."""
    data = request.json
    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"message": "patient_id is required"}), 400
    try:
        # 1. Fetch the existing Group from the FHIR DB
        get_response = requests.get(f"{FHIR_SERVER_BASE}/Group/{group_id}")
        get_response.raise_for_status()
        group = Group(**get_response.json())

        # 2. Add a new member to the Group object in memory
        if group.member is None:
            group.member = []
        
        # Avoid adding duplicate members
        if not any(member.entity.reference == f"Patient/{patient_id}" for member in group.member):
            new_member = GroupMember(entity=Reference(reference=f"Patient/{patient_id}"))
            group.member.append(new_member)
        
        # 3. Save the entire updated Group object back to the FHIR DB
        put_response = requests.put(
            f"{FHIR_SERVER_BASE}/Group/{group_id}", 
            data=group.model_dump_json(exclude_none=True), 
            headers={'Content-Type': 'application/json'}
        )
        put_response.raise_for_status()
        return jsonify(put_response.json()), 200
    except Exception as e:
        return jsonify({"message": f"Error adding member: {e}"}), 500

# ==============================================================================
# AUTOMATION LOGIC (UPDATED)
# ==============================================================================
def run_group_analysis_periodically():
    analyzed_groups = set()
    while True:
        time.sleep(15)
        print("[AUTOMATION] Checking for groups to analyze from JSON DB...")
        try:
            db_data = read_groups_db()
            for group in db_data['groups']:
                group_id = group["id"]
                
                # Trigger: Active "snakebite" group with 2+ members, not yet analyzed
                if group["active"] and group["type"] == "snakebite" and len(group["members"]) >= 2 and group_id not in analyzed_groups:
                    print(f"[AUTOMATION] TRIGGERED: Analyzing Group/{group_id}")
                    
                    # This part remains the same: it runs the Docker container
                    # and saves the resulting Flag to the REAL HAPI FHIR server.
                    result_json = subprocess.check_output(["docker", "run", "--rm", "care-analyzer"]).decode("utf-8")
                    result = json.loads(result_json)
                    
                    flag = Flag(
                        status="active",
                        category=[CodeableConcept(text="Clinical Alert")],
                        code=CodeableConcept(text=result["insight_text"]),
                        subject=Reference(reference=f"Patient/{result['patient_id']}")
                    )
                    
                    requests.post(f"{FHIR_SERVER_BASE}/Flag", data=flag.model_dump_json(), headers={'Content-Type': 'application/json'})
                    print(f"[AUTOMATION] ANALYSIS COMPLETE: Created Flag for Patient/{result['patient_id']}")
                    analyzed_groups.add(group_id)

        except Exception as e:
            print(f"[AUTOMATION ERROR] {e}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    # ... (Your existing startup logic)
    print("[INFO] C.A.R.E. Gateway started (using JSON DB for Groups).")
    
    # Start the simulation thread
    simulation_thread = threading.Thread(target=update_vitals_periodically, daemon=True)
    simulation_thread.start()
    print("[INFO] Real-time vital signs simulation thread started.")
    
    # Start the group analysis thread
    analysis_thread = threading.Thread(target=run_group_analysis_periodically, daemon=True)
    analysis_thread.start()
    print("[INFO] Group analysis automation thread started.")

    app.run(host='0.0.0.0', port=5000)