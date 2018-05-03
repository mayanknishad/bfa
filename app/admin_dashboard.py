from flask_security import current_user

from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import url_for, redirect, request, abort, jsonify
from app.models import AdvisorApplicant, Occupation, BigFirm, Specialty

from stringcase import titlecase


"""
is_accessible is set for all the views so if not logged in the views will not
be shown in the index
"""

def user_has_permission(user, name_of_permission='', table_name=''):
    """
    Takes a user, a permission name, and a table name, and returns whether the user
    has that permission set to true for that table. If a user has multiple roles
    for the same table, then they will have the permission if any of their roles
    has that permission set to true.
    """
    # First, we get the roles this user has on the given table_name.



    filtered_roles = [role for role in user.roles if role.table_name == table_name]

    # if the user has no roles for this table name, they don't have permission
    if len(filtered_roles) < 1:
        return False

    for target_role in filtered_roles:
        try:
            permission_value = getattr(target_role, name_of_permission)
        except AttributeError:
            if(target_role == 'can_edit_advisorapplicants' or target_role == 'can_create_advisors' ):
                return True
            permission_value = False

        # if the permission_value is True on this role, return immediately
        if permission_value == True:
            return True

    # if none of the roles had that permission set to true, return False
    return False


class AdvisorApprovalView(BaseView):
    """
    Custom view for approving AdvisorApplicants
    """
    @expose('/', methods=['GET'])
    def index(self):
        all_applicants = AdvisorApplicant.query.filter((AdvisorApplicant.status == 'Applied') \
            | (AdvisorApplicant.status == 'Declined')).order_by(AdvisorApplicant.status.asc(),AdvisorApplicant.date_applied.desc()).all()
        return self.render('custom_approval.html', applicants=all_applicants)

    @expose('/applicants/<advisor_id>', methods=['GET'])
    def get_applicant_details(self, advisor_id):
        applicant = AdvisorApplicant.query.get(advisor_id)

        if not applicant:
            return jsonify({'error': 'Advisor not found'}), 404

        return jsonify({titlecase(k): v for k, v in applicant.to_json().items()}), 200


    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_edit', 'advisorapplicants') and user_has_permission(current_user, 'can_create', 'advisors')

    def _handle_view(self, name, **kwargs):
            """
            Override builtin _handle_view in order to redirect users when a view is not accessible.
            """
            if not self.is_accessible():
                if current_user.is_authenticated:
                    # permission denied
                    abort(403)
                else:
                    # login
                    return redirect(url_for('security.login', next=request.url))

class AdvisorAuthView(BaseView):
    """
    Custom view for signing in with Auth0
    """
    @expose('/')
    def index(self):
        return self.render('custom_auth.html')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return True

    def _handle_view(self, name, **kwargs):
            """
            Override builtin _handle_view in order to redirect users when a view is not accessible.
            """
            if not self.is_accessible():
                if current_user.is_authenticated:
                    # permission denied
                    abort(403)
                else:
                    # login
                    return redirect(url_for('security.login', next=request.url))


