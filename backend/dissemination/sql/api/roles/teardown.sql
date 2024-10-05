------------------------------------------------------------------
-- authenticator role
------------------------------------------------------------------
DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'authenticator') THEN
      RAISE NOTICE 'ROLES Role "authenticator" already exists. Skipping.';
   ELSE
      CREATE ROLE authenticator LOGIN NOINHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER;
   END IF;
END
$do$;

------------------------------------------------------------------
-- api_fac_gov role
------------------------------------------------------------------
DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'api_fac_gov') THEN
      RAISE NOTICE 'ROLES Role "api_fac_gov" already exists. Skipping.';
   ELSE
      CREATE ROLE api_fac_gov NOLOGIN;
   END IF;
END
$do$;

GRANT api_fac_gov TO authenticator;

NOTIFY pgrst, 'reload schema';

