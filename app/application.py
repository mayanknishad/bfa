"""
Configuration for Flask App
"""

from flask import Flask, url_for
from flask_cors import CORS

app = Flask(__name__)
    
from app.config import configure_app
configure_app(app)

from app.database_setup import init_db
security_bp = init_db(app)

from app.admin_setup import configure_admin
admin = configure_admin(app)

from flask_admin import helpers as admin_helpers

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security_bp.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )



CORS(app, resources={r'*': {'origins': app.config['CROSS_DOMAIN']}})

# Importing all necessary API endpoints
from app import routes
from app import routes_advisors
from app import routes_client
from app import frontend_api
from app import routes_select_forms_autocomplete
