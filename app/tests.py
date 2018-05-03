"""
Tests.py - Contains unit tests to check the validity of all of our
database's models.
"""

import unittest
import datetime
from models import db, AdminLogin, Role, AdvisorApplicant, Advisor, Project
from flask import Flask
from flask_sqlalchemy import SQLAlchemy



class ModelUnitTests(unittest.TestCase):

    """
    ModelUnitTests will create a new database in memory for each
    test and verify that adding entries and querying for them will
    return expected results.
    """

    def setUp(self):
        self.app = Flask(__name__)
        self.db = db
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

        # self.base = Base
        # self.engine = create_engine("")
        # self.made_db.session = db.sessionmaker(bind=self.engine)
        # self.db.session = self.made_db.session()
        # self.base.metadata.create_all(self.engine)

    def tearDown(self):
        with self.app.app_context():
            self.db.drop_all()


    # These tests check the Role model

    def test_role_1(self):
        """
        Creates a role in the Role table, and then checks that the stored value matches the intended value.
        """
        # Column values
        test_name = "Test_Role1"

        test_can_delete_adminlogins = True
        test_can_edit_adminlogins = False
        test_can_create_adminlogins = True

        test_analytics_access = False
        test_database_access = True

        test_role = Role(name=test_name,
                         can_delete_adminlogins=test_can_delete_adminlogins,
                         can_edit_adminlogins=test_can_edit_adminlogins,
                         can_create_adminlogins=test_can_create_adminlogins,
                         analytics_access=test_analytics_access,
                         database_access=test_database_access)

        test_role_id = test_role.id
        with self.app.app_context():
            self.db.session.add(test_role)
            self.db.session.commit()
            self.assertTrue(test_role in self.db.session)
            queried_role = self.db.session.query(Role).filter_by(name="Test_Role1").first()

        self.assertEqual(queried_role.id, test_role_id)
        self.assertEqual(queried_role.name, test_name)
        self.assertEqual(queried_role.can_delete_adminlogins, test_can_delete_adminlogins)
        self.assertEqual(queried_role.can_edit_adminlogins, test_can_edit_adminlogins)
        self.assertEqual(queried_role.can_create_adminlogins, test_can_create_adminlogins)
        self.assertEqual(queried_role.can_create_roles, False)
        self.assertEqual(queried_role.analytics_access, test_analytics_access)
        self.assertEqual(queried_role.database_access, test_database_access)



    # These tests check the AdminLogin model

    def test_admin_1(self):
        """
        Creates a role in the Role table, queries for the role's generated ID, and then creates a new
        Admin in the AdminLogin table with that role ID. Inserts the new Admin into the AdminLogin table,
        then queries for it and verifies that it has all of the appropriate columns.
        """
        test_role = Role(name="AllFalse_Test_Role1")
        test_role_id = test_role.id

        with self.app.app_context():
            self.db.session.add(test_role)
            self.db.session.commit()
            self.assertTrue(test_role in self.db.session)

        test_email = "test1@email.com"
        test_password = "password-test-1"

        test_admin = AdminLogin(email=test_email, password=test_password)
        test_admin.roles.append(test_role)
        with self.app.app_context():
            self.db.session.add(test_admin)
            self.db.session.commit()
            self.assertTrue(test_admin in self.db.session)

            queried_admin = self.db.session.query(AdminLogin).filter_by(email="test1@email.com").first()
            queried_admin_roles = queried_admin.roles

        self.assertEqual(queried_admin.email, test_email)
        self.assertEqual(queried_admin.password, test_password)
        self.assertEqual(queried_admin_roles[0].name, "AllFalse_Test_Role1")


    # Maybe add some tests to check if duplicate insertion causes problems?

    # These tests check the AdvisorApplicant model
    def test_advisorapplicant_1(self):
        """
        Creates an advisor applicant in the AdvisorApplicant table, checks if stored values match intended values.
        """
        test_first_name = "First Name"
        test_last_name = "Last Name"
        test_email = "emailaddress@email.com"
        test_recommended_advisors = "recommendation@email.com"
        test_advisorapplicant = AdvisorApplicant(first_name=test_first_name,
                                                 last_name=test_last_name, email=test_email,
                                                 recommended_advisors=test_recommended_advisors)
        test_pk_id = test_advisorapplicant.pk_id

        with self.app.app_context():
            self.db.session.add(test_advisorapplicant)
            self.db.session.commit()
            self.assertTrue(test_advisorapplicant in self.db.session)

            queried_advisorapplicant = self.db.session.query(AdvisorApplicant).filter_by(email="emailaddress@email.com").first()

        self.assertEqual(queried_advisorapplicant.first_name, test_first_name)
        self.assertEqual(queried_advisorapplicant.last_name, test_last_name)
        self.assertEqual(queried_advisorapplicant.email, test_email)
        self.assertEqual(queried_advisorapplicant.pk_id, test_pk_id)
        self.assertEqual(queried_advisorapplicant.recommended_advisors, test_recommended_advisors)
        self.assertEqual(queried_advisorapplicant.status, 'Pending Decision')


    # These tests check the Advisor model

    def test_advisor_1(self):
        """
        Creates an advisor in the Advisor table, checks if stored values match intended values.
        """
        test_first_name = "First Name"
        test_last_name = "Last Name"
        test_email = "emailaddress@email.com"
        test_advisor = Advisor(first_name=test_first_name,
                               last_name=test_last_name, email=test_email)
        test_pk_id = test_advisor.pk_id

        with self.app.app_context():
            self.db.session.add(test_advisor)
            self.db.session.commit()
            self.assertTrue(test_advisor in self.db.session)

            queried_advisor = self.db.session.query(Advisor).filter_by(email="emailaddress@email.com").first()
        self.assertEqual(queried_advisor.first_name, test_first_name)
        self.assertEqual(queried_advisor.last_name, test_last_name)
        self.assertEqual(queried_advisor.email, test_email)
        self.assertEqual(queried_advisor.pk_id, test_pk_id)
        self.assertEqual(queried_advisor.status, 'Active')


    # These tests check the Project model

    def test_project_1(self):
        """
        Creates a project in the Project table, checks if stored values match intended values.
        """
        test_project_name = "Test Project"
        test_body = "Test Body"
        test_project = Project(title=test_project_name, body=test_body)
        test_pk_id = test_project.pk_id

        with self.app.app_context():
            self.db.session.add(test_project)
            self.db.session.commit()
            self.assertTrue(test_project in self.db.session)
            queried_project = self.db.session.query(Project).filter_by(date_created=datetime.date.today()).first()

        self.assertEqual(queried_project.pk_id, test_pk_id)
        self.assertEqual(queried_project.date_created, datetime.date.today())
        self.assertEqual(queried_project.title, test_project_name)
        self.assertEqual(queried_project.body, test_body)



if __name__ == '__main__':
    unittest.main()