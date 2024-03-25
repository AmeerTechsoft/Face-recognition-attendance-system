from flask import Blueprint

blueprint = Blueprint(
    'lecturer_blueprint',
    __name__,
    url_prefix='/lecturer'
)
