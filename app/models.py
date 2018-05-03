"""
Models for database
"""
import enum

from flask_security import current_user, login_required, RoleMixin, Security, \
    SQLAlchemyUserDatastore, UserMixin, utils
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask import flash
import uuid
import requests
import string
import random
from datetime import datetime, date, timedelta

from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from app.routes_helpers_api import get_auth0_mgmt_api_token, send_password_email, send_welcome_email


db = SQLAlchemy()

# make_searchable()

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Text(), db.ForeignKey('admins.id'), primary_key=True),
    db.Column('role_id', db.Text(), db.ForeignKey('roles.id'), primary_key=True)
)

advisors_past_big_firm = db.Table(
    'advisors_past_big_firm',
    db.Column('advisor_id', db.Text(), db.ForeignKey('advisors.pk_id'), primary_key=True),
    db.Column('big_firm_id', db.Text(), db.ForeignKey('bigfirms.pk_id'), primary_key=True)
)

advisors_specialties = db.Table(
    'advisors_specialties',
    db.Column('advisor_id', db.Text(), db.ForeignKey('advisors.pk_id'), primary_key=True),
    db.Column('specialty_id', db.Text(), db.ForeignKey('specialties.pk_id'), primary_key=True)
)

advisors_occupations = db.Table(
    'advisors_occupations',
    db.Column('advisor_id', db.Text(), db.ForeignKey('advisors.pk_id', primary_key=True)),
    db.Column('occupation_id', db.Text(), db.ForeignKey('occupations.pk_id', primary_key=True))
)

advisor_applicants_specialties = db.Table(
    'advisor_applicants_specialties',
    db.Column('advisor_applicant_id', db.Text(), db.ForeignKey('advisorapplicants.pk_id'), primary_key=True),
    db.Column('specialty_id', db.Text(), db.ForeignKey('specialties.pk_id'), primary_key=True)
)

advisor_applicants_past_big_firm = db.Table(
    'advisor_applicants_past_big_firms',
    db.Column('advisor_applicant_id', db.Text(), db.ForeignKey('advisorapplicants.pk_id'), primary_key=True),
    db.Column('big_firm_id', db.Text(), db.ForeignKey('bigfirms.pk_id'), primary_key=True)
)


class YearsOfExperienceRange(enum.Enum):
    LEVEL0 = ''
    LEVEL1 = '1-2'
    LEVEL2 = '3-5'
    LEVEL3 = '6-10'
    LEVEL4 = '11-20'
    LEVEL5 = '21+'
    LEVEL6 = '30+'

advisorapplicant_bigfirm = db.Table(
    'advisorapplicant_bigfirm',
    db.Column('advisorapplicant_id', db.Text(), db.ForeignKey('advisorapplicants.pk_id')),
    db.Column('bigfirm_id', db.Text(), db.ForeignKey('bigfirms.pk_id'))
)


advisor_bigfirm = db.Table(
    'advisor_bigfirm',
    db.Column('advisor_id', db.Text(), db.ForeignKey('advisors.pk_id')),
    db.Column('bigfirm_id', db.Text(), db.ForeignKey('bigfirms.pk_id'))
)

class AdminLogin(db.Model, UserMixin):
    """
    Admin accounts with different permissions
    """
    __tablename__ = 'admins'

    # Metadata
    id = db.Column(db.Text(), primary_key=True)
    active = db.Column(db.Boolean())

    # Application data
    email = db.Column(db.Text(), unique=True)
    password = db.Column(db.Text())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('AdminLogin'))

    analytics_access = db.Column(db.Boolean())
    database_access = db.Column(db.Boolean())

    def __init__(self, **data):
        # Metadata
        self.id = str(uuid.uuid4())
        self.active = data.get('active', False)

        # Application data
        self.email = data.get('email','')
        self.password = data.get('password','')

        self.analytics_access = data.get('analytics_access',False)
        self.database_access = data.get('database_access',False)


    def __repr__(self):
        return u'<{}>'.format(self.email)

    def to_json(self):
        return {
            "id": self.id,
            "active": self.active,
            "email": self.email,
            "roles": [[role.name, role.id] for role in self.roles] if self.roles is not None else []
        }

    def get_id(self):
        return self.id

    def has_role(self, role):
        for my_role in self.roles:
            if (my_role.name == role):
                return True
        return False

