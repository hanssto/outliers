from . import db
from .models import Charge
from .outliers import mark_outliers, update_distributions


# We'd fetch these periodically and store them in some cache.
# This depends a bit on what how often we receive charge data, and how long ago
# they were valid for.
CURRENCIES = {
    'AED': 0.272261,
    'BRL': 0.287763,
    'CAD': 0.752276,
    "CNY": 0.145706,
    'GBP': 1.2734,
    "EUR": 1.0665,
    "HKD": 0.128939,
    'KRW': 0.000857,
    'SGD': 0.704474,
    "USD": 1,
}


def process_charge_list(charge_list):
    """
    Validate, convert and store data in `charge_list` as Charge objects.

    The list is typically loaded from a JSON source.

    Arguments:
      charge_list -- list of dictionaries, each with data for a charge.

    Returns: A tuple with a list of created Charge objects and a list of errors
             in the data.
    """

    charges = []
    errors = []

    countries_seen = set([])

    for charge_data in charge_list:
        # TODO validate charge_data
        port = charge_data.get("port")
        currency = charge_data.get("currency")
        # Normalize immediately for simplicity. Obviously, we should keep
        # original data for future reference or re-calculation.
        value = charge_data["value"] * CURRENCIES[currency]
        charge_data.update({
            "country_code": port[0:2],
            "city_code": port[2:],
            "value": value,
            "valid": None,
        })
        del charge_data["port"]
        charges.append(Charge(**charge_data))
        countries_seen.add(charge_data["country_code"])

    db.session.bulk_save_objects(charges, return_defaults=True)
    db.session.commit()

    # Assuming the outlier calculation is slow or the data set is big, or it
    # takes a while before a human looks as the results data.
    # This should be spun off as an asynchronous task, or done as some sort
    # of map/reduce.
    mark_outliers(charges)

    # Allow the system to learn from the incomming data.
    # This could be done periodically or on dermand, especially if a human
    # should intervene to accept/reject (some) outliers.
    update_distributions(countries_seen)

    return charges, errors
