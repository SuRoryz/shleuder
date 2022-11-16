from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, request, jsonify
from parser import Parser
from json import loads, dumps

app = Flask(__name__, static_folder='static', template_folder='templates')
socketio = SocketIO(app)
ps = Parser()

ps.parse("primer3.doc")

def socket_wrapper(event):
    def wraps(f):
        def wraps_(*args, **kwargs):
            if hasattr(request, "stat"):
                emit(event, {"status": 0, "items": []})
            else:
                try:
                    f(*args, **kwargs)
                except Exception as e:
                    print(e)
                    emit(event, {"status": 2, "items": [str(e)]})
                    
        return wraps_
    return wraps

@app.route("/API/GET_SHLEUDE")
def api_shleude():
    return jsonify(ps.shleude)

@socketio.on('API:GET_SHLEUDE')
def get_shleude(data):
    emit('API:GET_SHLEUDE', dumps(ps.shleude))

socketio.run(app, debug=False, host="0.0.0.0", port=100)