class Role(db.Model, RoleMixin):
    """
    Role table to hold a set of permissions on a table
    """
    __tablename__ = 'roles'

    id = db.Column(db.Text(), primary_key=True)
    name = db.Column(db.Text())
    can_read = db.Column(db.Boolean())
    can_edit = db.Column(db.Boolean())
    can_create = db.Column(db.Boolean())
    can_delete = db.Column(db.Boolean())
    table_name = db.Column(db.Text())

    #
    # # Permissions for adminlogin
    # can_read_adminlogins = db.Column(db.Boolean())
    # can_delete_adminlogins = db.Column(db.Boolean())
    # can_edit_adminlogins = db.Column(db.Boolean())
    # can_create_adminlogins = db.Column(db.Boolean())
    #
    # # Permissions for advisor
    # can_read_advisors = db.Column(db.Boolean())
    # can_delete_advisors = db.Column(db.Boolean())
    # can_edit_advisors = db.Column(db.Boolean())
    # can_create_advisors = db.Column(db.Boolean())
    #
    # # Permissions for advisorapplicant
    # can_read_advisorapplicants = db.Column(db.Boolean())
    # can_delete_advisorapplicants = db.Column(db.Boolean())
    # can_edit_advisorapplicants = db.Column(db.Boolean())
    # can_create_advisorapplicants = db.Column(db.Boolean())
    #
    # # Permissions for project
    # can_read_projects = db.Column(db.Boolean())
    # can_delete_projects = db.Column(db.Boolean())
    # can_edit_projects = db.Column(db.Boolean())
    # can_create_projects = db.Column(db.Boolean())
    #
    # # Permissions for role
    # can_read_roles = db.Column(db.Boolean())
    # can_delete_roles = db.Column(db.Boolean())
    # can_edit_roles = db.Column(db.Boolean())
    # can_create_roles = db.Column(db.Boolean())
    #
    # # Permissions for specialty
    # can_read_specialties = db.Column(db.Boolean())
    # can_delete_specialties = db.Column(db.Boolean())
    # can_edit_specialties = db.Column(db.Boolean())
    # can_create_specialties = db.Column(db.Boolean())
    #
    # # Permissions for subspecialty
    # can_read_subspecialties = db.Column(db.Boolean())
    # can_delete_subspecialties = db.Column(db.Boolean())
    # can_edit_subspecialties = db.Column(db.Boolean())
    # can_create_subspecialties = db.Column(db.Boolean())
    #
    # # Permissions for bigfirm
    # can_read_bigfirms = db.Column(db.Boolean())
    # can_delete_bigfirms = db.Column(db.Boolean())
    # can_edit_bigfirms = db.Column(db.Boolean())
    # can_create_bigfirms = db.Column(db.Boolean())

    def __init__(self, **data):
        self.id = str(uuid.uuid4())
        self.name = data.get('name','')
        self.can_read = data.get('can_read', False)
        self.can_edit = data.get('can_edit', False)
        self.can_create = data.get('can_create', False)
        self.can_delete = data.get('can_delete', False)
        self.table_name = data.get('table_name', '').lower()
        # # Permissions for adminlogin
        # self.can_read_adminlogins = data.get('can_read_adminlogins', False)
        # self.can_delete_adminlogins = data.get('can_delete_adminlogins', False)
        # self.can_edit_adminlogins = data.get('can_edit_adminlogins', False)
        # self.can_create_adminlogins = data.get('can_create_adminlogins', False)
        #
        # # Permissions for advisor
        # self.can_read_advisors= data.get('can_read_advisors', False)
        # self.can_delete_advisors = data.get('can_delete_advisors', False)
        # self.can_edit_advisors = data.get('can_edit_advisors', False)
        # self.can_create_advisors = data.get('can_create_advisors', False)
        #
        # # Permissions for advisorapplicant
        # self.can_read_advisorapplicants = data.get('can_read_advisorapplicants', False)
        # self.can_delete_advisorapplicants = data.get('can_delete_advisorapplicants', False)
        # self.can_edit_advisorapplicants = data.get('can_edit_advisorapplicants', False)
        # self.can_create_advisorapplicants = data.get('can_create_advisorapplicants', False)
        #
        # # Permissions for project
        # self.can_read_projects = data.get('can_read_projects', False)
        # self.can_delete_projects = data.get('can_delete_projects', False)
        # self.can_edit_projects = data.get('can_edit_projects', False)
        # self.can_create_projects = data.get('can_create_projects', False)
        #
        # # Permissions for role
        # self.can_read_roles = data.get('can_read_roles', False)
        # self.can_delete_roles = data.get('can_delete_roles', False)
        # self.can_edit_roles = data.get('can_edit_roles', False)
        # self.can_create_roles = data.get('can_create_roles', False)
        #
        # # Permissions for specialties
        # self.can_read_specialties = data.get('can_read_specialties', False)
        # self.can_delete_specialties = data.get('can_delete_specialties', False)
        # self.can_edit_specialties = data.get('can_edit_specialties', False)
        # self.can_create_specialties = data.get('can_create_specialties', False)
        #
        # # Permissions for subspecialties
        # self.can_read_subspecialties = data.get('can_read_subspecialties', False)
        # self.can_delete_subspecialties = data.get('can_delete_subspecialties', False)
        # self.can_edit_subspecialties = data.get('can_edit_subspecialties', False)
        # self.can_create_subspecialties = data.get('can_create_subspecialties', False)
        #
        # # Permissions for bigfirm
        # self.can_read_bigfirms = data.get('can_read_bigfirms', False)
        # self.can_delete_bigfirms = data.get('can_delete_bigfirms', False)
        # self.can_edit_bigfirms = data.get('can_edit_bigfirms', False)
        # self.can_create_bigfirms = data.get('can_create_bigfirms', False)

    def __repr__(self):
        return u'<{}>'.format(self.name)

#
# class Permissions(db.Model):
#     """
#     Permissions class that stores the permissions a role has on a table.
#     """
#     __tablename__ = 'permissions'
#
#     id = db.Column(db.Text(), primary_key=True)
#     name = db.Column(db.Text())
#     can_read = db.Column(db.Boolean())
#     can_edit = db.Column(db.Boolean())
#     can_create = db.Column(db.Boolean())
#     can_delete = db.Column(db.Boolean())
#     table_name = db.Column(db.Text())
#
#     def __init__(self, **data):
#         self.id = str(uuid.uuid4())
#         self.name = data.get('name','')
#         self.can_read = data.get('can_read', False)
#         self.can_edit = data.get('can_edit', False)
#         self.can_create = data.get('can_create', False)
#         self.can_delete = data.get('can_delete', False)
#         self.table_name = data.get('table_name', None)
#
#     def __repr__(self):
#         return u'<{}>'.format(self.name)
#

