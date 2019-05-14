from flask import session, request
from flask_socketio import emit, join_room
from .. import socketio


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room, include_self=False)


@socketio.on('message')
def on_message(msg):
    print(msg)


@socketio.on('forward')
def forward(message):
    print(message)
    socketio.emit('forward')


@socketio.on('left')
def left(message):
    socketio.emit('left')


@socketio.on('right')
def right(message):
    socketio.emit('right')


@socketio.on('lift')
def lift(message):
    socketio.emit('lift')


@socketio.on('drop')
def drop(message):
    socketio.emit('drop')


@socketio.on('stop')
def stop(message):
    socketio.emit('stop')
