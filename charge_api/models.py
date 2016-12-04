from . import db


class Charge(db.Model):
    """
    Simplified model for a port handling charge.

    Obvious improvements:
    * Port, country and city are clearly separate entities.
    * Associate values with a creation date or data set. I was a bit surprised
      to see that this wasn't the case already considering it involves
      specific currencies.
    """

    __tablename__ = "charge"

    charge_id = db.Column(db.Integer(), primary_key=True)
    country_code = db.Column(db.String(2))
    city_code = db.Column(db.String(3))
    supplier_id = db.Column(db.Integer())
    currency = db.Column(db.String(3))
    value = db.Column(db.Float())
    valid = db.Column(db.Boolean(), default=None)


class Distribution(db.Model):
    """
    Simplified model for caching of statistical distribution info.

    Obvious improvements:
    * Could store historical data with a created field.
    * Could store more statistical information like mean, stddev, etc, to
      allow more flexibility in the algorithm without at lof ot changes.
    * Could be stored in redis or something similar.
    """

    __tablename__ = "distribution"

    country_code = db.Column(db.String(2), primary_key=True)
    median = db.Column(db.Float())
    mad_threshold = db.Column(db.Float())