class AdvisorApplicant(db.Model):
    """
    Applicants class that stores information from applied users.
    """
    __tablename__ = 'advisorapplicants'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)
    status = db.Column(db.Text(), nullable=False)  # status should be a table
    date_applied = db.Column(db.Date(), nullable=False)

    # Application/Profile data
    first_name = db.Column(db.Text())
    last_name = db.Column(db.Text())
    profile_pic_url = db.Column(db.Text())
    email = db.Column(db.Text(), nullable=False, unique=True)
    how_they_found = db.Column(db.Text())  # EMAIL/LI/etc.
    referral_user  = db.Column(db.Text())  # eventually it will be a foreign key, but right now it will just be an email
    recommended_advisors = db.Column(db.Text()) # A string of email addresses for people that this applicant would recommend for this platform
    years_of_experience = db.Column(db.Text())
    years_of_bigfirm_experience = db.Column(db.Text())
    # specialty_id = db.Column(db.Text(), db.ForeignKey('specialties.pk_id'))
    # specialty = db.relationship('Specialty', backref='advisorapplicants')

    specialties = db.relationship('Specialty', secondary=advisor_applicants_specialties,
                                     backref='advisorapplicants', lazy=True)

    subspecialties_text = db.Column(db.Text())

    occupation_id = db.Column(db.Text(), db.ForeignKey('occupations.pk_id'))
    occupation = db.relationship('Occupation', backref='advisorapplicants')
    location = db.Column(db.Text()) # right now, this is just their state
    previous_firm_id = db.Column(db.Text(), db.ForeignKey('bigfirms.pk_id'))

    previous_firms = db.relationship('BigFirm', secondary='advisorapplicant_bigfirm')

    company_url = db.Column(db.Text())
    short_bio = db.Column(db.Text())
    current_firm = db.Column(db.Text())
    current_firm_size = db.Column(db.Integer())
    current_firm_revenue =  db.Column(db.Integer())
    undergrad_education = db.Column(db.Text())
    grad_education = db.Column(db.Text())
    billing_rate = db.Column(db.Text())
    work_of_interest = db.Column(db.Text())
    new_client_engagement = db.Column(db.Text())

    city = db.Column(db.Text())
    state = db.Column(db.Text())

    # LinkedIn Data
    linkedin_url = db.Column(db.Text())
    linkedin_first_name = db.Column(db.Text())
    linkedin_last_name = db.Column(db.Text())
    linkedin_maiden_name = db.Column(db.Text())
    linkedin_formatted_name = db.Column(db.Text())
    linkedin_phonetic_first_name = db.Column(db.Text())
    linkedin_phonetic_last_name = db.Column(db.Text())
    linkedin_headline = db.Column(db.Text())
    linkedin_location = db.Column(db.Text())  # An object representing the user's physical location.
    linkedin_industry = db.Column(db.Text())  # See industry Codes for a list of possible values: https://developer.linkedin.com/docs/reference/industry-codes
    linkedin_summary = db.Column(db.Text())
    linkedin_specialities = db.Column(db.Text())
    linkedin_positions = db.Column(db.Text())  # An object representing the member's current position.
    linkedin_picture_url = db.Column(db.Text())
    linkedin_picture_url_orig = db.Column(db.Text())
    linkedin_site_standard_profile_request = db.Column(db.Text())
    linkedin_api_standard_profile_request = db.Column(db.Text())
    linkedin_public_profile_url = db.Column(db.Text())

    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        self.status = 'Applied'
        self.date_applied = date.today()

        # Application data
        self.first_name = data.get('first_name','')
        self.last_name = data.get('last_name','')
        #temporary url
        self.profile_pic_url = data.get('profile_pic_url','https://image.ibb.co/cPxxEQ/headshot.jpg')
        self.email = data.get('email','')
        self.how_they_found = data.get('how_they_found','')
        self.referral_user = data.get('referral_user','')
        self.recommended_advisors = data.get('recommended_advisors','')
        self.years_of_experience = data.get('years_of_experience','')
        self.years_of_bigfirm_experience = data.get('years_of_bigfirm_experience','')
        self.occupation_id = data.get('occupation_id',None)
        self.location = data.get('location','')
        self.previous_firm_id = data.get('previous_firm_id',None)
        self.company_url = data.get('company_url', '')
        self.short_bio = data.get('short_bio', '')
        self.current_firm = data.get('current_firm', '')
        self.current_firm_size = data.get('current_firm_size', 0)
        self.current_firm_revenue =  data.get('current_firm_revenue', 0)
        self.undergrad_education = data.get('undergrad_education', '')
        self.grad_education = data.get('grad_education','')
        self.billing_rate = data.get('billing_rate','')
        self.work_of_interest = data.get('work_of_interest', '')
        self.new_client_engagement = data.get('new_client_engagement','')

        self.specialties = data.get('specialties', [])

        self.city = data.get('city')
        self.state = data.get('state')

        # LinkedIn Data
        self.linkedin_url = data.get('linkedin_url','')
        self.linkedin_first_name = data.get('linkedin_first_name','')
        self.linkedin_last_name = data.get('linkedin_last_name','')
        self.linkedin_maiden_name = data.get('linkedin_maiden_name','')
        self.linkedin_formatted_name = data.get('linkedin_formatted_name','')
        self.linkedin_phonetic_first_name = data.get('linkedin_phonetic_first_name','')
        self.linkedin_phonetic_last_name = data.get('linkedin_phonetic_last_name','')
        self.linkedin_headline = data.get('linkedin_headline','')
        self.linkedin_location = data.get('linkedin_location','')
        self.linkedin_industry = data.get('linkedin_industry','')
        self.linkedin_summary = data.get('linkedin_summary','')
        self.linkedin_specialities = data.get('linkedin_specialities','')
        self.linkedin_positions = data.get('linkedin_positions','')
        self.linkedin_picture_url = data.get('linkedin_picture_url','')
        self.linkedin_picture_url_orig = data.get('linkedin_picture_url_orig','')
        self.linkedin_site_standard_profile_request = data.get('linkedin_site_standard_profile_request','')
        self.linkedin_api_standard_profile_request = data.get('linkedin_api_standard_profile_request','')
        self.linkedin_public_profile_url = data.get('linkedin_public_profile_url','')

    def __repr__(self):
        return u'<{} {} - {}>'.format(self.first_name or self.linkedin_first_name, self.last_name or
                                      self.linkedin_last_name, self.email)

    def reject(self):
        """
        Called when the applicant is denied by an admin
        """
        self.status = 'Declined'

    def approve(self, welcome_message):
        """
        Called when the applicant is approved by an admin.
        """
        # First, check that this application wasn't already approved
        if self.status == 'Accepted':
            return False
        # Second, check that no advisor currently exists with the given email
        queried_test = db.session.query(Advisor).filter_by(email=self.email).first()
        if queried_test is not None:
            flash("Advisor with email " + self.email + " already exists.")
            return False


        # Create a new Advisor based on the current applicant's data
        # randomly generated default password
        default_password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))

        mgmt_api_token = get_auth0_mgmt_api_token()
        if mgmt_api_token is None:
            flash("Could not retrieve Auth0 management API token")
            return False

        headers = {'Authorization': str('Bearer ' + mgmt_api_token), 'Content-type': 'application/json'}
        auth_create_request = requests.post('https://bigfirmadvisors.auth0.com/api/v2/users', \
                                            headers=headers, \
                                            json={"user_id": "",
                                                  "connection": "BFA-DB-Connection",
                                                  "email": self.email,
                                                  "password": default_password,
                                                  "user_metadata": {
                                                                    "firstName": self.first_name,
                                                                    "lastName": self.last_name
                                                                    },
                                                  "email_verified": False,
                                                  "verify_email": True,
                                                  "app_metadata": {}})


        try:
            new_user = auth_create_request.json()
        except:
            flash("Something went wrong when creating the user on Auth0")
            return False

        if new_user is None:
            flash("Something went wrong when creating the user on Auth0")
            return False

        print('Created new user')
        print(new_user)
        new_user_id = new_user['identities'][0]['user_id']
        print("Auth0 created the user with the pk_id " + new_user_id)
        # new_user_email = new_user['email']

        approved_advisor = Advisor.query.filter_by(pk_id=new_user_id).first()
        if approved_advisor is None:
            flash("During approval, couldn't find the new user with pk_id " + new_user_id)
            return False

        approved_advisor.status='Pending'
        approved_advisor.date_accepted=date.today()
        approved_advisor.date_applied=self.date_applied
        approved_advisor.first_name=self.first_name
        approved_advisor.last_name=self.last_name
        approved_advisor.profile_pic_url=self.linkedin_picture_url
        approved_advisor.email=self.email
        approved_advisor.how_they_found=self.how_they_found
        approved_advisor.referral_user=self.referral_user
        approved_advisor.completed_account_setup = False

        approved_advisor.city = self.city
        approved_advisor.state = self.state

        approved_advisor.years_of_experience = self.years_of_experience
        approved_advisor.years_of_bigfirm_experience = self.years_of_bigfirm_experience

        approved_advisor.specialties = self.specialties
        approved_advisor.subspecialty_text = self.subspecialties_text

        approved_advisor.occupation_id = self.occupation_id
        approved_advisor.location = self.location
        approved_advisor.previous_firm_id = self.previous_firm_id
        approved_advisor.previous_firms = self.previous_firms
        approved_advisor.company_url = self.company_url
        approved_advisor.short_bio = self.short_bio
        approved_advisor.current_firm_name = self.current_firm
        approved_advisor.current_firm_size = self.current_firm_size
        approved_advisor.current_firm_revenue = self.current_firm_revenue
        approved_advisor.undergrad_education = self.undergrad_education
        approved_advisor.grad_education = self.grad_education
        approved_advisor.billing_rate = self.billing_rate

        approved_advisor.linkedin_url=self.linkedin_url
        approved_advisor.linkedin_first_name=self.linkedin_first_name
        approved_advisor.linkedin_last_name=self.linkedin_last_name
        approved_advisor.linkedin_maiden_name=self.linkedin_maiden_name
        approved_advisor.linkedin_formatted_name=self.linkedin_formatted_name
        approved_advisor.linkedin_phonetic_first_name=self.linkedin_phonetic_first_name
        approved_advisor.linkedin_phonetic_last_name=self.linkedin_phonetic_last_name
        approved_advisor.linkedin_headline=self.linkedin_headline
        approved_advisor.linkedin_location=self.linkedin_location
        approved_advisor.linkedin_industry=self.linkedin_industry
        approved_advisor.linkedin_summary=self.linkedin_summary
        approved_advisor.linkedin_specialities=self.linkedin_specialities
        approved_advisor.linkedin_positions=self.linkedin_positions
        approved_advisor.linkedin_picture_url=self.linkedin_picture_url
        approved_advisor.linkedin_picture_url_orig=self.linkedin_picture_url_orig
        approved_advisor.linkedin_site_standard_profile_request=self.linkedin_site_standard_profile_request
        approved_advisor.linkedin_api_standard_profile_request=self.linkedin_api_standard_profile_request
        approved_advisor.linkedin_public_profile_url=self.linkedin_public_profile_url

        if approved_advisor in db.session:
            # Insert the new Advisor into the table
            self.status = 'Accepted'
            db.session.commit()
            # send the new advisor his/her password in an email
            # send_password_email(approved_advisor.email, default_password)
            # send the admin's welcome message
            # send_welcome_email(approved_advisor.email, welcome_message)

            auth_create_request = requests.post('https://bigfirmadvisors.auth0.com/dbconnections/change_password', \
                                            headers=headers, \
                                            json={"client_id": "NtTKOA7_92gYxGwVSJQf1q2BYkEDWJI_",
                                                  "connection": "BFA-DB-Connection",
                                                  "email": approved_advisor.email
                                                  })
            return True
        else:
            flash("Something went wrong while adding the new user's profile information to the database")
            db.session.rollback()
            return False


    def to_json(self):
        return {
            "id": self.pk_id,
            "firstName": self.first_name or self.linkedin_first_name,
            "lastName": self.last_name or self.linkedin_last_name,
            "email": self.email,
            "profilePicUrl": self.profile_pic_url,
            "previousFirm": [firm.name for firm in self.previous_firms],
            "occupation": self.occupation.name if self.occupation is not None else None,
            "specialties": [specialty.name for specialty in self.specialties],
            "yearsOfExperience": self.years_of_experience,
            "yearsOfBigFirmExperience": self.years_of_bigfirm_experience,
            "city": self.city,
            "state": self.state,
            "biography": self.short_bio,
            "currentFirm": self.current_firm,
            "undergradEducation": self.undergrad_education,
            "gradEducation": self.grad_education,
            "companyUrl": self.company_url,
            "billingRate": self.billing_rate,
            "workOfInterest": self.work_of_interest,
            "newClientEngagement": self.new_client_engagement,
            "subspecialties": self.subspecialties_text
        }


