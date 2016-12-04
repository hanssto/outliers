from flask import request, json, render_template, redirect

from . import app
from . import db
from .charges import process_charge_list
from .models import Charge, Distribution


CHARGES_FILENAME = "charges_file"  # TODO Move to setting.


@app.route("/upload", methods=["POST"])
def upload():
    """
    Receives a file of charge data, validates and stores it.

    Could be made to accept a zip file, if the JSON files are big.
    """

    charges_file = request.files.get(CHARGES_FILENAME)

    if not charges_file:
        return "No '%s' passed." % CHARGES_FILENAME, 400,

    try:
        charge_list = json.load(charges_file)
    except ValueError:
        return "Invalid JSON data.", 400,

    charges, errors = process_charge_list(charge_list)

    if errors and not charges:
        return "errors", 400,  # TODO

    return redirect("/")


@app.route("/", methods=["GET"])
def charges():
    """
    Lists charges registered in the system.

    Parameters:
    country_code -- Limits the returned charges to those for `country_code`.
    valid        -- Limits the returned charges by whether they are valid.
                    Legal values: "yes" (only valid), "no" (only invalid).
    """

    valid_choices = (
        (None, "Either"),
        ("no", "Invalid"),
        ("yes", "Valid"),
    )

    # Obviously we'd validate the args properly.
    # I hear WTForms isn't popular in your backyard, so I'm curious how you do
    # this.
    country_code = request.args.get("country_code")
    valid = request.args.get("valid")

    countries = db.session.query(
        Charge.country_code.distinct().label("country_code")
    ).order_by("country_code").all()
    charges = Charge.query.order_by("country_code", "value")

    distributions = Distribution.query

    if country_code:
        charges = charges.filter_by(country_code=country_code)
        distributions = distributions.filter_by(country_code=country_code)

    if valid:
        charges = charges.filter_by(valid=valid == "yes")

    return render_template(
        "charges.html",
        countries=countries,
        country_code=country_code,
        valid_choices=valid_choices,
        valid=valid,
        distributions=distributions.all(),
        charges=charges.all(),
    )


# Stubs for REST API views, for use with a client-side application.

@app.route("/api/1.0/charges", methods=["GET", "POST"])
def api_charges():
    """
    List or create charges in the system.

    Methods:
    GET  -- Lists the charges in the system.
    POST -- Creates a new set of charges in the system.

    Parameters (GET):
    country_code -- Limits the returned charges to those for `country_code`.
    valid        -- Limits the returned charges by whether they are valid.
                    Legal values: "yes" (only valid), "no" (only invalid).

    Format:
    A list of objects, each with the following properties:
    * charge_id (GET only) - ...
    * port (POST only) - ...
    * country_code (GET only) - ...
    * city_code  (GET only)- ...
    * supplier_id - ...
    * currency - ...
    * value - ...
    """
    pass


@app.route("/api/1.0/countries", methods=["GET"])
def api_countries():
    pass


@app.route("/api/1.0/charges/<int:charge_id>", methods=["GET", "PATCH"])
def api_charge(charge_id):
    pass


@app.route("/api/1.0/distributions", methods=["GET"])
def api_distributions():
    pass


@app.route("/api/1.0/distributions/country/<string:country_code>",
           methods=["GET", "PUT"])
def api_distribution(country_code):
    pass


def to_dicts(model, query_result):
    columns = [column.name for column in model.__table__columns]
    return [
        {column: getattr(obj, column) for column in columns}
        for obj in query_result
    ]
