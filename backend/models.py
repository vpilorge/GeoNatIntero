from datetime import datetime
from geonature.utils.env import DB
from enum import IntEnum


class Format(IntEnum):
    CSV = 1
    JSON = 2
    RDF = 4


format_map_ext = {
    Format.CSV: 'csv',
    Format.JSON: 'json',
    Format.RDF: 'rdf'
}

format_map_mime = {
    Format.CSV: 'text/csv',
    Format.JSON: 'application/json',
    # https://www.w3.org/2008/01/rdf-media-types
    # XML       serialization of RDF	        application/rdf+xml
    Format.RDF: 'application/rdf+xml'
    # simple    serialization of RDF	        text/plain
    # turtle	textual serialization of RDF	application/x-turtle
    # n3	    extension¹ of turtle language 	text/rdf+n3 (not registered)
}


class Standard(IntEnum):
    NONE = 0
    SINP = 1
    DWC = 2
    ABCD = 4
    EML = 8


standard_map_label = {
    Standard.NONE: 'RAW',
    Standard.SINP: 'SINP',
    Standard.DWC: 'DarwinCore',
    Standard.ABCD: 'ABCD Schema',
    Standard.EML: 'EML'
}


class ExportType(DB.Model):
    __tablename__ = 't_exports'
    __table_args__ = {'schema': 'gn_intero', 'extend_existing': True}
    id = DB.Column(DB.Integer, primary_key=True, nullable=False)
    label = DB.Column(DB.Text, nullable=False)
    selection = DB.Column(DB.Text, nullable=False)


class Export(DB.Model):
    __tablename__ = 't_exports_logs'
    __table_args__ = {'schema': 'gn_intero', 'extend_existing': True}
    id = DB.Column(DB.TIMESTAMP(timezone=False),
                   primary_key=True, nullable=False)
    standard = DB.Column(DB.Numeric, default=0)
    format = DB.Column(DB.Integer, nullable=False)
    status = DB.Column(DB.Numeric, default=-2)
    log = DB.Column(DB.UnicodeText)
    start = DB.Column(DB.DateTime)
    end = DB.Column(DB.DateTime)
    id_export = DB.Column(
        DB.Integer(), DB.ForeignKey('gn_intero.t_exports.id'))
    export = DB.relationship('ExportType', foreign_keys='Export.id_export',
                             backref=DB.backref('ExportType', lazy='dynamic'))

    def __init__(self, standard, format):
        self.standard = standard
        self.id = datetime.utcnow()
        self.format = int(format)

    def __repr__(self):
        return "<Export(id='{}', selection='{}', date='{}', standard='{}', format='{}')>".format(  # noqa
            self.ts(), self.export.selection, self.start, self.standard, self.format)  # noqa

    def as_dict(self):
        return {
            'id': float(self.id.timestamp()),
            'extension': format_map_ext[self.format],
            'selection': self.export.selection,
            'label': self.export.label,
            'standard': standard_map_label[self.standard],
            'date': self.start
        }

    def ts(self):
        return (datetime.strptime(str(self.id), '%Y-%m-%d %H:%M:%S.%f')
                - datetime.utcfromtimestamp(0)).total_seconds()
