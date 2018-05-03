from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.models import db, Advisor, AdminLogin, AdvisorApplicant, Project, Role, \
    Specialty, Subspecialty, BigFirm, Occupation, OccupationType, Update, MNActivity, Vendor, Promotion
from app.admin_dashboard import AdvisorView, AdminLoginView, \
     AdvisorApplicantView, ProjectView, RoleView, SpecialtyView, \
     SubspecialtyView, BigFirmView, AdvisorApprovalView, LinkedInView, \
     OccupationView, OccupationTypeView, AdvisorAuthView, UpdateView, \
     MNActivityView

def configure_admin(app):
    admin = Admin(
        app,
        'BFA Admin',
        base_template='my_master.html',
        template_mode='bootstrap3',
    )

    # Add view
    admin.add_view(AdvisorView(Advisor, db.session))
    admin.add_view(AdvisorApplicantView(AdvisorApplicant, db.session))
    admin.add_view(AdvisorApprovalView(name='Advisor Approval', endpoint='advisorapproval'))
    admin.add_view(ProjectView(Project, db.session))
    admin.add_view(RoleView(Role, db.session))
    admin.add_view(AdminLoginView(AdminLogin, db.session))
    admin.add_view(SpecialtyView(Specialty, db.session))
    admin.add_view(SubspecialtyView(Subspecialty, db.session))
    admin.add_view(BigFirmView(BigFirm, db.session))
    admin.add_view(LinkedInView(name='LinkedIn View', endpoint='linkedinview'))
    admin.add_view(AdvisorAuthView(name='Advisor Login View', endpoint='advisorauthview'))
    admin.add_view(OccupationView(Occupation, db.session))
    admin.add_view(OccupationTypeView(OccupationType, db.session))
    admin.add_view(UpdateView(Update, db.session))
    admin.add_view(MNActivityView(MNActivity, db.session))

    admin.add_view(ModelView(Vendor, db.session))
    admin.add_view(ModelView(Promotion, db.session))

    return admin
