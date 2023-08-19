from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta
import heapq

app = Flask(__name__)

JOHN_DOE_API_BASE = "http://20.244.56.144/train"
ACCESS_CODE = "hMkCJZ   "
API_KEY = "your_api_key_here"

def get_authenticated_token():
    response = requests.post(f"{JOHN_DOE_API_BASE}/register", data={"access_code": ACCESS_CODE})
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception("Authentication failed")

def fetch_train_data(auth_token):
    now = datetime.now()
    end_time = now + timedelta(hours=12)

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{JOHN_DOE_API_BASE}/trains", headers=headers)
    train_data = response.json()

    upcoming_trains = [
        train for train in train_data
        if now + timedelta(minutes=30) <= datetime.fromisoformat(train["departure_time"]) <= end_time
    ]

    return upcoming_trains

@app.route('/trains', methods=['GET'])
def get_ordered_train_schedules():
    try:
        auth_token = get_authenticated_token()
        train_data = fetch_train_data(auth_token)
        
        # Create a priority queue to sort the trains
        heap = []
        for train in train_data:
            heapq.heappush(heap, (train["ac_price"], -train["ac_availability"], -train["delay_minutes"], train))

        response = []
        while heap:
            _, _, _, train = heapq.heappop(heap)
            response.append({
                "train_number": train["train_number"],
                "departure_time": train["departure_time"],
                "sleeper_availability": train["sleeper_availability"],
                "sleeper_price": train["sleeper_price"],
                "ac_availability": train["ac_availability"],
                "ac_price": train["ac_price"],
                "delay_minutes": train["delay_minutes"]
            })

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
