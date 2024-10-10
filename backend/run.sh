#!/bin/bash

# Source everything; everything is now a function.
# Remember: bash has no idea if a function exists, 
# so a typo in a function name will fail silently. Similarly,
# bash has horrible scoping, so use of `local` in functions is 
# critical for cleanliness in the startup script.
source tools/util_startup.sh
# This will choose the correct environment
# for local envs (LOCAL or TESTING) and cloud.gov
source tools/setup_env.sh
source tools/sql_pre_post.sh
source tools/migrate_app_tables.sh
source tools/sling_first_run.sh
source tools/build_indexes.sh
source tools/seed_cog_baseline.sh

#####
# SETUP THE LOCAL ENVIRONMENT
setup_env
gonogo "setup_env"

#####
# SQL PRE
# We have SQL that we want to run before the migrations and sling are run.
# This tears down things that would conflict with migrations, etc.
sql_pre
gonogo "sql_pre"

#####
# MIGRATE APP TABLES
# migrate_app_tables
gonogo "migrate_app_tables"

#####
# PREP API TABLES
# This runs sling and preps tables in the snapshot DB.
# Only runs if the tables are not present (e.g. first deploy)
sling_first_run
gonogo "sling_first_run"

#####
# SQL POST
# Rebuild the API and prepare the system for execution.
# Runs after migrations.
sql_post
gonogo "sql_post"

#####
# SEED COG/OVER TABLES
# Setup tables for cog/over assignments
seed_cog_baseline
gonogo "seed_cog_baseline"

#####
# LAUNCH THE APP
# We will have died long ago if things didn't work.
npm run dev & python manage.py runserver 0.0.0.0:8000
