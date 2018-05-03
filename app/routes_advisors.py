"""
API endpoints for Flask App relating to agent only routes
"""

from app.application import app
from app.status import Status
from app.models import db, Advisor, Project, Specialty, Occupation, Update, MNActivity
from app.slack_utils import transform_links
from app.auth import *
from app.routes_helpers_api import get_auth0_user_profile_from_token
from flask import jsonify, request
from flask_cors import cross_origin
import sys, os

from sqlalchemy.sql.expression import func, and_




@app.route('/api/advisors/profile', methods=['GET'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_profile():
    """
    This endpoint takes an auth0 access token (given to the user
    at sign in) and uses it to retrieve the rest of the user's
    information.
    """
    try:
        access_token = get_token_auth_header()
        user_json = get_auth0_user_profile_from_token(access_token)
        if user_json is None:
            return jsonify({'error': 'No user profile found'}), Status.BAD

        user_pk_id = user_json.get('sub', None)
        if user_pk_id is None:
            return jsonify({'error': 'User profile was invalid'}), Status.BAD

        # the pk_id is originally prefixed by 'auth0|' so we filter it out
        user_pk_id = user_pk_id[6:]

        found_advisor = db.session.query(Advisor).filter_by(pk_id=user_pk_id).first()
        if found_advisor is None:
            return jsonify({'error': 'The user id returned by auth0 is not found in our database'}), \
                    Status.BAD
        return jsonify(found_advisor.to_json()), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD


@app.route('/api/advisors/mn-activity', methods=['POST'])
def add_mn_activity():
    try:
        data = request.get_json()
        print(data)
        event = data.get('event', None)
        if event:
            if event.get('username', None) == 'BFA Test':
                attachment = event.get('attachments', None)[0]
                if attachment:
                    pretext_text = attachment.get('pretext', None)
                    body_text = attachment.get('title', None)
                    body_link = attachment.get('title_link', None)
                    if pretext_text and body_text:
                        title = transform_links(pretext_text)
                        body = body_text
                        body_link = body_link
                        print(title, body, body_link)

                        activity = MNActivity()
                        activity.title = title
                        activity.body = body
                        activity.body_link = body_link

                        db.session.add(activity);
                        if activity not in db.session:
                            db.session.rollback()
                            db.session.close()
                            print('db rollback')
                            return jsonify({'error': "Couldn't insert activity successfully"}), Status.BAD
                        else:
                            db.session.commit()
                            return jsonify({'message': 'Activity created'}), Status.COMPLETED
                    else:
                        print('pre_text or body_text not found')
                else:
                    print('no attachment found')
        else:
            print('event not found')
            return jsonify({'error': 'no event found'}), Status.BAD
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), Status.BAD
    return jsonify({'error': 'MN activity not logged'}), Status.BAD

@app.route('/api/advisors/recent-members', methods=['GET'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_recent_members():

    try:
        advisors = db.session.query(Advisor).limit(3).all()
        advisors_list = []

        for found_advisor in advisors:

            advisor_data = found_advisor.to_json()

            advisors_list += [advisor_data]


        return jsonify({
                "items": advisors_list,
                "itemCount": len(advisors_list)
                }), Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/advisors/recent-projects', methods=['GET'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_recent_projects():
    try:
        projects = db.session.query(Project).order_by(db.desc(Project.date_created)).limit(3).all()

        recent_projects = [project.to_json() for project in projects]
        return jsonify({
            'recentProjects' : recent_projects
            })
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/advisors/recent-updates', methods=['GET'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_recent_updates():
    try:
        updates = db.session.query(Update).order_by(db.desc(Update.date_created)).limit(5).all()

        recent_updates = [update.to_json() for update in updates]
        return jsonify({
            'recentUpdates' : recent_updates
            })
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD


@app.route('/api/advisors/mn-activity-feed', methods=['GET'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_mnactivity_feed():
    try:
        recent_activity = db.session.query(MNActivity).order_by(db.desc(MNActivity.date_created)).limit(5).all()

        recent_activity = [activity.to_json() for activity in recent_activity]
        return jsonify({
            'mnActivity' : recent_activity
            })
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD


@app.route('/api/advisors/search', methods=['POST'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_dashboard_search():
    """
    The dashboard search function that searches through advisors
    and projects for relevant info
    """
    try:
        data = request.get_json()

        search_string = data.get('searchString', None)
        if search_string is None or search_string == "":
            return jsonify({'error': 'searchString was not given'}), Status.COMPLETED

        advisors_q = Advisor.query.search(search_string).all()
        projects_q = Project.query.search(search_string).all()

        return jsonify({
            "projects": {
                "items": [proj.to_json() for proj in projects_q],
                "itemCount": len(projects_q)
            },
            "advisors": {
                "items": [adv.to_json() for adv in advisors_q],
                "itemCount": len(advisors_q)
            }
        }), Status.COMPLETED

    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print(str(e))
        print(str(v))
        return jsonify({'error': str(e),
                        'value': str(v)}), Status.BAD

@app.route('/api/advisors/advisorsearch', methods=['POST'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_search():
    """
    Search for advisors that returns important information about
    each advisor that matches the query
    """

    try:
        data = request.get_json()

        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD
        # get filter options
        filter_occupation = data.get('occupationId')  # will get the pk_id of the occupation
        filter_location = data.get('location')  # Name of state
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
            "items": [adv.to_json() for adv in advisors],
            "itemCount": len(advisors)
        })

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

@app.route('/api/advisors/all', methods=['GET'])
def all_advisors():
    """
    Returns Advisor search page's initial advisors
    :return:
    """
    advisors = Advisor.query.order_by(func.random()).limit(9).all()
    return jsonify({
            "items": [{"id": adv.pk_id,
                       "firstName": adv.first_name,
                       "lastName": adv.last_name,
                       "specialty": [specialty.to_json() for specialty in (adv.specialties or [])],
                       "occupation": [occ.to_json() for occ in (adv.occupations or [])],
                       "previousFirm": [firm.to_json() for firm in (adv.previous_firms or [])],
                       "city": adv.city,
                       "state": adv.state,
                       "yearsOfExperience": adv.years_of_experience_range.value if adv.years_of_experience_range else adv.years_of_experience,
                       "imageUrl": adv.linkedin_picture_url,
                       "bio": adv.biography} for adv in advisors],
            "itemCount": len(advisors)
        }), Status.COMPLETED


@app.route('/api/advisors/projectsearch', methods=['POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_project_search():
    """
    Returns projects based on filters
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        # get filter options
        filter_occupation = data.get('occupationId', None)
        filter_location = data.get('location', None)

        if filter_occupation is not None:
            filter_occupation = filter_occupation.strip()
            if filter_occupation == "":
                filter_occupation = None

        if filter_location is not None:
            filter_location = filter_location.strip()
            if filter_location == "":
                filter_location = None

        if filter_occupation is None and filter_location is None: # no filters, return all projects
            projects = Project.query.filter_by(status='Open').all()
        elif filter_occupation is None: # only filter by location
            projects = Project.query.filter((Project.location == filter_location) & \
                (Project.status == 'Open')).all()
        elif filter_location is None: # only filter by occupation
            projects = Project.query.filter((Project.occupation_id == filter_occupation) & \
                (Project.status == 'Open')).all()
        else: # filter by both
            projects = db.session.query(Project).filter((Project.occupation_id == filter_occupation) & \
                (Project.location == filter_location) & (Project.status == 'Open')).all()


        response = jsonify({
            "items": [project.to_json() for project in projects],
            "itemCount": len(projects)
        })
        db.session.close()
        return response, Status.COMPLETED
    except:
        db.session.rollback()
        db.session.close()
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        return jsonify({'error': str(e),
                        'value': str(v),
                        'file' : str(fname),
                        'line' : str(exc_tb.tb_lineno)
                        }), Status.BAD

@app.route('/api/advisors/projectdetails', methods=['POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_get_project_details():
    """
    Returns details about a specific project
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        project_id = data.get('projectId', None)
        if project_id is None:
            return jsonify({'error': 'projectId was not given'}), Status.BAD

        project = db.session.query(Project).filter_by(pk_id=project_id).first()
        response = jsonify(project.to_json()) if project is not None else jsonify({})
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


@app.route('/api/advisors/postproject', methods=['POST'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisors_new_project():
    try:

        data = request.get_json(force=True)
        print(request.headers.get('Content-Type'))
        print(data)
        print(request.get_json())
        if data is None:
            return jsonify({'error': 'Request JSON was not found'}), Status.BAD

        required_fields = ['title', 'description', 'location', 'duration', \
            'budget',  'specialtyId', 'occupationId', 'requiredQualifications', \
            'preferredQualifications', 'startDate', 'advisorWhoPostedId', 'referralFee']

        for r_field in required_fields:
            if data.get(r_field,None) is None:
                return jsonify({'error': r_field + ' was not given'}), Status.BAD



        new_proj = Project()
        new_proj.title = data.get('title', '')
        new_proj.description = data.get('description', '')
        new_proj.location = data.get('location', '')
        new_proj.duration = data.get('duration', 0.0)
        new_proj.budget = data.get('budget', 0.0)
        #new_proj.project_image_url = data.get('projectImageUrl', '')
        #new_proj.file_attachments = data.get('fileAttachments', [])
        specialty = data.get('specialtyId')
        #new_proj.specialty_id = db.session.query(Specialty).filter_by(name = specialty).first().pk_id

        occupation = data.get('occupationId')
        #new_proj.occupation_id = db.session.query(Occupation).filter_by(name = occupation).first().pk_id
        #new_proj.preferred_previous_bigfirm_id = data.get('preferredPrevBigFirmId', None)
        #new_proj.status = data.get('status', '')
        #new_proj.required_years_experience = data.get('requiredYearsExp', 0)
        #new_proj.requested
        new_proj.required_qualifications = data.get('requiredQualifications', '')
        new_proj.preferred_qualifications = data.get('preferredQualifications', '')
        new_proj.start_date = data.get('startDate', None)

        db.session.add(new_proj);
        if new_proj not in db.session:
            db.session.rollback()
            db.session.close()
            return jsonify({'error': "Couldn't insert project successfully"}), Status.BAD
        else:
            db.session.commit()
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

@app.route('/api/advisors/advisordetails', methods=['POST'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
def advisor_details():
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

        found_advisor = Advisor.query.get(filter_id)

        if found_advisor is not None and found_advisor.status == 'Active':
            response = jsonify(found_advisor.to_json())
        else:
            response = jsonify({"error": "No active advisor found with that ID"})

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
