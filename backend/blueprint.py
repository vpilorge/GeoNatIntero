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

from .models import Export
# FIXME: import backend/frontend/jobs shared conf


blueprint = Blueprint('export', __name__)


@blueprint.route('/add', methods=['GET'])
# @fnauth.check_auth_cruved('R')
def add():
    selection = request.args.get('selection', None)
    export = Export(selection)
    submissionID = export.submission
    DB.session.add(export)
    DB.session.commit()
    # utc datetime Export.submission -> µs timestamp submissionID
    submissionID = (
        datetime.strptime(str(submissionID), '%Y-%m-%d %H:%M:%S.%f') -
        datetime.utcfromtimestamp(0)).total_seconds()
    return jsonify(id=submissionID, selection=selection)


@blueprint.route('/progress/<submissionID>')
def progress(submissionID):
    try:
        # µs timestamp submissionID -> utc datetime Export.submission
        submission = datetime.utcfromtimestamp(float(submissionID))
        # ranking: 'SELECT COUNT(submission) FROM gn_intero.t_exports WHERE status = -2 AND submission < %s', submission)
        export = Export.query.get(submission)
        return jsonify(
                submission=submission,
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
            export, mimetype='text/csv', as_attachment=True)
    except Exception as e:
        return str(e)


@blueprint.route('/exports')
# @fnauth.check_auth_cruved('R')
def getExports():
    # FIXME: poc specs !
    # midnight = datetime.combine(datetime.today(), time.min)
    # .filter(Export.end>=midnight)\
    exports = Export.query\
                    .filter(Export.status==0)\
                    .order_by(Export.end.desc())\
                    .limit(6)\
                    .all()
    exports = [
        ('export_{id}.{ext}'.format(
            id=(datetime.strptime(str(export.submission), '%Y-%m-%d %H:%M:%S.%f') -
            datetime.utcfromtimestamp(0)).total_seconds(), ext='csv'), export.submission)
        for export in exports if os.path.exists(  # and isfile()
            os.path.join(current_app.static_folder, 'exports', 'export_{id}.{ext}'.format(
                id=(datetime.strptime(str(export.submission), '%Y-%m-%d %H:%M:%S.%f') -
                datetime.utcfromtimestamp(0)).total_seconds(), ext='csv')))]
    return jsonify(exports)
