from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
import pickle
import numpy as np
import json
import glob
import os

list_of_models = glob.glob('./model/*.pickle') # * means all if need specific format then *.csv
latest_model = max(list_of_models, key=os.path.getctime)
# print(latest_model)

app = Flask(__name__)
api = Api(app)

# Create parser for the payload data
parser = reqparse.RequestParser()
parser.add_argument('data')

def prepare_input(data):
    tmp = json.loads(data)
    X = []
    for key in tmp:
        if isinstance(tmp[key]["value"], int):
            X.append(tmp[key]["value"])
        else:
            if tmp[key]["value"] == 'M':
                X.extend([0, 0, 1, 0])
            if tmp[key]["value"] == 'D':
                X.extend([1, 0, 0, 0])
            if tmp[key]["value"] == 'W':
                X.extend([0, 0, 0, 1])
            if tmp[key]["value"] == 'L':
                X.extend([0, 1, 0, 0])
    return X

def parse_result(prediction, prediction_probs):
    # Away Team Win: 0, Dual: 1, Home Team Win: 2
    result = ''
    if prediction[0] == 0:
        result = "{'result': 'Away Team Win',"
    if prediction[0] == 1:
        result = "{'result': 'Duel',"
    if prediction[0] == 2:
        result = "{'result': 'Home Team Win',"
    return result + "winning_probability:{" + f"away_team:{prediction_probs[0][1]}, dual:{prediction_probs[0][1]}, home_team:{prediction_probs[0][2]}" + "}"

# Define how the api will respond to the post requests
class MatchPrediction(Resource):
    def post(self):
        args = parser.parse_args()
        data = args["data"]
        data = data.replace("'", "\"")
        print(data)
        X = prepare_input(data)
        print(X)
        print(type(X))
        X = np.array(X)
        X = X.reshape(1, -1)
        print(X)
        prediction = model.predict(X)
        prediction_probs = model.predict_proba(X)
        print(prediction_probs)
        result = parse_result(prediction, prediction_probs)
        return jsonify(result)

api.add_resource(MatchPrediction, '/prediction')

if __name__ == '__main__':
    # Load model
    with open(latest_model, 'rb') as f:
        model = pickle.load(f)

    app.run(debug=True)
