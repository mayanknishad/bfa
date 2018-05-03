"""
database initialization and setup
"""


def init_db(app):
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Initializes database and creates the tables
    """
    from app.models import db, Role, AdminLogin, Project
    from flask_security import Security, SQLAlchemyUserDatastore
    from flask_migrate import Migrate
    db.init_app(app)
    app.app_context().push()

    # Initialize the SQLAlchemy data store and Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, AdminLogin, Role)
    security_bp = Security(app, user_datastore)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # db.drop_all() # drops tables, won't drop functions or anything else
    # db.create_all()

    """
    only run configure_mappers() and create_all() once, because
    create_all() will throw an error that the tsvector functions
    already exist. With tables, create_all() can recognize they already
    exist and then not create them again, but with functions it struggles
    and will try to create the functions that already exist in the database.
    """
    # db.configure_mappers() # need this to enable TsVector triggers
    # db.create_all()
    # # insert dummy data
    # from app.dummy_data import insert_dummy_data
    # insert_dummy_data(db)

    # Create a default superuser that has all permissions
    user_datastore.find_or_create_role(name="superuser_admins",
                                       table_name='admins',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_roles",
                                       table_name='roles',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)
    user_datastore.find_or_create_role(name="superuser_advisorapplicants",
                                       table_name='advisorapplicants',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_advisors",
                                       table_name='advisors',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_projects",
                                       table_name='projects',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_specialties",
                                       table_name='specialties',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_subspecialties",
                                       table_name='subspecialties',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_bigfirms",
                                       table_name='bigfirms',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_occupations",
                                       table_name='occupations',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="superuser_occupationtypes",
                                       table_name='occupationtypes',
                                       can_read=True,
                                       can_edit=True,
                                       can_create=True,
                                       can_delete=True)

    user_datastore.find_or_create_role(name="can_edit_advisorapplicants")
    user_datastore.find_or_create_role(name="can_create_advisors", )

    if not user_datastore.get_user(app.config['SUPERUSER_ADMIN_EMAIL']):
        user_datastore.create_user(email=app.config['SUPERUSER_ADMIN_EMAIL'],
                                   password=app.config['SUPERUSER_ADMIN_PASSWORD'],
                                   active=True,
                                   analytics_access=True,
                                   database_access=True)
    db.session.commit()



    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_admins")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_roles")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_advisorapplicants")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_advisors")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_projects")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_specialties")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_subspecialties")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_bigfirms")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_occupations")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser_occupationtypes")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "can_edit_advisorapplicants")
    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "can_create_advisors")

    db.session.commit()

    db.session.close()

    return security_bp
