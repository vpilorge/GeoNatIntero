import os
from flask import (
    Blueprint, request, current_app, send_from_directory, jsonify)
from geonature.utils.env import DB
# from geonature.utils.errors import GeonatureApiError
# from geonature.core.users.models import TRoles, UserRigth
# from pypnusershub.db.tools import InsufficientRightsError
# from pypnusershub import routes as fnauth

from .models import (Export,
                     Format, format_map_ext, format_map_mime,
                     Standard, standard_map_label)
EXPORTS_FOLDER = os.path.join(current_app.static_folder, 'exports')
# FIXME: backend/frontend/jobs shared conf


blueprint = Blueprint('export', __name__)


@blueprint.route('/add', methods=['GET'])
# @fnauth.check_auth_cruved('R')
def add():
    selection = request.args.get('selection', '*')
    # FIXME: app logic + fk_selection + add(...)
    standards = [Standard.SINP, Standard.DWC]
    formats = [Format.CSV, Format.JSON]
    export = None
    exports = []
    for standard in standards:
        for format in formats:
            export = Export(int(standard), format, selection)
            DB.session.add(export)
            exports.append(export)
    DB.session.commit()
    return jsonify([{
            'id': export.id,
            'standard': standard_map_label[export.standard],
            'format': format_map_ext[export.format].upper()
        } for export in exports])


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
    filename, standard, id, extension = fname(export)
    mime = [format_map_mime[k]
            for k, v in format_map_ext.items() if v == extension][0]
    try:
        return send_from_directory(
            EXPORTS_FOLDER, filename, mimetype=mime, as_attachment=True)
    except Exception as e:
        return str(e)


@blueprint.route('/exports')
# @fnauth.check_auth_cruved('R')
def getExports():
    # FIXME: export selection, order, limit
    exports = Export.query\
                    .filter(Export.status >= 0)\
                    .group_by(Export.id_export, Export.id)\
                    .order_by(Export.id.desc())\
                    .limit(50)\
                    .all()
    return jsonify([export.as_dict() for export in exports])


def fname(export):
    rest, ext = export.rsplit('.', 1)
    _, std, id = rest.split('_')
    return ('export_{std}_{id}.{ext}'.format(std=std, id=id, ext=ext),
            std, id, ext)