class VectorQuery(BaseQuery, SearchQueryMixin):
    """
    Query class that enables TSVector full text search.
    For models that use this, SearchQueryMixin adds the ability
    to do a full text search using ths syntax Table.query.search('searchstring')
    """
    pass

class Advisor(db.Model):
    """
    Advisors class with initializer to document models. These are all approved advisors.
    """
    query_class = VectorQuery
    __tablename__ = 'advisors'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)
    email = db.Column(db.Text(), unique=True)
    status = db.Column(db.Text())
    email_verified = db.Column(db.Boolean())

    completed_account_setup = db.Column(db.Boolean())


    # invite_url = db.Column(db.Text())
    date_applied = db.Column(db.Date())
    date_accepted = db.Column(db.Date())
    stripe_subscription_id = db.Column(db.Text()) # ID for stripe, which stores subscription info
    password = db.Column(db.Text())
    profile_pic_url = db.Column(db.Text())

    updates = db.relationship("Update", backref="update_author", lazy='dynamic')

    # Application data
    first_name = db.Column(db.Text())
    last_name = db.Column(db.Text())
    years_of_experience = db.Column(db.Text())
    years_of_bigfirm_experience = db.Column(db.Text())

    years_of_experience_range = db.Column(db.Enum(YearsOfExperienceRange))
    years_of_bigfirm_experience_range = db.Column(db.Enum(YearsOfExperienceRange))

    how_they_found = db.Column(db.Text())
    referral_user  = db.Column(db.Text())
    # specialty_id = db.Column(db.Text(), db.ForeignKey('specialties.pk_id'))

    specialties = db.relationship('Specialty', secondary=advisors_specialties,
                                  backref='advisors', lazy=True)

    subspecialty_text = db.Column(db.Text())

    subspecialty_id = db.Column(db.Text(), db.ForeignKey('subspecialties.pk_id'))
    subspecialty = db.relationship('Subspecialty', backref='advisors')
    # occupation_id = db.Column(db.Text(), db.ForeignKey('occupations.pk_id'))
    occupations = db.relationship('Occupation', secondary=advisors_occupations,
                                  backref='advisors', lazy=True)

    location = db.Column(db.Text())

    previous_firms = db.relationship('BigFirm', secondary='advisors_past_big_firm')

    current_firm_id = db.Column(db.Text(), db.ForeignKey('bigfirms.pk_id'))

    resume_url = db.Column(db.Text())
    biography = db.Column(db.Text())
    current_firm_name = db.Column(db.Text())
    current_firm_size = db.Column(db.Integer())
    current_firm_revenue =  db.Column(db.Integer())
    undergrad_education = db.Column(db.Text())
    grad_education = db.Column(db.Text())
    billing_rate = db.Column(db.Text())
    work_of_interest = db.Column(db.Text())
    new_client_engagement = db.Column(db.Text())

    city = db.Column(db.Text())
    state = db.Column(db.Text())

    company_url = db.Column(db.Text())

    posted_projects = db.relationship('Project', backref='advisor_who_posted', lazy='dynamic')


    # LinkedIn Data
    linkedin_url = db.Column(db.Text())
    linkedin_first_name = db.Column(db.Text())
    linkedin_last_name = db.Column(db.Text())
    linkedin_maiden_name = db.Column(db.Text())
    linkedin_formatted_name = db.Column(db.Text())
    linkedin_phonetic_first_name = db.Column(db.Text())
    linkedin_phonetic_last_name = db.Column(db.Text())
    linkedin_headline = db.Column(db.Text())
    linkedin_location = db.Column(db.Text())  # An object representing the user's physical location.
    linkedin_industry = db.Column(
        db.Text())  # See industry Codes for a list of possible values: https://developer.linkedin.com/docs/reference/industry-codes
    linkedin_summary = db.Column(db.Text())
    linkedin_specialities = db.Column(db.Text())
    linkedin_positions = db.Column(db.Text())  # An object representing the member's current position.
    linkedin_picture_url = db.Column(db.Text())
    linkedin_picture_url_orig = db.Column(db.Text())
    linkedin_site_standard_profile_request = db.Column(db.Text())
    linkedin_api_standard_profile_request = db.Column(db.Text())
    linkedin_public_profile_url = db.Column(db.Text())

    # Search vector for full text search
    search_vector = db.Column(TSVectorType('first_name', 'last_name', 'status', \
        'referral_user', 'location', 'short_bio', 'current_firm', 'undergrad_education', \
        'grad_education', 'billing_rate', 'work_of_interest', \
        'new_client_engagement'))

    def __init__(self, **data):
        self.pk_id = str(uuid.uuid4())

        # Metadata
        self.status = data.get('status', 'Pending')
        # self.invite_url = data.get('invite_url','')
        self.date_applied = data.get('date_applied', date.today())
        self.date_accepted = data.get('date_accepted', date.today())
        self.stripe_subscription_id = data.get('stripe_subscription_id','')
        self.email_verified = False
        self.completed_account_setup = False
        self.profile_pic_url = data.get('profile_pic_url','https://image.ibb.co/cPxxEQ/headshot.jpg')

        # Application data
        self.first_name = data.get('first_name','')
        self.last_name = data.get('last_name','')
        self.email = data.get('email','')
        self.how_they_found = data.get('how_they_found','')
        self.referral_user = data.get('referral_user','')

        self.previous_firms = data.get('previous_firms', [])

        self.years_of_experience = data.get('years_of_experience',0)
        self.years_of_bigfirm_experience = data.get('years_of_bigfirm_experience',0)

        self.years_of_experience_range = data.get('years_of_experience_range')
        self.years_of_bigfirm_experience_range = data.get('years_of_bigfirm_experience_range')

        # self.specialty_id = data.get('specialty_id',None)
        self.specialties = data.get('specialties',[])

        self.subspecialty_id = data.get('subspecialty_id',None)
        self.subspecialty = data.get('subspecialty',None)

        self.occupations = data.get('occupations', [])


        # self.occupation_id = data.get('occupation_id',None)
        # self.occupation = data.get('occupation',None)
        self.location = data.get('location','')
        # self.previous_firm_id = data.get('previous_firm_id',None)
        self.resume_url = data.get('resume_url', '')
        self.biography = data.get('biography', '')
        self.current_firm_name = data.get('current_firm_name', '')

        self.current_firm_size = data.get('current_firm_size', 0)
        self.current_firm_revenue =  data.get('current_firm_revenue', 0)
        self.undergrad_education = data.get('undergrad_education', '')
        self.grad_education = data.get('grad_education','')
        self.billing_rate = data.get('billing_rate','')
        self.work_of_interest = data.get('work_of_interest', '')
        self.new_client_engagement = data.get('new_client_engagement','')

        self.city = data.get('city')
        self.state = data.get('state')

        # LinkedIn Data
        self.linkedin_url = data.get('linkedin_url','')
        self.linkedin_first_name = data.get('linkedin_first_name','')
        self.linkedin_last_name = data.get('linkedin_last_name','')
        self.linkedin_maiden_name = data.get('linkedin_maiden_name','')
        self.linkedin_formatted_name = data.get('linkedin_formatted_name','')
        self.linkedin_phonetic_first_name = data.get('linkedin_phonetic_first_name','')
        self.linkedin_phonetic_last_name = data.get('linkedin_phonetic_last_name','')
        self.linkedin_headline = data.get('linkedin_headline','')
        self.linkedin_location = data.get('linkedin_location','')
        self.linkedin_industry = data.get('linkedin_industry','')
        self.linkedin_summary = data.get('linkedin_summary','')
        self.linkedin_specialities = data.get('linkedin_specialities','')
        self.linkedin_positions = data.get('linkedin_positions','')
        self.linkedin_picture_url = data.get('linkedin_picture_url','')
        self.linkedin_picture_url_orig = data.get('linkedin_picture_url_orig','')
        self.linkedin_site_standard_profile_request = data.get('linkedin_site_standard_profile_request','')
        self.linkedin_api_standard_profile_request = data.get('linkedin_api_standard_profile_request','')
        self.linkedin_public_profile_url = data.get('linkedin_public_profile_url','')

    def __repr__(self):
        return u'<{} {} - {}>'.format(self.first_name or self.linkedin_first_name, self.last_name or
                                      self.linkedin_last_name, self.email)


    def to_json(self):
        return {
            "id": self.pk_id,
            "firstName": self.first_name or self.linkedin_first_name,
            "lastName": self.last_name or self.linkedin_last_name,
            "email": self.email,
            "profilePicUrl": self.profile_pic_url,
            "completedAccountSetup": self.completed_account_setup,
            "previousFirm": [firm.to_json() for firm in self.previous_firms],
            "occupation": [occ.to_json() for occ in self.occupations],
            "specialty": [spec.to_json() for spec in self.specialties],
            "subspecialty": self.subspecialty_text,
            "yearsOfExperience": self.years_of_experience_range.value
                                 if self.years_of_experience_range else self.years_of_experience,
            "yearsOfBigFirmExperience": self.years_of_bigfirm_experience_range.value
                                        if self.years_of_bigfirm_experience_range else self.years_of_bigfirm_experience,
            "location": self.location,
            "city": self.city,
            "state": self.state,
            "biography": self.biography,
            "currentFirm": self.current_firm.name if self.current_firm else self.current_firm_name,
            "currentFirmSize": self.current_firm_size,
            "currentFirmRevenue": self.current_firm_revenue,
            "undergradEducation": self.undergrad_education,
            "gradEducation": self.grad_education,
            "companyUrl": self.company_url,
            "billingRate": self.billing_rate,
            "workOfInterest": self.work_of_interest,
            "newClientEngagement": self.new_client_engagement
        }


