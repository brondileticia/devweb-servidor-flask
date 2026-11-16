from flask import Blueprint

bp = Blueprint('emails', __name__)

from app.emails import routes  # noqa
