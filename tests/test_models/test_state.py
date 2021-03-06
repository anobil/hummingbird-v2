from unittest import TestCase
from app import app, db
from models import State
from tests.runner import clear_db


class TestStateMethods(TestCase):

    def setUp(self):
        self.app_context = app.test_request_context()
        self.app_context.push()
        app.test_client()
        self.app = app
        db.create_all()
        self.db = db

    def tearDown(self):
        clear_db(self.db)

    def test_if_save_method_saves_state_on_database(self):
        State().save(self.db.session, abbreviation='SP', name='São Paulo',
                     lat=12.0001, lng=25.0001)
        self.db.session.commit()
        _model = self.db.session.query(State).filter_by(abbreviation='SP').first()
        self.assertIsNotNone(_model)
