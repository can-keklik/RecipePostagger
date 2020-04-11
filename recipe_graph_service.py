from flask import Flask
from flask import request
import json
app = Flask(__name__)

@app.route('/')
def help():
    return 'POST to /graphviz'

@app.route('/graphviz', methods = ['GET', 'POST'])
def graphviz():
    return json.dumps(request.form)

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)