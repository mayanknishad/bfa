"""
API endpoints for Flask App
"""

from app.application import app
from app.status import Status
from app.models import db, AdvisorApplicant, Advisor, BigFirm, Specialty, Occupation, Promotion, Vendor
from flask import jsonify, request, flash, redirect
from flask_security import current_user
from app.admin_dashboard import user_has_permission
from sqlalchemy.sql.expression import and_
import boto3
import datetime
import sys
from sqlalchemy.sql.expression import or_

from pprint import pprint


@app.route('/')
def index():
    try:
        return jsonify({'Status': 'up'}), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/refer')
def refer():
    try:
        return jsonify({'Status': 'In Development'}), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD
@app.route('/api/mail')
def mail():
    try:
        return jsonify({'Status': 'In Development'}), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD


@app.route('/api/contactus', methods=['POST'])
def contact_us():
    """
    Takes a source email address and a message and sends that to the admin
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD


        required_fields = ['name', 'senderEmail', 'message']
        for r_field in required_fields:
            if data.get(r_field, None) is None or data.get(r_field) == '':
                return jsonify({'error': r_field + ' was not given'}), Status.BAD

        ses = boto3.client('ses',
                           aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                           region_name=app.config['AWS_REGION_NAME'])
        ses.send_email(Source=app.config['AWS_SES_SOURCE_EMAIL'], # should be the SES email designated for sending emails
                       Message={
                                    'Subject': {
                                        'Charset': 'UTF-8',
                                        'Data': data.get('name') + ': ' + data.get('subject', 'No Subject')
                                    },
                                    'Body': {
                                        'Text': {
                                            'Charset': 'UTF-8',
                                            'Data': data.get('message')
                                        }
                                    }
                                },
                       Destination={
                                       'ToAddresses': [app.config['AWS_SES_TARGET_EMAIL']] # should be set to the admin email
                                   },
                       ReplyToAddresses=[data.get('senderEmail')]) # set to the sender's email so replies are sent there
        return jsonify({}), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD



@app.route('/api/apply', methods=['POST'])
def create_applicant():
    """
    Creates an application.
    Frontend will supply all LinkedIn data after calling the API.
    """
    # try:
    data = request.get_json()
    if  data is None:
        return jsonify({"error": "Error inserting applicant"}), Status.BAD

    # Application data

    email = data.get('email',None)
    if email is None:
        return jsonify({"error": "No email entered"}), Status.BAD

    # Name is one argument, and we split it into first and last name manually
    # Anything after the first name is placed in the last name field
    names = data.get('name', '').strip().split(" ", 1)
    if len(names) != 2:
        return jsonify({"error": "Invalid name entered"}), Status.BAD

    email_exists = bool(AdvisorApplicant.query.filter_by(email=email).first())

    if email_exists:
        return jsonify({'error': 'Applicant email already exists'}), Status.BAD

    pprint(data)

    new_applicant = AdvisorApplicant()

    new_applicant.first_name = names[0]
    new_applicant.last_name = names[1]
    new_applicant.email = email
    new_applicant.how_they_found = data.get('howTheyFound','')
    new_applicant.referral_user = data.get('referralUser','')
    new_applicant.recommended_advisors = data.get('recommendedAdvisors','')
    new_applicant.years_of_experience = data.get('yearsOfExperience')
    new_applicant.years_of_bigfirm_experience = data.get('yearsOfBigFirmExperience')

    new_applicant.specialties = [Specialty.query.get(specialty_id) for specialty_id
                                                                   in data.get('specialtyId', [])]
    new_applicant.subspecialties_text = data.get('subspecialtyText', '')

    new_applicant.occupation_id = data.get('occupationId',None)
    new_applicant.location = data.get('location', '')
    new_applicant.city = data.get('city')
    new_applicant.state = data.get('state')

    new_applicant.short_bio = data.get('biography', '')

    new_applicant.current_firm = data.get('currentFirm', '')
    new_applicant.current_firm_size = data.get('currentFirmSize', 0)
    new_applicant.current_firm_revenue =  data.get('currentFirmRevenue', 0)
    new_applicant.undergrad_education = data.get('undergradEducation', '')
    new_applicant.grad_education = data.get('gradEducation','')
    new_applicant.billing_rate = data.get('billingRate','')

    new_applicant.work_of_interest = data.get('workOfInterest')
    new_applicant.new_client_engagement = data.get('newClientAvailability')


    new_applicant.company_url = data.get('currentFirmWebsite','')

    # LinkedIn Data
    new_applicant.linkedin_url = data.get('linkedInUrl','')
    new_applicant.linkedin_first_name = data.get('linkedInFirstName','')
    new_applicant.linkedin_last_name = data.get('linkedInLastName','')
    new_applicant.linkedin_maiden_name = data.get('linkedInMaidenName','')
    new_applicant.linkedin_formatted_name = data.get('linkedInFormattedName','')
    new_applicant.linkedin_phonetic_first_name = data.get('linkedInPhoneticFirstName','')
    new_applicant.linkedin_phonetic_last_name = data.get('linkedInPhoneticLastName','')
    new_applicant.linkedin_headline = data.get('linkedInHeadline','')
    new_applicant.linkedin_location = data.get('linkedInLocation','')
    new_applicant.linkedin_industry = data.get('linkedInIndustry','')
    new_applicant.linkedin_summary = data.get('linkedInSummary','')
    new_applicant.linkedin_specialities = data.get('linkedInSpecialties','')
    new_applicant.linkedin_positions = data.get('linkedInPositions','')
    new_applicant.linkedin_picture_url = data.get('linkedInPictureUrl','')
    new_applicant.linkedin_picture_url_orig = data.get('linkedInPictureUrlOrig','')
    new_applicant.linkedin_site_standard_profile_request = data.get('linkedInSiteStandardProfileRequest','')
    new_applicant.linkedin_api_standard_profile_request = data.get('linkedInApiStandardProfileRequest','')
    new_applicant.linkedin_public_profile_url = data.get('linkedInPublicProfileUrl','')

    new_applicant.previous_firms = [BigFirm.query.get(f) for f in data.get('previousFirmId', [])]


    db.session.add(new_applicant)
    if new_applicant not in db.session:
        db.session.rollback()
        db.session.close()
        return jsonify({"error": "Error inserting applicant"}), Status.BAD

    db.session.commit()

    if db.session.query(AdvisorApplicant).filter_by(pk_id=new_applicant.pk_id).first() is None:
        db.session.close()
        return jsonify({"error": "Error inserting applicant"}), Status.BAD
    else:
        db.session.close()
        return jsonify({}), Status.COMPLETED


@app.route('/api/approveapplicant', methods=['POST'])
def action_approve():
    print('action')
    try:
        if not current_user.is_active or not current_user.is_authenticated \
          or not user_has_permission(current_user, 'can_edit_advisorapplicants') \
            or not user_has_permission(current_user, 'can_create_advisors'):
            flash("You do not have permission to approve applicants.")
            return redirect("/admin/advisorapproval")

        data = request.form
        if data is None:
            flash("No form data was given.")
            return redirect("/admin/advisorapproval")

        welcome_message = data.get('welcomeMessage', '')
        if welcome_message == '':
            flash("Welcome message cannot be empty.")
            return redirect("/admin/advisorapproval")

        id = data.get('Advisor Applicant', None)
        query = AdvisorApplicant.query.filter_by(pk_id=id)
        count = 0
        applicant = query.first()

        if applicant is None:
            flash("Applicant not found.")
            return redirect("/admin/advisorapproval")

        # else
        if applicant.approve(welcome_message):
            flash("User named {} {} was successfully approved.\n Welcome message: {}".format(applicant.first_name, \
                applicant.last_name, welcome_message))
        else:
            flash("An error occurred while approving the user named {} {}.".format(applicant.first_name, \
                applicant.last_name))
        return redirect("/admin/advisorapproval")

    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/prospects/advisors', methods=['POST'])
def prospects_advisor_search():
    """
    Searches for advisors based on the user-given filters.
    It is the endpoint for unauthorized users to use, and it
    returns a less information than the authorized
    "/api/advisors" endpoint.
    """
    try:
        data = request.get_json()

        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD
        # get filter options
        filter_occupation = data.get('occupationId') # will get the pk_id of the occupation
        filter_location = data.get('location') # Name of state
        filter_specialty = data.get('specialty')

        if filter_occupation is None:
            return jsonify({"error": "occupation must be provided"}), Status.BAD

        occupation = Occupation.query.get(filter_occupation)

        if not occupation and not filter_location:
            return jsonify({'error': 'occupation invalid'}), Status.BAD

        filters = [Advisor.status == 'Active']
        if filter_location:
            filters.append(Advisor.state == filter_location)

        if occupation:
            filters.append(Advisor.occupations.contains(occupation))

        if filter_specialty:
            specialty = Specialty.query.get(filter_specialty)
            filters.append(Advisor.specialties.contains(specialty))

        advisors = Advisor.query.filter(and_(*filters)).all() or []

        response = jsonify({
            "items": [{"id": adv.pk_id,
                       "firstName": adv.first_name,
                       "lastInitial": adv.last_name[0],
                       "specialty": [specialty.to_json() for specialty in (adv.specialties or [])],
                       "occupation": [occ.to_json() for occ in (adv.occupations or [])],
                       "previousFirm": [firm.to_json() for firm in (adv.previous_firms or [])],
                       "city": adv.city,
                       "state": adv.state,
                       "yearsOfExperience": adv.years_of_experience_range.value if adv.years_of_experience_range else adv.years_of_experience,
                       "imageUrl": adv.linkedin_picture_url,
                       "bio": adv.biography} for adv in advisors],
            "itemCount": len(advisors)
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

@app.route('/api/prospects/advisordetails', methods=['POST'])
def prospects_advisor_details():
    """
    Returns an individual advisor's full information.
    Takes the pk_id of the advisor and returns all info for them.
    """
    try:
        data = request.get_json()

        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        filter_id = data.get('advisorId', None)
        if filter_id is None:
            return jsonify({'error':'No advisorId provided'})

        found_advisor = db.session.query(Advisor)\
                    .filter(Advisor.status == 'Active', Advisor.pk_id == filter_id).first()

        if found_advisor is not None:
            response = jsonify({"id": found_advisor.pk_id,
                                "email": found_advisor.email,
                                "firstName": found_advisor.first_name,
                                "lastName": found_advisor.last_name[0] if found_advisor.last_name else '',
                                "city": found_advisor.city,
                                "state": found_advisor.state,
                                "location": found_advisor.location,
                                "specialty": [specialty.to_json() for specialty in (found_advisor.specialties or [])],
                                "occupation": [occ.to_json() for occ in (found_advisor.occupations or [])],
                                "previousFirm": [firm.to_json() for firm in (found_advisor.previous_firms or [])],
                                "yearsOfExperience": found_advisor.years_of_experience_range.value if found_advisor.years_of_experience_range else '',
                                "biography": found_advisor.biography,
                                "currentFirm": found_advisor.current_firm.name if found_advisor.current_firm else '',
                                "currentFirmSize": found_advisor.current_firm_size,
                                "currentFirmRevenue": found_advisor.current_firm_revenue,
                                "undergradEducation": found_advisor.undergrad_education,
                                "gradEducation": found_advisor.grad_education,
                                "imageUrl": found_advisor.linkedin_picture_url,
                                "resumeUrl": found_advisor.resume_url} if found_advisor is not None else {})
        else:
            response = jsonify({"error": "No active advisor found with that ID"})

        db.session.close()

        return response, Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v),
                        'line' : str(exc_tb.tb_lineno)
                        }), Status.BAD


@app.route('/api/prospects/advisors/all', methods=['GET'])
def prospects_all_advisors():
    """
    Returns Advisor search page's initial advisors
    :return:
    """
    query = Advisor.query.filter_by(status='Active').order_by(Advisor.date_accepted.desc())
    total_advisors = query.count()
    advisors = query.limit(9)
    return jsonify({
            "items": [{"id": adv.pk_id,
                       "firstName": adv.first_name,
                       "lastInitial": adv.last_name[0],
                       "specialty": [specialty.to_json() for specialty in (adv.specialties or [])],
                       "occupation": [occ.to_json() for occ in (adv.occupations or [])],
                       "previousFirm": [firm.to_json() for firm in (adv.previous_firms or [])],
                       "city": adv.city,
                       "state": adv.state,
                       "yearsOfExperience": adv.years_of_experience_range.value if adv.years_of_experience_range else adv.years_of_experience,
                       "imageUrl": adv.linkedin_picture_url,
                       "bio": adv.biography} for adv in advisors],
            "itemCount": total_advisors
        }), Status.COMPLETED


@app.route('/api/promotions', methods=['GET'])
# @requires_auth
def get_promotions():
    """
    Returns all promotions based on query
    :return:
    """
    if request.args.get('all') == 'true':
        promotions = Promotion.query.all()
    else:
        filters = [
            Promotion.expires_at == None,
            Promotion.expires_at > datetime.datetime.now()
        ]
        promotions = Promotion.query.filter(or_(*filters))

    return jsonify({"promotions": [promotion.to_json() for promotion in promotions]}), 200


@app.route('/api/vendors', methods=['GET'])
# @requires_auth
def get_vendors():
    """
    Returns all vendors based on query
    :return:
    """
    vendors = Vendor.query.all()

    return jsonify({"vendors": [vendor.to_json() for vendor in vendors]}), 200
