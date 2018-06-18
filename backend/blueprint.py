import os
from flask import (
    Blueprint, request, current_app, send_from_directory, jsonify)
from geonature.utils.env import DB
# from geonature.utils.errors import GeonatureApiError
# from geonature.core.users.models import TRoles, UserRigth
# from pypnusershub.db.tools import InsufficientRightsError
# from pypnusershub import routes as fnauth

from .models import (Export,
                     Format, format_map_ext,  # format_map_mime,
                     Standard, standard_map_label)
# FIXME: backend/frontend/jobs shared conf
EXPORTS_FOLDER = os.path.join(current_app.static_folder, 'exports')


blueprint = Blueprint('export', __name__)


@blueprint.route('/add', methods=['GET'])
# @fnauth.check_auth_cruved('R')
def add():
    selection = request.args.get('selection', '*')

    standards = [Standard.SINP, Standard.DWC]
    formats = [Format.CSV, Format.JSON]
    export = None
    for standard in standards:
        for format in formats:
            export = Export(selection, standard, format)
            DB.session.add(export)
    DB.session.commit()

    submissionID = export.ts()  # fallback export ref ?
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
    # FIXME: mimetype
    filename, standard, id, extension = fname(export)
    p = os.path.join(current_app.static_folder, 'exports', filename)
    print(p, os.path.exists(p) and os.path.isfile(p))

    try:
        return send_from_directory(
            EXPORTS_FOLDER, filename,  # mimetype=format_map_ext[],
            as_attachment=True)
    except Exception as e:
        return str(e)


@blueprint.route('/exports')
# @fnauth.check_auth_cruved('R')
def getExports():
    exports = Export.query\
                    .filter(Export.status >= 0)\
                    .group_by(Export.id_export, Export.id)\
                    .all()
    return jsonify([export.as_dict() for export in exports])


def fname(export):
    rest, ext = export.rsplit('.', 1)
    _, std, id = rest.split('_')
    print(std, id, ext)
    return 'export_{std}_{id}.{ext}'.format(std=std, id=id, ext=ext), std, id, ext