class Project(db.Model):
    """
    Project class with initializer to document models
    """
    query_class = VectorQuery
    __tablename__ = 'projects'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)
    date_created = db.Column(db.Date())

    # Application data
    title = db.Column(db.Text())
    description = db.Column(db.Text())
    location = db.Column(db.Text())
    duration = db.Column(db.Text()) # in months
    budget = db.Column(db.Float()) # per month
    project_image_url = db.Column(db.Text())
    file_attachments = db.Column(ARRAY(TEXT)) # array of file URLs
    specialty_id = db.Column(db.Text(), db.ForeignKey('specialties.pk_id'))
    specialty = db.relationship('Specialty', backref='projects')
    occupation_id = db.Column(db.Text(), db.ForeignKey('occupations.pk_id'))
    occupation = db.relationship('Occupation', backref='projects')
    preferred_previous_bigfirm_id = db.Column(db.Text(), db.ForeignKey('bigfirms.pk_id'))

    status = db.Column(db.Text()) # status of the project

    required_years_experience = db.Column(db.Integer())
    required_qualifications = db.Column(db.Text())
    preferred_qualifications = db.Column(db.Text())
    start_date = db.Column(db.Text())

    #person who posted it
    advisor_who_posted_id = db.Column(db.Text(), db.ForeignKey('advisors.pk_id', onupdate='CASCADE', ondelete='SET NULL'))

    referral_fee = db.Column(db.Float())

    # Search vector for full text search
    search_vector = db.Column(TSVectorType('title', 'description', 'location', \
        'location', 'duration', 'status', 'required_qualifications', 'preferred_qualifications', \
        'start_date'))

    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        self.date_created = date.today()
        # Application data
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.location = data.get('location', '')
        self.duration = data.get('duration',0.0)
        self.budget = data.get('budget', 0.0)
        self.project_image_url = data.get('project_image_url', '')
        self.file_attachments = data.get('file_attachments',None)
        self.specialty_id = data.get('speciality_id', None)
        self.occupation_id = data.get('occupation_id', None)
        self.preferred_previous_bigfirm_id = data.get('preferred_previous_bigfirm_id', None)
        self.required_years_experience = data.get('required_years_experience', 0)
        self.required_qualifications = data.get('required_qualifications','')
        self.preferred_qualifications = data.get('preferred_qualifications', '')
        self.start_date = data.get('start_date', 'Not Time Sensitive')
        self.advisor_who_posted_id = data.get('advisor_who_posted_id', None)
        self.status = data.get('status', 'Open')
        self.referral_fee = data.get('referral_fee', 0.0)


    def __repr__(self):
        return u'<{} - {} - {}>'.format(self.pk_id, self.title, self.date_created)

    def to_json(self):
        return {
           "id": self.pk_id,
           "title": self.title,
           "status": self.status,
           "description": self.description,
           "dateCreated": self.date_created,
           "location": self.location,
           "duration": str(self.duration) + " months",
           "budget": "$" + str(self.budget) + " per month",
           "occupation": self.occupation.name if self.occupation is not None else {},
           "specialty": self.specialty.name if self.specialty is not None else {},
           "preferredPreviousBigFirm": self.preferred_previous_bigfirm.name if self.preferred_previous_bigfirm is not None else {},
           "requiredYearsExperience": self.required_years_experience,
           "requiredQualifications": self.required_qualifications,
           "preferredQualifications": self.preferred_qualifications,
           "startDate": self.start_date,
           "referralFee" :self.referral_fee,
           "advisorWhoPosted": {"id": self.advisor_who_posted.pk_id, "email": self.advisor_who_posted.email, \
                                "firstName": self.advisor_who_posted.first_name
                                             or self.advisor_who_posted_id.linkedin_first_name,
                                "lastName": self.advisor_who_posted.last_name
                                            or self.advisor_who_posted_id.linkedin_last_name
                                } \
                                if self.advisor_who_posted is not None else {}
        }

