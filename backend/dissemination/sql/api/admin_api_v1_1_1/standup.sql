DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'authenticator') THEN
      RAISE NOTICE 'Role "authenticator" already exists. Skipping.';
   ELSE
      CREATE ROLE authenticator LOGIN NOINHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'api_fac_gov') THEN
      RAISE NOTICE 'Role "api_fac_gov" already exists. Skipping.';
   ELSE
      CREATE ROLE api_fac_gov NOLOGIN;
   END IF;
END
$do$;

GRANT api_fac_gov TO authenticator;

NOTIFY pgrst, 'reload schema';
begin;

do
$$
begin
    DROP SCHEMA IF EXISTS admin_api_v1_1_1 CASCADE;
    DROP SCHEMA IF EXISTS admin_api_v1_1_1_functions CASCADE;

    if not exists (select schema_name from information_schema.schemata where schema_name = 'admin_api_v1_1_1') then
        create schema admin_api_v1_1_1;
        create schema admin_api_v1_1_1_functions;

        grant usage on schema admin_api_v1_1_1_functions to api_fac_gov;

        -- Grant access to tables and views
        alter default privileges
            in schema admin_api_v1_1_1
            grant select
        -- this includes views
        on tables
        to api_fac_gov;
                
        -- Grant access to sequences, if we have them
        grant usage on schema admin_api_v1_1_1 to api_fac_gov;
        grant select, usage on all sequences in schema admin_api_v1_1_1 to api_fac_gov;
        alter default privileges
            in schema admin_api_v1_1_1
            grant select, usage
        on sequences
        to api_fac_gov;

        -- The admin API needs to be able to write user permissions.
        -- This is so we can add and remove people who will have tribal data access
        -- via the administrative API.
        GRANT INSERT, SELECT, DELETE on public.users_userpermission to api_fac_gov;
        -- We need to be able to look up slugs and turn them into permission IDs.
        GRANT SELECT on public.users_permission to api_fac_gov;
        -- It also needs to be able to log events.
        GRANT INSERT on public.support_adminapievent to api_fac_gov;
        -- And, it wants to read the UUIDs of administrative keys
        GRANT SELECT ON public.support_administrative_key_uuids TO api_fac_gov;
        -- We want to see data in flight as admins.
        GRANT SELECT ON public.audit_singleauditchecklist TO api_fac_gov;

        GRANT INSERT, SELECT, DELETE on public.dissemination_tribalapiaccesskeyids to api_fac_gov;
        GRANT INSERT on public.dissemination_onetimeaccess to api_fac_gov;
    end if;
end
$$
;

commit;

notify pgrst,
       'reload schema';

begin;


CREATE OR REPLACE FUNCTION admin_api_v1_1_1_functions.get_header(item text) RETURNS text
    AS $get_header$
    declare res text;
   	begin
    	SELECT (current_setting('request.headers', true)::json)->>item into res;
    	return res;
   end;
$get_header$ LANGUAGE plpgsql;

create or replace function admin_api_v1_1_1_functions.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select admin_api_v1_1_1_functions.get_header('x-api-user-id') into uuid;
	return uuid;
end;
$gaku$ LANGUAGE plpgsql;

-- log_api_event
-- Maintain an internal table of administrative API events.
-- Also RAISE INFO so that NR gets a copy.
create or replace function admin_api_v1_1_1_functions.log_admin_api_event(event TEXT, meta JSON)
returns boolean
as $log_admin_api_event$
DECLARE
    uuid_header text;
BEGIN
    SELECT admin_api_v1_1_1_functions.get_api_key_uuid() INTO uuid_header;

    INSERT INTO public.support_adminapievent 
        (api_key_uuid, event, event_data, "timestamp")
        VALUES (uuid_header, event, meta, NOW());

    RAISE INFO 'ADMIN_API % % %', uuid_header, event, meta; 
    RETURN 1;
END;
$log_admin_api_event$ LANGUAGE plpgsql;


-- has_admin_data_access :: permission -> bool
-- The permissions (insert, select, delete) allow us to have users who can
-- read administrative data in addition to users who can (say) update
-- select tables like the tribal access lists.
create or replace function admin_api_v1_1_1_functions.has_admin_data_access(perm TEXT) returns boolean
as $has_admin_data_access$
DECLARE 
    uuid_header text;
    key_exists boolean;
    has_permission boolean;
