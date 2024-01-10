create or replace function admin_api_v1_0_0.add_tribal_api_key_access(params JSON) 
returns BOOLEAN
as $add_tribal_api_key_access$
DECLARE 
    already_exists INTEGER;
    read_tribal_id INTEGER;
BEGIN
    -- If the API user has insert permissions, give it a go
    IF admin_api_v1_0_0_functions.has_admin_data_access('CREATE')
    THEN
        -- Are they already in the table?
        SELECT count(up.email) 
            FROM public.users_userpermission as up
            WHERE email = params->>'email' INTO already_exists;

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
                VALUES (params->>'email', read_tribal_id, null);
            RETURN admin_api_v1_0_0_functions.log_admin_api_event('tribal-access-email-added', 
                                                        json_build_object('email', params->>'email'));
        END IF;
    ELSE
        RETURN 0;
    END IF;
end;
$add_tribal_api_key_access$ LANGUAGE plpgsql;

-- Adds many email addresses. Calls `add_tribal_api_key_access` for each address.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/add_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
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
CREATE OR REPLACE FUNCTION admin_api_v1_0_0.add_tribal_access_emails(params JSON) 
returns BOOLEAN
as $add_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_0_0_functions.has_admin_data_access('CREATE')
    THEN 
        -- This is a FOR loop over a JSON array in plPgSQL
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            -- PERFORM is how to execute code that does not return anything.
            -- If a SELECT was used here, the SQL compiler would complain.
            PERFORM admin_api_v1_0_0.add_tribal_api_key_access(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$add_tribal_access_emails$ LANGUAGE plpgsql;

-- Removes the email. Will remove multiple rows. That shouldn't happen, but still.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_api_key_access
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_0_0.remove_tribal_api_key_access(params JSON) 
returns BOOLEAN
as $remove_tribal_api_key_access$
DECLARE
      affected_rows INTEGER;
BEGIN

    IF admin_api_v1_0_0_functions.has_admin_data_access('DELETE')
    THEN 
        -- Delete rows where the email address matches
        DELETE FROM public.users_userpermission as up
            WHERE up.email = params->>'email';
        -- This is the Postgres way to find out how many rows
        -- were affected by a DELETE.
        GET DIAGNOSTICS affected_rows = ROW_COUNT;
        -- If that is greater than zero, we were successful.
        IF affected_rows > 0
        THEN
            RETURN admin_api_v1_0_0_functions.log_admin_api_event('tribal-access-email-removed', 
                                                        json_build_object('email', params->>'email'));
        ELSE
            RETURN 0;
        END IF;
    ELSE
        -- If we did not have permission, consider it a failure.
        RETURN 0;
    END IF;
end;
$remove_tribal_api_key_access$ LANGUAGE plpgsql;

-- Removes many email addresses. Calls `remove_tribal_api_key_access` for each address.
-- 
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
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
CREATE OR REPLACE FUNCTION admin_api_v1_0_0.remove_tribal_access_emails(params JSON) 
returns BOOLEAN
as $remove_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_0_0_functions.has_admin_data_access('DELETE')
    THEN 
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            PERFORM admin_api_v1_0_0.remove_tribal_api_key_access(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$remove_tribal_access_emails$ LANGUAGE plpgsql;

commit;

NOTIFY pgrst, 'reload schema';
