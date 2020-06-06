import time

from authlib_gino.fastapi_session.gino_app import load_entry_point
from authlib_gino.fastapi_session.models import Identity
from authlib_gino.gino_oauth2.functions import id_generator
from gino import Gino

db = load_entry_point("db", Gino)


class SMSIdentity(Identity):
    sms_prefix = db.StringProperty()
    sms_number = db.StringProperty()


class LoginSMS(db.Model):
    __tablename__ = "login_sms"

    id = db.Column(db.Text(), primary_key=True, default=id_generator("sms", 48))
    prefix = db.Column(db.Text(), nullable=False)
    number = db.Column(db.Text(), nullable=False)
    code = db.Column(db.Text(), nullable=False)
    created_at = db.Column(
        db.Integer(), nullable=False, default=lambda: int(time.time())
    )
    consumed_at = db.Column(db.Integer())
