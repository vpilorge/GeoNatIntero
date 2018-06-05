import datetime
from geonature.utils.env import DB

class Export(DB.Model):
    __tablename__ = 't_exports'
    __table_args__ = {'schema': 'gn_intero'}
    submission = DB.Column(DB.TIMESTAMP(timezone=False), primary_key=True)
    status = DB.Column(DB.Numeric, default=-2)
    selection = DB.Column(DB.UnicodeText)
    log = DB.Column(DB.UnicodeText)
    start = DB.Column(DB.DateTime)
    end = DB.Column(DB.DateTime)
    # TODO: FK_EXPORT_TYPE

    def __init__(self, selection):
        self.selection = selection or ','.join([
            'nomCite',
            'dateDebut', 'dateFin',
            'heureDebut', 'heureFin',
            'altMax', 'altMin',
            'cdNom', 'cdRef'
        ])
        self.submission = datetime.datetime.utcnow()

    def __repr__(self):
        return "<Export(submission='%s', selection='%s')>".format(
            self.submission, self.selection)
