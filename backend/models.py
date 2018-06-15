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
    # https://www.w3.org/2008/01/rdf-media-types
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


class Export(DB.Model):
    __tablename__ = 't_exports'
    __table_args__ = {'schema': 'gn_intero'}
    id = DB.Column(DB.TIMESTAMP(timezone=False), primary_key=True, nullable=False)
    format = DB.Column(DB.Integer, nullable=False)
    selection = DB.Column(DB.UnicodeText, default='*')
    standard = DB.Column(DB.Numeric, default=0)
    status = DB.Column(DB.Numeric, default=-2)
    log = DB.Column(DB.UnicodeText)
    start = DB.Column(DB.DateTime)
    end = DB.Column(DB.DateTime)

    def __init__(self, standard, format):
        self.standard = standard
        self.id = datetime.utcnow()
        self.format = int(format)

    def __repr__(self):
        return "<Export(id='{}', date='{}', standard='{}', format='{}')>".format(
            self.ts(), self.start, self.standard, self.format)

    def as_dict(self):
        return {
            'path': float(self.id.timestamp()),
            'extension': format_map_ext[self.format],
            'standard': standard_map_label[self.standard],
            'date': self.start
        }

    def ts(self):
        return (datetime.strptime(str(self.id), '%Y-%m-%d %H:%M:%S.%f') - datetime.utcfromtimestamp(0)).total_seconds()
