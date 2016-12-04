"""
Prepare the database and run the server.
"""

from os import remove, path

# Let's start fresh every time.
db_path = "/tmp/test.db"
if path.exists(db_path):
    remove(db_path)


from charge_api import app, db
from charge_api.models import Distribution
from charge_api.outliers import get_distribution_values


db.create_all()

# Bootstrap the system with initial values.
INITIAL_COUNTRY_VALUES = {
    "CN": (100.0, 182.0),
    "HK": (257.0, 282.0),
    "US": (367.0, 500.0),
}

initial_distributions = []
for country_code, values in INITIAL_COUNTRY_VALUES.iteritems():
    dist_values = get_distribution_values(values)
    initial_distributions.append(Distribution(
        country_code=country_code,
        **dist_values
    ))
db.session.bulk_save_objects(initial_distributions)
db.session.commit()


app.run(debug=True)