class AdvisorView(ModelView):
    """
    def is_accessible(self):
        return login.current_user.is_authenticated
    """

    column_display_pk = True

    can_delete = True # we only want to delete through Auth0
    can_create = True # we only want to create through Auth0
    column_searchable_list = ('status', 'date_applied', 'date_accepted', \
        'first_name', 'last_name', 'email', 'how_they_found', 'current_firm_name', 'biography', \
        'undergrad_education', 'grad_education', 'city', 'state', 'subspecialty_text')



    form_columns = ['email', 'status', 'date_applied', 'date_accepted', 'first_name', 'last_name', \
                     'years_of_experience', 'how_they_found', 'referral_user', 'specialties', 'occupations', \
                    # 'previous_firm',
                    'posted_projects', \
                     'current_firm_name', 'current_firm_size', 'current_firm_revenue', 'biography', \
                     'undergrad_education', 'grad_education', 'resume_url', 'city', 'state', 'specialties',
                    'subspecialty_text']


    form_choices = {
        'status': [('Invited', 'Invited'), ('Pending', 'Pending'), ('Active', 'Active'), \
            ('Deactivated', 'Deactivated')],
        'occupation': [(occup.pk_id, occup.name) for occup in Occupation.query.all()],
        #'specialty': [(spec.pk_id, spec.name) for spec in Specialty.query.all()],
        # 'previous_firm': [(firm.pk_id, firm.name) for firm in BigFirm.query.all()]
    }

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read', 'advisors')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create', 'advisors'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit', 'advisors'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete', 'advisors'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class AdvisorApplicantView(ModelView):
    """
    view for AdvisorApplicant table
    """
    column_searchable_list = ('status', 'date_applied', \
        'first_name', 'last_name', 'email', 'how_they_found', 'current_firm', 'short_bio', \
        'undergrad_education', 'grad_education', 'city', 'state', 'subspecialties_text')

    form_columns = [ 'email', 'status', 'date_applied', 'first_name', 'last_name', \
                     'years_of_experience', 'years_of_bigfirm_experience', 'how_they_found', 'referral_user', 'specialties', 'occupation', \
                     'city', 'state', 'previous_firms', 'current_firm', 'current_firm_size', 'current_firm_revenue', \
                     'short_bio', 'undergrad_education', 'grad_education',
                     'company_url', 'profile_pic_url', 'linkedin_picture_url', 'specialties', 'subspecialties_text'
                     ]

    form_choices = {
        'status': [('Applied', 'Applied'), ('Declined', 'Declined')],
        'occupation': [(occup.pk_id, occup.name) for occup in Occupation.query.all()],
        # 'specialty': [(spec.pk_id, spec.name) for spec in Specialty.query.all()],
        # 'previous_firm': [(firm.pk_id, firm.name) for firm in BigFirm.query.all()]
    }


    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read', 'advisorapplicants')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create', 'advisorapplicants'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit', 'advisorapplicants'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete', 'advisorapplicants'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class ProjectView(ModelView):
    """
    view for Project table
    """
    column_searchable_list = ('title', 'date_created', \
        'description')

    form_choices = {
        'status': [('Open', 'Open'), ('Closed', 'Closed')]
    }

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read', 'projects')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','projects'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','projects'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','projects'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class RoleView(ModelView):
    """
    view for Role table
    """
    form_choices = {
        'table_name': [('admins','Admins'), ('roles','Roles'), \
                       ('advisorapplicants', 'Advisor Applicants'), \
                       ('advisors', 'Advisors'), ('projects', 'Projects'), \
                       ('specialties', 'Specialties'), ('bigfirms', 'Big Firms'), \
                       ('occupations', 'Occupations'), ('occupationtypes', 'Occupation Types'),\
                       ('updates', 'Updates'), ('mn_activity', 'Mighty Network Activity')]
    }

    column_labels = dict(AdminLogin='Admins with this Role')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','roles')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','roles'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','roles'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','roles'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class AdminLoginView(ModelView):
    """
    view for AdminLogin table
    """
    column_searchable_list = ('email',)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','admins')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','admins'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','admins'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','admins'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class SpecialtyView(ModelView):
    """
    view for Specialty table
    """
    column_display_pk = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','specialties')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','specialties'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','specialties'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','specialties'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class SubspecialtyView(ModelView):
    """
    view for Subspecialty table
    """
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','subspecialties')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','subspecialties'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','subspecialties'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','subspecialties'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class UpdateView(ModelView):
    """
    view for Subspecialty table
    """
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','updates')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','updates'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','updates'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','updates'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class MNActivityView(ModelView):
    """
    view for Subspecialty table
    """
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','mn_activity')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','mn_activity'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','mn_activity'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','mn_activity'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class BigFirmView(ModelView):
    """
    view for BigFirm table
    """
    column_searchable_list = ('name',)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','bigfirms')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','bigfirms'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','bigfirms'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','bigfirms'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class LinkedInView(BaseView):
    """
    Custom view for signing in with LinkedIn and creating AdvisorApplicants from that data
    """
    @expose('/')
    def index(self):
        return self.render('custom_linkedin.html')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_edit','advisorapplicants') \
            and user_has_permission(current_user, 'can_create','advisorapplicants')

    def _handle_view(self, name, **kwargs):
            """
            Override builtin _handle_view in order to redirect users when a view is not accessible.
            """
            if not self.is_accessible():
                if current_user.is_authenticated:
                    # permission denied
                    abort(403)
                else:
                    # login
                    return redirect(url_for('security.login', next=request.url))

class OccupationView(ModelView):
    """
    view for Occupation table
    """
    column_display_pk = True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','occupations')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','occupations'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','occupations'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','occupations'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class OccupationTypeView(ModelView):
    """
    view for OccupationType table
    """
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return user_has_permission(current_user, 'can_read','occupationtypes')

    def on_model_change(self, form, model, is_created):
        """
        Called before a model is created or updated. Checks permissions to ensure
        only authorized users are able to perform those actions.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        elif is_created:
            if not user_has_permission(current_user, 'can_create','occupationtypes'):
                abort(403)
        else:
            if not user_has_permission(current_user, 'can_edit','occupationtypes'):
                abort(403)

    def on_model_delete(self, model):
        """
        Called before a model is deleted. Checks permissions to ensure
        only authorized users are able to perform this action.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            abort(403)
        if not user_has_permission(current_user, 'can_delete','occupationtypes'):
            abort(403)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
