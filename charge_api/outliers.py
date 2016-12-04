import numpy as np

from . import db
from .models import Charge, Distribution


# We know prices will change over time, so some lee-way around the MAD is
# necessary. We'd want the scaling to be as low as possible to be precise,
# and as big as possible to accept reasonable variations.
THRESHOLD_FACTOR = 4


def mark_outliers(charges):
    """
    Mark `charges` as outliers or not in the database.

    Arguments:
      charges -- list of Charge objects to mark.
    """

    distributions_seen = {}

    for charge in charges:
        country_code = charge.country_code
        dist = distributions_seen.get(country_code)

        if not dist:
            dist = get_or_create_distribution(country_code)
            distributions_seen[country_code] = dist

        charge.valid = not is_outlier(charge, dist)

    db.session.bulk_save_objects(charges)
    db.session.commit()


def get_or_create_distribution(country_code):
    """
    Django-eqsue function for getting or creating a non-existent Distribution.
    """

    dist = Distribution.query.filter_by(country_code=country_code).first()

    if not dist:
        dist = update_distributions([country_code])[0]

    return dist


def update_distributions(country_codes):
    """
    Update the distribution information for `country_codes` in the database.

    Arguments:
      country_codes -- list of country codes to update information for.
    """

    # We'd probably want to store historical information, but in this case,
    # I'll just regenerate the set for simplicity.
    db.session.query(Distribution.country_code.in_(country_codes)).delete()

    dists_to_update = []
    for country_code in country_codes:
        values = get_values_by_country(country_code)
        dist_values = get_distribution_values(values)
        dist_values["mad_threshold"] *= THRESHOLD_FACTOR
        dists_to_update.append(Distribution(
            country_code=country_code,
            **dist_values
        ))

    db.session.bulk_save_objects(dists_to_update)
    db.session.commit()

    return dists_to_update


def get_values_by_country(country_code):
    """
    Get the value properties of Charges for `country_code`.

    This is here so that get_distribution_values() can be disconnected from
    the model and used in run.py.

    There's presumably a simpler way in SQLAlchemy for this. This and other
    similar methods could be expressed on Charge.query.
    """

    country_charges = Charge.query.filter_by(country_code=country_code).all()
    return [charge.value for charge in country_charges]


def get_distribution_values(values):
    """
    Get the distribution values for the given set of values.

    Currently this is the median and the Median Absolute Deviation (MAD).
    """

    med = np.median(values)
    return {
        "median": med,
        "mad_threshold": np.median(abs(values - med))
    }


def is_outlier(charge, distribution):
    """
    Test if `charge` has an outlier value compared to its `distribution`.

    In this implementation, `charge` is an outlier if it's beyond the
    Median Absolute Deviation for its data set, typically values for a country.
    The MAD is adjusted slightly to allow for growing the space of legal
    values.

    Arguments:
      charge       -- Charge object to test.
      distribution -- Distribution object with info about the dataset.
    """
    return abs(charge.value - distribution.median) > distribution.mad_threshold
