"""
API endpoints for Flask App
"""

from app.application import app
from app.status import Status
from flask import jsonify

@app.route('/api/segment')
def API_segment():
    return jsonify({'Segment':'No Key Available Yet'}), Status.COMPLETED
