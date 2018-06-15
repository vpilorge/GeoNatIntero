import os
from flask import (
    Blueprint, request, current_app, send_from_directory, jsonify)
from geonature.utils.env import DB
# from geonature.utils.errors import GeonatureApiError
# from geonature.core.users.models import TRoles, UserRigth
# from pypnusershub.db.tools import InsufficientRightsError
# from pypnusershub import routes as fnauth

from .models import (Export, Format, format_map_ext, format_map_mime,
                     Standard, standard_map_label)
# FIXME: backend/frontend/jobs shared conf


blueprint = Blueprint('export', __name__)


@blueprint.route('/add', methods=['GET'])
# @fnauth.check_auth_cruved('R')
def add():
    standard = request.args.get('standard', Standard)
    formats = [Format.CSV, Format.JSON]
    export = None
    for format in formats:
        export = Export(standard, format)
        DB.session.add(export)
    DB.session.commit()
    submissionID = export.ts()
    # utc datetime Export.submission -> µs timestamp submissionID
    return jsonify(id=submissionID, standard=standard, format=format)


# @blueprint.route('/progress/<submissionID>')
# def progress(submissionID):
#     try:
#         # µs timestamp submissionID -> utc datetime Export.submission
#         submission = datetime.utcfromtimestamp(float(submissionID))
#         # ranking: 'SELECT COUNT(id) FROM gn_intero.t_exports WHERE status = -2 AND id < %s', id)  # noqa
#         export = Export.query.get(id)
#         return jsonify(
#                 submission=submission,
#                 format=format_map_ext[format],
#                 status=str(export.status),
#                 start=str(export.start),
#                 end=str(export.end),
#                 log=str(export.log)
#             ) if export else jsonify(submission='null')
#     except ValueError as e:
#         return jsonify(str(e))


@blueprint.route('/exports/<path:export>')
# @fnauth.check_auth_cruved('R')
def getExport(export):
    # if not file.exists:
        # trigger export etl
    try:
        return send_from_directory(
            os.path.join(current_app.static_folder, 'exports'),
            export,  # mimetype='',  # FIXME: mimetypes
            as_attachment=True)
    except Exception as e:
        return str(e)


@blueprint.route('/exports')
# @fnauth.check_auth_cruved('R')
def getExports():
    exports_list = Export.query\
                         .filter(Export.status >= 0)\
                         .group_by(Export.standard, Export.id)\
                         .all()
    standards = {}
    for export in exports_list:
        std = standard_map_label[export.standard]
        if not standards.get(std, None):
            standards[std] = [export.as_dict()]
        else:
            standards[std].append(export.as_dict())
    return jsonify(standards)


def fname(export):
    # super sloooow:
    # if os.path.exists(fname(export)) and os.path.isfile(fname(export))]
    return os.path.join(
        current_app.static_folder, 'exports',
        'export_{std}_{id}.{ext}'.format(
            std=standard_map_label[export.standard],
            id=export.ts(), ext=format_map_ext[export.format]))