class Update(db.Model):
    """
    Project class with initializer to document models
    """
    query_class = VectorQuery
    __tablename__ = 'updates'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)
    date_created = db.Column(db.Date())



    # Application data
    title = db.Column(db.Text())
    tag = db.Column(db.Text())
    body = db.Column(db.Text())
    image_url = db.Column(db.Text())

    #person who posted it
    advisor_id = db.Column(db.Text, db.ForeignKey('advisors.pk_id'))
    advisor = db.relationship('Advisor')
    # Search vector for full text search


    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        self.date_created = date.today()
        # Application data
        self.title = data.get('title', '')
        self.tag = data.get('tag', '')
        self.body = data.get('body', '')
        self.image_url = data.get('image_url','')
        self.advisor_id = data.get('advisor_id', None)
        self.advisor = data.get('advisor', None)


    def __repr__(self):
        return u'<{} - {} - {}>'.format(self.pk_id, self.title, self.date_created)

    def to_json(self):
        return {
           "id": self.pk_id,
           "title": self.title,
           "date_created": self.date_created.strftime('%a %B %e, %Y'),
           "tag": self.tag,
           "body": self.body,
           "image_url": self.image_url,
           "author_id": {
               "id": self.advisor.pk_id,
               "email": self.advisor.email,
               "firstName": self.advisor.first_name or self.advisor.linkedin_first_name,
               "lastName": self.advisor.last_name or self.advisor.linkedin_last_name,
               "authorProfilePicUrl": self.advisor.profile_pic_url} if self.advisor is not None else {}
        }


