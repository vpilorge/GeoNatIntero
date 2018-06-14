import os
from datetime import datetime, time
import psycopg2
from flask import (
    Blueprint, request, current_app, send_from_directory, request, jsonify)
from geonature.utils.env import DB
from geonature.utils.errors import GeonatureApiError
# from geonature.core.users.models import TRoles, UserRigth
# from pypnusershub.db.tools import InsufficientRightsError
# from pypnusershub import routes as fnauth

from .models import Export, Format, format_map_ext
# FIXME: import backend/frontend/jobs shared conf


blueprint = Blueprint('export', __name__)


@blueprint.route('/add', methods=['GET'])
# @fnauth.check_auth_cruved('R')
def add():
    selection = request.args.get('selection', None)
    format = request.args.get('format', Format.CSV)
    export = Export(selection, format)
    submissionID = export.id
    DB.session.add(export)
    DB.session.commit()
    # utc datetime Export.submission -> µs timestamp submissionID
    submissionID = export.ts()
    return jsonify(id=submissionID, selection=selection, format=format)


@blueprint.route('/progress/<submissionID>')
def progress(submissionID):
    try:
        # µs timestamp submissionID -> utc datetime Export.submission
        submission = datetime.utcfromtimestamp(float(submissionID))
        # ranking: 'SELECT COUNT(id) FROM gn_intero.t_exports WHERE status = -2 AND id < %s', id)
        export = Export.query.get(id)
        return jsonify(
                submission=submission,
                format=format_map_ext[format],
                status=str(export.status),
                start=str(export.start),
                end=str(export.end),
                log=str(export.log)
            ) if export else jsonify(submission='null')
    except ValueError as e:
        return jsonify(str(e))


@blueprint.route('/exports/<path:export>')
# @fnauth.check_auth_cruved('R')
def getExport(export):
    try:
        return send_from_directory(
            os.path.join(current_app.static_folder, 'exports'),
            export, mimetype='text/csv', as_attachment=True)  # TODO: json mimetype
    except Exception as e:
        return str(e)


@blueprint.route('/exports')
# @fnauth.check_auth_cruved('R')
def getExports():
    # FIXME: poc specs !
    # midnight = datetime.combine(datetime.today(), time.min)
    # .filter(Export.end>=midnight)\
    exports = Export.query\
                    .filter(Export.status == 0)\
                    .order_by(Export.end.desc())\
                    .limit(6)\
                    .all()
    export_fname = os.path.join(current_app.static_folder, 'exports', 'export_{id}.{ext}'.format(id=export.ts(), ext='csv'))  # TODO: JSON
    exports = [
        (export_fname, export.id)
        for export in exports if os.path.exists(export_fname) and os.path.isfile(export_fname)]
    return jsonify(exports)