BEGIN
    SELECT admin_api_v1_1_1_functions.get_api_key_uuid() INTO uuid_header;

    SELECT 
        CASE WHEN EXISTS (
            SELECT uuid 
            FROM public.support_administrative_key_uuids aku
            WHERE aku.uuid = uuid_header)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;

    SELECT 
        CASE WHEN EXISTS (
            SELECT permissions
            FROM public.support_administrative_key_uuids aku 
            WHERE aku.uuid = uuid_header
            AND aku.permissions like '%' || perm || '%')
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO has_permission;
    
    -- This log event is an INSERT. When called from a VIEW (a SELECT-only context),
    -- a call to log_admin_api_event() fails. So, we'll RAISE INFO right here, so we can
    -- see the resultse of access checks in the log. We might later comment this out if 
    -- it becomes too noisy.
    RAISE INFO 'ADMIN_API has_access_check % % %', uuid_header, key_exists, has_permission;

    RETURN key_exists AND has_permission;
END;
$has_admin_data_access$ LANGUAGE plpgsql;

-- Takes an email address and, if that address is not in the access table,
-- inserts it. If the address already exists, the insert is skipped.
-- 
-- ### Example from REST client
-- POST http://localhost:3000/rpc/add_tribal_access_email
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_1_1
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
create or replace function admin_api_v1_1_1.add_tribal_access_email(params JSON) 
returns BOOLEAN
as $add_tribal_access_email$
DECLARE 
    already_exists INTEGER;
    read_tribal_id INTEGER;
BEGIN
    -- If the API user has insert permissions, give it a go
    IF admin_api_v1_1_1_functions.has_admin_data_access('CREATE')
    THEN
        -- Are they already in the table?
        SELECT count(up.email) 
            FROM public.users_userpermission as up
            WHERE LOWER(email) = LOWER(params->>'email') INTO already_exists;

        -- If they are, we're going to exit.
        IF already_exists <> 0
        THEN
            RETURN 0;
        END IF;

        -- Grab the permission ID that we need for the insert below.
        -- We want the 'read-tribal' permission, which has a human-readable
        -- slug. But, we need it's ID, because that is the PK.
        SELECT up.id INTO read_tribal_id 
            FROM public.users_permission AS up
            WHERE up.slug = 'read-tribal';

        IF already_exists = 0 
        THEN
            -- Can we make the 1 not magic... do a select into.
            INSERT INTO public.users_userpermission
                (email, permission_id, user_id)
                VALUES (LOWER(params->>'email'), read_tribal_id, null);

            RAISE INFO 'ADMIN_API add_tribal_access_email OK %', LOWER(params->>'email');
            RETURN admin_api_v1_1_1_functions.log_admin_api_event('tribal-access-email-added', 
                                                        json_build_object('email', LOWER(params->>'email')));
        END IF;
    ELSE
        RETURN 0;
    END IF;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;