class MNActivity(db.Model):
    """
    Project class with initializer to document models
    """
    query_class = VectorQuery
    __tablename__ = 'mn_activity'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)
    date_created = db.Column(db.Date())

    # Application data
    title = db.Column(db.Text())
    body = db.Column(db.Text())
    body_link = db.Column(db.Text())


    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        self.date_created = date.today()
        # Application data
        self.title = data.get('title', '')
        self.body = data.get('body', '')
        self.body_link = data.get('body_link', '')

    def __repr__(self):
        return u'<{} - {} - {}>'.format(self.pk_id, self.title, self.date_created)

    def to_json(self):
        return {
           "id": self.pk_id,
           "date_created": self.date_created.strftime('%a %B %e, %Y'),
           "title": self.title,
           "body": self.body,
           "body_link": self.body_link
        }

class Specialty(db.Model):
    """
    Model for Specialty
    """
    __tablename__ = 'specialties'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)

    # Application data
    name = db.Column(db.Text())
    occupation_id = db.Column(db.Text(), db.ForeignKey('occupations.pk_id'))
    occupation = db.relationship('Occupation', back_populates='specialties')

    #subspecialties = db.relationship('Subspecialty', backref='specialty', lazy='dynamic')
    # projects = db.relationship('Project', backref='specialties', lazy='dynamic')
    # advisors = db.relationship('Advisor', backref='specialties', lazy='dynamic')
    # advisor_applicants = db.relationship('AdvisorApplicant', backref='specialties', lazy='dynamic')


    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        # Application data
        self.name = data.get('name', '')
        self.occupation_id = data.get('occupation_id', None)
        self.occupation = data.get('occupation', None)

    def __repr__(self):
        return u'<{}>'.format(self.name)

    def to_json(self):
        return {
           "id": self.pk_id,
           "name": self.name
        }

