import datetime
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


class Standard(IntEnum):
    DRWC = 1
    ABCD = 2
    EML = 4


class Export(DB.Model):
    __tablename__ = 't_exports'
    __table_args__ = {'schema': 'gn_intero'}
    id = DB.Column(DB.TIMESTAMP(timezone=False), primary_key=True, nullable=False)
    format = DB.Column(DB.Integer, nullable=False)  # TODO: FK_EXPORT_TYPE
    status = DB.Column(DB.Numeric, default=-2)
    selection = DB.Column(DB.UnicodeText, nullable=False)
    log = DB.Column(DB.UnicodeText)
    start = DB.Column(DB.DateTime)
    end = DB.Column(DB.DateTime)

    def __init__(self, selection, format):
        self.selection = selection or ','.join([
            'nomCite',
            'dateDebut', 'dateFin',
            'heureDebut', 'heureFin',
            'altMax', 'altMin',
            'cdNom', 'cdRef'
        ])
        self.id = datetime.datetime.utcnow()
        self.format = int(format)

    def __repr__(self):
        return "<Export(submission='%s', selection='%s')>".format(
            self.id, self.selection)

    def ts(self):
        return (datetime.strptime(str(self.id), '%Y-%m-%d %H:%M:%S.%f') - datetime.utcfromtimestamp(0)).total_seconds()
