"""
this is a comment
API endpoints for Flask App relating to select forms
"""

from app.application import app
from app.status import Status
from app.models import db, Advisor, BigFirm, Specialty, Subspecialty, Occupation
from flask import jsonify, request
import sys


@app.route('/api/checkemail', methods=['POST'])
def check_if_email_exists():
    """
    This endpoint takes an email and checks if an advisor already exists
    with that email. Should be used to check whether an applicant can apply
    with a certain email.
    Returns true if an advisor with that email already exists, false if not.
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'})
        email_to_check = data.get('email', None)
        if email_to_check is None:
            return jsonify({'error': 'email not provided'})

        found_advisor = db.session.query(Advisor).filter_by(email=email_to_check).first()
        if found_advisor is None: # no advisor was found with that email
            return jsonify({'result': False}), Status.COMPLETED
        else: # we found an advisor with that email
            return jsonify({'result': True}), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD


@app.route('/api/autocomplete/bigfirms', methods=['POST'])
def get_bigfirms_sl():
    """
    Returns the name and ID of all bigfirms
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        search = data.get('search')
        if search is None:
            return jsonify({'error': 'search was not given'}), Status.BAD

        bigfirms = db.session.query(BigFirm).filter(BigFirm.name.ilike("%" + search + "%")).all()

        response = jsonify({
            "items": [{"id": firm.pk_id,
                       "name": firm.name } for firm in bigfirms],
            "itemCount": len(bigfirms)
            })

        db.session.close()
        return response, Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/autocomplete/subspecialties', methods=['POST'])
def get_subspecialties_sl():
    """
    Returns the name and ID of all subspecialties under a given specialty
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        search = data.get('search')
        if search is None:
            return jsonify({'error': 'search was not given'}), Status.BAD

        subspecialties = db.session.query(Subspecialty).filter(Specialty.name.ilike("%" + search + "%")).filter(Subspecialty.count > 4 ).all()

        response = jsonify({
            "items": [{"id": subspec.pk_id,
                       "name": subspec.name } for subspec in subspecialties],
            "itemCount": len(subspecialties)
            })

        db.session.close()
        return response, Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/selectlists/specialties', methods=['POST'])
def get_specialties_sl():
    """
    Returns the name and ID of all specialties
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        occupation_id = data.get('occupationId')
        if occupation_id is None:
            return jsonify({'error': 'occupationId was not given'}), Status.BAD

        occupation = Occupation.query.get(occupation_id)

        response = jsonify({
            "items": [{"id": spec.pk_id,
                       "name": spec.name } for spec in occupation.specialties],
            "itemCount": len(occupation.specialties)
            })

        db.session.close()
        return response, Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD


@app.route('/api/selectlists/occupations', methods=['GET'])
def get_occupations_sl():
    """
    Returns the name and ID of all occupations
    """
    try:
        occupations = db.session.query(Occupation).all()

        response = jsonify({
            "items": [occupation.to_json() for occupation in occupations],
            "itemCount": len(occupations)
            })

        db.session.close()
        return response, Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD