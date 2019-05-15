import json

from flask import request
from flask_socketio import emit, join_room, leave_room

from .. import socketio
from app.enums import Commands

"""
Variables to keep track socket id and IP address of each robots and users
"""
robots = dict()
users = dict()

"""
rooms (dict): Control which one is controlling which robot
key: robot's sid
value: user's sid if connected else None

"""
rooms = dict()


@socketio.on('connect')
def on_connect():
    print('New connection from SID: {}  ||  IP: {}:{}'
          .format(request.sid, request.remote_addr, request.environ.get('REMOTE_PORT')))


@socketio.on('join')
def on_join(data):
    if not isinstance(data, dict):
        emit('message', {'content': 'Invalid request data'})
        return

    from_ = data.get('from')
    if not from_:
        emit('message', {'content': 'Invalid request data'})
        return

    if from_ == 'robot':
        _handle_robot_connection()
    elif from_ == 'user':
        _handle_user_connection()


def _handle_robot_connection():
    """Whenever a robot connects to server, it joins a room of its socket id"""
    sid = request.sid
    ip_addr = '{}:{}'.format(request.remote_addr, request.environ.get('REMOTE_PORT'))
    robots[sid] = ip_addr
    rooms[sid] = None
    join_room(sid)


def _handle_user_connection():
    """Connect user to a free robot, otherwise sending message informing no no robot connected"""
    sid = request.sid
    ip_addr = '{}:{}'.format(request.remote_addr, request.environ.get('REMOTE_PORT'))
    users[sid] = ip_addr
    if not robots:
        emit('message', {'content': 'There is no available robot to connect'})
        return
    for robot_sid, user_sid in rooms.items():
        if not user_sid:
            rooms[robot_sid] = sid
            join_room(robot_sid)
            emit('message', {'content': 'User and robot are connected'}, room=robot_sid)
            return

    emit('message', {'content': 'Connection failed. All robots are under control'})


@socketio.on('disconnect')
def on_disconnection():
    """Handling robot and user disconnection
    Robot disconnection: Leave it from current room, delete corresponding key in rooms variable
    User disconnection: Set the connected robot free
    """
    sid = request.sid
    if sid in robots:
        connected_user_sid = rooms[sid]
        if connected_user_sid:
            emit('message', {'content': 'Robot has been disconnected'}, sid=connected_user_sid)
            leave_room(sid)
            rooms.pop(sid)
            robots.pop(sid)
    elif sid in users:
        for robot_sid, user_sid in rooms.items():
            if user_sid == sid:
                emit('message', {'content': 'Controlling user has been disconnected'}, room=robot_sid)
                leave_room(robot_sid)
                rooms[robot_sid] = None
                users.pop(sid)


def _send_command(command):
    """Forward command to both user and connected robot"""
    for robot_sid, user_sid in rooms.items():
        if user_sid == request.sid:
            socketio.emit(command, room=robot_sid)
            return
    emit('message', {'content': 'You does not connect to any robot'})


@socketio.on('forward')
def forward(*args, **kwargs):
    _send_command(Commands.FORWARD)


@socketio.on('backward')
def backward(*args, **kwargss):
    _send_command(Commands.BACKWARD)


@socketio.on('left')
def left(*args, **kwargs):
    _send_command(Commands.LEFT)


@socketio.on('right')
def right(*args, **kwargs):
    _send_command(Commands.RIGHT)


@socketio.on('lift')
def lift(*args, **kwargs):
    _send_command(Commands.LIFT)


@socketio.on('drop')
def drop(*args, **kwargs):
    _send_command(Commands.DROP)


@socketio.on('auto')
def auto_run(*args, **kwargs):
    _send_command(Commands.AUTO_RUN)


@socketio.on('stop')
def stop(*args, **kwargs):
    _send_command(Commands.STOP)
