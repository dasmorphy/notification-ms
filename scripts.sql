
----------------------------------------------------------------------------------------------------------------------

-- Table: public.notifications

-- DROP TABLE IF EXISTS public.notifications;

CREATE TABLE IF NOT EXISTS public.notifications
(
    id_notification uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    fcm_message_id text COLLATE pg_catalog."default",
    fcm_token text COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default" NOT NULL,
    body text COLLATE pg_catalog."default" DEFAULT ''::text,
    img_url text COLLATE pg_catalog."default",
    notification_type text COLLATE pg_catalog."default",
    data jsonb DEFAULT '{}'::jsonb,
    status text DEFAULT 'pending',
    error text,
    is_read boolean NOT NULL DEFAULT false,
    is_deleted boolean NOT NULL DEFAULT false,
    sent_at timestamp without time zone DEFAULT now(),
    read_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT notifications_pkey PRIMARY KEY (id_notification),
    CONSTRAINT notifications_fcm_message_id_key UNIQUE (fcm_message_id),
    CONSTRAINT notification_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id_user) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.notifications
    OWNER to nextgen;

-- DROP INDEX IF EXISTS public.fki_notification_user_id_fkey;

CREATE INDEX IF NOT EXISTS fki_notification_user_id_fkey
    ON public.notifications USING btree
    (user_id ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_notifications_user_feed

-- DROP INDEX IF EXISTS public.idx_notifications_user_feed;

CREATE INDEX IF NOT EXISTS idx_notifications_user_feed
    ON public.notifications USING btree
    (user_id ASC NULLS LAST, sent_at DESC NULLS FIRST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default
    WHERE is_deleted = false;

-----------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE public.fcm_token_users
(
    id_fcm_token integer NOT NULL,
    user_id uuid NOT NULL,
    project_id integer NOT NULL,
    fcm_token text NOT NULL,
    platform text NOT NULL,
    is_active boolean NOT NULL DEFAULT True,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT fcm_token_pkey PRIMARY KEY (id_fcm_token),
    CONSTRAINT fcm_token_user_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id_user) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fcm_token_project_fkey FOREIGN KEY (project_id)
        REFERENCES public.firebase_projects (id_project) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.fcm_token_users
    OWNER to nextgen;


CREATE SEQUENCE public.fcm_token_users_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.fcm_token_users_id_seq
    OWNED BY public.fcm_token_users.id_fcm_token;

ALTER SEQUENCE public.fcm_token_users_id_seq
    OWNER TO nextgen;

ALTER TABLE IF EXISTS public.fcm_token_users
    ALTER COLUMN id_fcm_token SET DEFAULT nextval('fcm_token_users_id_seq'::regclass);


------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.firebase_projects

-- DROP TABLE IF EXISTS public.firebase_projects;

CREATE TABLE IF NOT EXISTS public.firebase_projects
(
    id_project integer NOT NULL,
    name text COLLATE pg_catalog."default",
    service_account_path text COLLATE pg_catalog."default",
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    created_by text COLLATE pg_catalog."default",
    CONSTRAINT firebase_projects_pkey PRIMARY KEY (id_project)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.firebase_projects
    OWNER to nextgen;


CREATE SEQUENCE public.firebase_projects_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.firebase_projects_id_seq
    OWNED BY public.firebase_projects.id_project;

ALTER SEQUENCE public.firebase_projects_id_seq
    OWNER TO nextgen;

ALTER TABLE IF EXISTS public.firebase_projects
    ALTER COLUMN id_project SET DEFAULT nextval('firebase_projects_id_seq'::regclass);


----------------------------------------------------------------------------------------------------------

ALTER TABLE IF EXISTS public.fcm_token_users DROP COLUMN IF EXISTS token_session;

ALTER TABLE IF EXISTS public.fcm_token_users
    ADD COLUMN session_id integer;
ALTER TABLE IF EXISTS public.fcm_token_users
    ADD CONSTRAINT fcm_token_session_id FOREIGN KEY (session_id)
    REFERENCES public.user_sessions (id_session) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS fki_fcm_token_session_id
    ON public.fcm_token_users(session_id);