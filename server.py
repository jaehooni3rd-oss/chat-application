from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit, join_room
import json
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 파일 로드
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

try:
    with open("messages.json", "r") as f:
        messages = json.load(f)
except:
    messages = []

rooms = ["main"]

# 저장 함수
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

def save_messages():
    with open("messages.json", "w") as f:
        json.dump(messages, f)

# HTML 제공
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 회원가입
@socketio.on("register")
def register(data):
    id = data["id"]
    pw = data["pw"]

    if id in users:
        emit("login_fail", "이미 존재하는 아이디")
    else:
        users[id] = pw
        save_users()
        emit("register_success")

# 로그인
@socketio.on("login")
def login(data):
    id = data["id"]
    pw = data["pw"]

    if id in users and users[id] == pw:
        emit("login_success", id)
    else:
        emit("login_fail", "아이디 또는 비밀번호 오류")

# 방 목록
@socketio.on("get_rooms")
def get_rooms():
    emit("room_list", rooms)

# 방 생성
@socketio.on("create_room")
def create_room(room):
    if room not in rooms:
        rooms.append(room)
    socketio.emit("room_list", rooms)

# 방 입장
@socketio.on("join_room")
def handle_join(room):
    join_room(room)
    room_msgs = [m for m in messages if m.get("room") == room]
    emit("load_messages", room_msgs)

# 메시지
@socketio.on("send_message")
def handle_message(data):
    msg = {
        "user": data["user"],
        "text": data["text"],
        "room": data["room"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    messages.append(msg)
    save_messages()

    socketio.emit("new_message", msg)

# 채팅 초기화
@socketio.on("reset_chat")
def reset_chat(room):
    global messages
    messages = [m for m in messages if m.get("room") != room]
    save_messages()
    socketio.emit("load_messages", [])

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)