-- Adds many email addresses. Calls `add_tribal_access_email` for each address.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/add_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_1_1
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "emails": [
--         "darth.vader@deathstar.org",
--         "bob.darth.vader@deathstar.org",
--         "darthy.vader@deathstar.org",
--         "bob@deathstar.org"
--     ]
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_1_1.add_tribal_access_emails(params JSON) 
returns BOOLEAN
as $add_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_1_1_functions.has_admin_data_access('CREATE')
    THEN 
        -- This is a FOR loop over a JSON array in plPgSQL
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            -- PERFORM is how to execute code that does not return anything.
            -- If a SELECT was used here, the SQL compiler would complain.
            PERFORM admin_api_v1_1_1.add_tribal_access_email(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$add_tribal_access_emails$ LANGUAGE plpgsql;

-- Removes the email. Will remove multiple rows. That shouldn't happen, but still.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_access_email
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_1_1
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_1_1.remove_tribal_access_email(params JSON) 
returns BOOLEAN
as $remove_tribal_access_email$
DECLARE
      affected_rows INTEGER;
BEGIN

    IF admin_api_v1_1_1_functions.has_admin_data_access('DELETE')
    THEN 
        -- Delete rows where the email address matches
        DELETE FROM public.users_userpermission as up
            WHERE LOWER(up.email) = LOWER(params->>'email');
        -- This is the Postgres way to find out how many rows
        -- were affected by a DELETE.
        GET DIAGNOSTICS affected_rows = ROW_COUNT;
        -- If that is greater than zero, we were successful.
        IF affected_rows > 0
        THEN
            RETURN admin_api_v1_1_1_functions.log_admin_api_event('tribal-access-email-removed', 
                                                        json_build_object('email', LOWER(params->>'email')));
        ELSE
            RETURN 0;
        END IF;
    ELSE
        -- If we did not have permission, consider it a failure.
        RETURN 0;
    END IF;
end;
$remove_tribal_access_email$ LANGUAGE plpgsql;

-- Removes many email addresses. Calls `remove_tribal_access_email` for each address.
-- 
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_1_1
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "emails": [
--         "darth.vader@deathstar.org",
--         "bob.darth.vader@deathstar.org",
--         "darthy.vader@deathstar.org",
--         "bob@deathstar.org"
--     ]
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_1_1.remove_tribal_access_emails(params JSON) 
returns BOOLEAN
as $remove_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_1_1_functions.has_admin_data_access('DELETE')
    THEN 
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            PERFORM admin_api_v1_1_1.remove_tribal_access_email(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$remove_tribal_access_emails$ LANGUAGE plpgsql;




--The function below add_tribal_api_key_access adds read access to a tribal API for a specified email.
--It checks if the API user has read permissions.
--Otherwise, it adds the email with 'read-tribal' permission, logs the event, and returns true.

CREATE OR REPLACE FUNCTION admin_api_v1_1_1.add_tribal_api_key_access(params JSON) 
RETURNS JSON
AS $add_tribal_api_key_access$
DECLARE 
    user_exists BOOLEAN;
BEGIN
    -- If the API user has create permissions, we can proceed
    IF admin_api_v1_1_1_functions.has_admin_data_access('CREATE') THEN
    -- Check if the user with the given email
        SELECT EXISTS (
            SELECT 1 
            FROM public.dissemination_TribalApiAccessKeyIds
            WHERE LOWER(email) = LOWER(params->>'email')
        )
        INTO user_exists;

        -- If the user already exists, it means they have access.
        -- For purposes of this function, lets call that "succses", and return true.
        IF user_exists THEN
            RAISE INFO 'ADMIN_API add_tribal_api_key_access ALREADY_EXISTS %', LOWER(params->>'email');
            RETURN json_build_object(
                'result', 'success',
                'message', 'User with this key already exists')::JSON;

        END IF;

        -- If the user does not exist, add a new record
        INSERT INTO public.dissemination_TribalApiAccessKeyIds (email, key_id, date_added)
        VALUES (LOWER(params->>'email'), params->>'key_id', CURRENT_TIMESTAMP);
        RAISE INFO 'ADMIN_API add_tribal_api_key_access ACCESS_GRANTED % %', LOWER(params->>'email'), params->>'key_id';
        RETURN json_build_object(
            'result', 'success', 
            'message', 'User access granted')::JSON;
    ELSE
        -- If the user does not have CREATE permissions, then we should return a message to that effect. 
        -- It is a permissions error, but still, we need to know this failed.
        RAISE INFO 'ADMIN_API add_tribal_api_key_access ADMIN_LACKS_CREATE';
        RETURN json_build_object(
            'result', 'failure', 
            'message', 'Admin user lacks CREATE permissions')::JSON;
    END IF;

    -- Return false by default.
    RAISE INFO 'ADMIN_API add_tribal_api_key_access WAT %', LOWER(params->>'email');
    RETURN json_build_object(
        'result', 'failure', 
        'message', 'Unknown error in access addition')::JSON;
END;
$add_tribal_api_key_access$ LANGUAGE plpgsql;

-- The function below removes tribal API key access for a specified email.
-- It checks if the API user has read permissions.
-- If the email exists in the database with 'read-tribal' permission, it removes the entry, logs the removal event, and returns true.
-- If the email doesn't exist or the user lacks proper permissions, the function returns false.

CREATE OR REPLACE FUNCTION admin_api_v1_1_1.remove_tribal_api_key_access(params JSON) 
RETURNS JSON
AS $remove_tribal_api_key_access$
DECLARE 
    user_exists BOOLEAN;
BEGIN
    -- If the API user has read permissions, give it a go
    IF admin_api_v1_1_1_functions.has_admin_data_access('DELETE') THEN
        -- Check if the user with the given email exists
        SELECT EXISTS (
            SELECT 1 
            FROM public.dissemination_TribalApiAccessKeyIds
            WHERE LOWER(email) = LOWER(params->>'email')
        )
        INTO user_exists;

        -- If the user exists, remove the record
        IF user_exists THEN
            DELETE FROM public.dissemination_TribalApiAccessKeyIds
            WHERE LOWER(email) = LOWER(params->>'email');
            RAISE INFO 'ADMIN_API remove_tribal_api_key_access ACCESS_REMOVED %', LOWER(params->>'email');
            RETURN json_build_object(
                'result', 'success', 
                'message', 'Removed record')::JSON; 
        ELSE
            RAISE INFO 'ADMIN_API remove_tribal_api_key_access DID_NOT_EXIST %', LOWER(params->>'email');
            RETURN json_build_object(
                'result', 'failure', 
                'message', 'User did not exist in table')::JSON;
        END IF;
    ELSE
        RAISE INFO 'ADMIN_API remove_tribal_api_key_access ADMIN_LACKS_DELETE';
        RETURN json_build_object(
            'result', 'failure', 
            'message', 'Admin user lacks DELETE permissions')::JSON; -- Return false if the API user doesn't have read permissions
    END IF;
    RAISE INFO 'ADMIN_API add_tribal_api_key_access WAT %', LOWER(params->>'email');
    RETURN json_build_object(
        'result', 'failure', 
        'message', 'Uknown error in access removal')::JSON;
END;
$remove_tribal_api_key_access$ LANGUAGE plpgsql;


commit;

NOTIFY pgrst, 'reload schema';

begin;


---------------------------------------
-- accesses
---------------------------------------
-- public.audit_access definition

-- Drop table

-- DROP TABLE public.audit_access;

CREATE OR REPLACE VIEW admin_api_v1_1_1.tribal_access AS
    SELECT
        uup.email,
        up.slug as permission
    FROM
        users_userpermission uup,
        users_permission up
    WHERE
        (uup.permission_id = up.id)
        AND (up.slug = 'read-tribal')
        AND admin_api_v1_1_1_functions.has_admin_data_access('READ')
    ORDER BY uup.id
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.admin_api_events AS
    SELECT
        ae.timestamp,
        ae.api_key_uuid,
        ae.event,
        ae.event_data
    FROM
        public.support_adminapievent ae
    WHERE
        admin_api_v1_1_1_functions.has_admin_data_access('READ')
    ORDER BY ae.id
;

-----------------
-- Expose more of the internal tables for analysis/trouble-shooting.
-----------------
CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_access AS
    SELECT * FROM public.audit_access
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_deletedaccess AS
    SELECT * FROM public.audit_deletedaccess
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_excelfile AS
    SELECT * FROM public.audit_excelfile
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.singleauditchecklist AS
    SELECT *
    FROM public.audit_singleauditchecklist sac
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_sacvalidationwaiver AS
    SELECT * FROM public.audit_sacvalidationwaiver
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_singleauditreportfile AS
    SELECT * FROM public.audit_singleauditreportfile
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_submissionevent AS
    SELECT * FROM public.audit_submissionevent
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.auth_user AS
    SELECT * FROM public.auth_user
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.django_migrations AS
    SELECT * FROM public.django_migrations
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.support_adminapievent AS
    SELECT * FROM public.support_adminapievent
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.support_cognizantassignment AS
    SELECT * FROM public.support_cognizantassignment
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.support_cognizantbaseline AS
    SELECT * FROM public.support_cognizantbaseline
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.users_userpermission AS
    SELECT * FROM public.users_userpermission
    WHERE admin_api_v1_1_1_functions.has_admin_data_access('READ')
;

commit;

notify pgrst,
       'reload schema';
