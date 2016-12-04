# Application for outliers in terminal handling charges

## Overview

I read a little bit and decided to go for an approach using Median Absolute
Deviation, and some factor around it. I prime the database with the known good
ranges supplied in the assignment. Uploading data re-computes the acceptable
ranges for the next upload. It seems the method I chose doesn't align that well
with the data. A factor that's specific to each country data set might improve
on it.

The database is currently recreated on each run of the server. I decided to use
SQLlite for simplicity. The MAD calculation could and should be offloaded to
the database.

The currency data is hard-coded. It should be fairly simple to fetch and store
from an external source in an separate task.

No particular validation is done on the uploaded data. Little error handling is
done on nonexistent data for a country. I'd ideally use some sort of framework
for the first part.

I like to work with ORMs, so I tried out SQLAlchemy for the first time. It's a
bit more involved than I'm used to. It strikes me as a poor choice for working
with JSON data.

I included a set of stubs for a REST API and an example test case. I'll expand
on these if I find the time.

## Installation

Optionally install and activate a virtualenv:

    virtualenv some_path
    . some_path/bin/activate
    pip install --upgrade pip  # Necessary on my Ubuntu at least.

Install the dependencies:

    pip install -r requirements.txt

## Running

In a shell, run:

    python run.py

Open your browser and point it to:

    http://127.0.0.1:5000/

You should now see an empty list of registered charges, and an initial set of
distribution information. Choosing a file and clicking "Upload", should import
charges from the file.

Use the filters to drill down on country and validity.

## Tests

So far, only one test case is implemented as an example. Nose should find and
execute this and any others added later:

    nosetsts
