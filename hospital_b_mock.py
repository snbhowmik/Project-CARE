import os
import time
import json

# The folder we use to communicate
MAILBOX_DIR = "federated_data"
QUERY_FILE = os.path.join(MAILBOX_DIR, "query.json")
ANSWER_FILE = os.path.join(MAILBOX_DIR, "answer.json")

# The "expert knowledge" from the Data Architect
HOSPITAL_B_KNOWLEDGE = {
    "SINGLE_BITE_VS_MULTI_BITE_RISK": "Our data confirms single bite cases show faster onset of neurotoxicity. Prioritize this patient immediately."
}

def answer_query():
    print("[City General Hospital] Query received. Analyzing...")
    with open(QUERY_FILE, 'r') as f:
        query_data = json.load(f)

    # Simple logic to answer the known question
    question_code = query_data.get("question_code")
    if question_code in HOSPITAL_B_KNOWLEDGE:
        response = {
            "answering_hospital": "City General Mock Hospital",
            "query_id": query_data.get("query_id"),
            "response_text": HOSPITAL_B_KNOWLEDGE[question_code]
        }
        
        with open(ANSWER_FILE, 'w') as f:
            json.dump(response, f)
            
        print("[City General Hospital] Response sent.")
    
    os.remove(QUERY_FILE)

if __name__ == "__main__":
    print("[City General Hospital] Mock Interface is ONLINE. Watching for queries...")
    if not os.path.exists(MAILBOX_DIR):
        os.makedirs(MAILBOX_DIR)
        
    while True:
        if os.path.exists(QUERY_FILE):
            answer_query()
        time.sleep(2) # Check every 2 seconds