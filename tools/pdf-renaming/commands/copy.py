import click
import logging
import sys
import time
from playhouse.shortcuts import model_to_dict
from .tables import (
    Renaming,
    setup_database
    )
from .constants import *
from .s3_support import s3_copy, s3_check_exists

logger = logging.getLogger(__name__)

def timing_update(t0, limit):
    t1 = time.time()
    print({
        "delta": (t1-t0),
        "each": (t1-t0)/float(limit),
        "count": limit
    })

@click.command()
@click.argument("db_filename")
@click.option('--destination', default="local")
@click.argument("--local_temp_path", default="tmp")
@click.option('-l', '--limit', default=None)
@click.option('-y', '--year', default=2022)
@click.option("-r", "--live_run", default=False)
def copy(db_filename, 
        destination,
        local_temp_path, 
        limit, year, live_run):
    setup_database(db_filename)

    if destination not in ["preview", "production"]:
        print("Destination is not in allowed list. Existing.")
        sys.exit(-1)

    t0 = time.time()
    ticker = 0

    q = (Renaming.select()
         .where(Renaming.census_file_exists == True, 
                Renaming.year == int(year), 
                # Only copy files we have not previously attempted to copy.
                Renaming.gsa_file_copied.is_null()))

    if limit:
        print(f"Set query limit to {limit}")
        q = q.limit(int(limit))

    r: Renaming
    for r in q.iterator():
        ticker += 1
        if ticker % 100 == 0:
            timing_update(t0, ticker)

        dest_file = f"{r.gsa_path}{r.gsa_name}"
        if live_run:
            is_good = s3_copy({
                "local_temp_path": local_temp_path,
                "source_env": "census",
                "source_file": f"{r.census_path}{r.census_name}", 
                "destination_env": destination,
                "destination_file": dest_file
                },
                live_run)
            if is_good:
                r.gsa_file_copied = True
            else: 
                r.gsa_file_copied = False
            r.save()