class Subspecialty(db.Model):
    """
    Model for Subspecialty
    """
    __tablename__ = 'subspecialties'


    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)

    # Application data
    name = db.Column(db.Text())
    count = db.Column(db.Integer())


    # advisors = db.relationship('Advisor', backref='advisor_subspecialty', lazy='dynamic')
    # advisor_applicants = db.relationship('AdvisorApplicant', backref='applicant_advisor_subspecialty', lazy='dynamic')

    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        # Application data
        self.name = data.get('name', '')
        self.count = data.get('count',0)


    def __repr__(self):
        return u'< {} >'.format(self.name)

    def to_json(self):
        return {
           "id": self.pk_id,
           "name": self.name,
        }


class BigFirm(db.Model):
    """
    Model for BigFirm
    """
    __tablename__ = 'bigfirms'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)

    # Application data
    name = db.Column(db.Text(), unique=True)
    weight = db.Column(db.Integer())

    advisors = db.relationship('Advisor', backref='current_firm', lazy='subquery')
    advisor_applicants = db.relationship('AdvisorApplicant', backref='previous_firm', lazy='subquery')
    projects = db.relationship('Project', backref='preferred_previous_bigfirm', lazy='dynamic')


    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        # Application data
        self.name = data.get('name', '')
        self.weight = data.get('weight', 0)

    def __repr__(self):
        return u'<{} - {}>'.format(self.pk_id, self.name)

    def to_json(self):
        return {
           "id": self.pk_id,
           "name": self.name,
           "weight": self.weight,
        }


# class Status(db.Model):
#     """
#     All statuses
#     Separate table allows for statuses to be updated if need to be changed later
#     """
#     __tablename__ = 'statuses'

#     id = db.Column(db.Text(), primary_key=True)
#     status = db.Column(db.Text())

#     def __init__(self, status=''):
#         self.id = uuid.uuid4()
#         self.status = status

#     def __repr__(self):
#         return self.status
#         self.admin_role = admin_role

#     def get_id(self):
#         return self.id



class Occupation(db.Model):
    """
    Model for Occupation
    """
    __tablename__ = 'occupations'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)

    # Application data
    name = db.Column(db.Text(), unique=True)
    specialties = db.relationship("Specialty", back_populates='occupation')

    # specialties = db.relationship('Specialty', backref='occupations', lazy='dynamic')
    # advisors = db.relationship('Advisor', backref='occupations', lazy='subquery')
    # advisor_applicants = db.relationship('AdvisorApplicant', backref='occupations', lazy='dynamic')
    # projects = db.relationship('Project', backref='occupations', lazy='dynamic')

    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        # Application data
        self.name = data.get('name', '')


    def __repr__(self):
        return u'<{} - {}>'.format(self.pk_id, self.name)

    def to_json(self):
        return {
           "id": self.pk_id,
           "name": self.name
        }


class OccupationType(db.Model):
    """
    Model for OccupationType
    """
    __tablename__ = 'occupationtypes'

    # Metadata
    pk_id = db.Column(db.Text(), primary_key=True)

    # Application data
    name = db.Column(db.Text())
    occupation_id = db.Column(db.Text(), db.ForeignKey('occupations.pk_id'))


    def __init__(self, **data):
        # Metadata
        self.pk_id = str(uuid.uuid4())
        # Application data
        self.name = data.get('name', '')
        self.occupation_id = data.get('occupation_id', None)

    def __repr__(self):
        return u'<{} - {}>'.format(self.pk_id, self.name)

    def to_json(self):
        return {
           "id": self.pk_id,
           "name": self.name,
           "occupation": {"id": self.occupation.pk_id, "name": self.occupation.name} if self.occupation is not None else {}
        }


class Vendor(db.Model):
    """
    Model for vendors for promotions
    """

    __tablename__ = 'vendors'

    pk_id = db.Column(db.Text(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text())
    website_url = db.Column(db.Text())
    logo_url = db.Column(db.Text())

    promotions = db.relationship('Promotion', backref='vendor')

    def __init__(self, **data):
        self.pk_id = str(uuid.uuid4())
        self.name = data.get('name')
        self.description = data.get('description')
        self.website_url = data.get('website_url')
        self.logo_url = data.get('logo_url')

        self.promotions = data.get('promotions', [])

    def __str__(self):
        return '<Vendor: {}>'.format(self.name)

    def to_json(self, include_promotions=False):
        return {
            'id': self.pk_id,
            'name': self.name,
            'description': self.description,
            'website_url': self.website_url,
            'logo_url': self.logo_url,
            'promotions': [p.to_json() for p in self.promotions] if include_promotions else []
        }


class Promotion(db.Model):
    """
    Model for promotions
    """

    __tablename__ = 'promotions'

    pk_id = db.Column(db.Text(), primary_key=True)
    title = db.Column(db.Text())
    description = db.Column(db.Text(), nullable=False)
    how_to_redeem = db.Column(db.Text(), nullable=False)

    vendor_id = db.Column(db.Text(), db.ForeignKey('vendors.pk_id'))

    expires_at = db.Column(db.DateTime())

    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())

    def __init__(self, **data):
        self.pk_id = str(uuid.uuid4())
        self.title = data.get('title')
        self.description = data.get('description')
        self.how_to_redeem = data.get('how_to_redeem')

        self.vendor_id = data.get('vendor_id')

        self.expires_at = data.get('expires_at', datetime.now() + timedelta(days=365))

        self.created_at = datetime.now()

    def to_json(self):
        return {
            'id': self.pk_id,
            'title': self.title,
            'description': self.description,
            'how_to_redeem': self.how_to_redeem,
            'vendor': self.vendor.to_json(),
            'expires_at': self.expires_at and self.expires_at.strftime('%B %d, %Y'),
            'created_at': self.created_at and self.created_at.strftime('%B %d, %Y %H:%M'),
            'updated_at': self.updated_at and self.updated_at.strftime('%B %d, %Y %H:%M')
        }

