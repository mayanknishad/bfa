"""
API endpoints for Flask App relating to client only routes
"""

from app.application import app
from app.status import Status
from app.models import db, AdminLogin, Role, AdvisorApplicant, Advisor, Project, BigFirm, Specialty, Subspecialty
from flask import jsonify, request, flash, redirect
from flask_security import current_user
from app.admin_dashboard import user_has_permission
import datetime
import sys