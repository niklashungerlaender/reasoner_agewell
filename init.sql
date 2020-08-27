--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 12.2

-- Started on 2020-08-27 11:39:06

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

--
-- TOC entry 196 (class 1259 OID 44754291)
-- Name: activity; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity (
    activity_id integer NOT NULL,
    user_id text NOT NULL,
    goal_id smallint NOT NULL,
    type_id smallint NOT NULL
);


ALTER TABLE public.activity OWNER TO postgres;

--
-- TOC entry 195 (class 1259 OID 44754289)
-- Name: activity_activity_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_activity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activity_activity_id_seq OWNER TO postgres;

--
-- TOC entry 2212 (class 0 OID 0)
-- Dependencies: 195
-- Name: activity_activity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_activity_id_seq OWNED BY public.activity.activity_id;


--
-- TOC entry 192 (class 1259 OID 44754262)
-- Name: activity_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_type (
    type_id integer NOT NULL,
    activity_name character varying(255) NOT NULL,
    met_value smallint NOT NULL,
    duration integer[],
    url text
);


ALTER TABLE public.activity_type OWNER TO postgres;

--
-- TOC entry 191 (class 1259 OID 44754260)
-- Name: activity_type_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_type_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activity_type_type_id_seq OWNER TO postgres;

--
-- TOC entry 2213 (class 0 OID 0)
-- Dependencies: 191
-- Name: activity_type_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_type_type_id_seq OWNED BY public.activity_type.type_id;


--
-- TOC entry 199 (class 1259 OID 44754342)
-- Name: apscheduler_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.apscheduler_jobs (
    id character varying(191) NOT NULL,
    next_run_time double precision,
    job_state bytea NOT NULL
);


ALTER TABLE public.apscheduler_jobs OWNER TO postgres;

--
-- TOC entry 194 (class 1259 OID 44754275)
-- Name: goal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.goal (
    goal_id integer NOT NULL,
    user_id text NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    met_required smallint,
    achieved smallint
);


ALTER TABLE public.goal OWNER TO postgres;

--
-- TOC entry 193 (class 1259 OID 44754273)
-- Name: goal_goal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.goal_goal_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.goal_goal_id_seq OWNER TO postgres;

--
-- TOC entry 2214 (class 0 OID 0)
-- Dependencies: 193
-- Name: goal_goal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.goal_goal_id_seq OWNED BY public.goal.goal_id;


--
-- TOC entry 190 (class 1259 OID 44754241)
-- Name: message; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message (
    template_id integer NOT NULL,
    notification_id text NOT NULL
);


ALTER TABLE public.message OWNER TO postgres;

--
-- TOC entry 189 (class 1259 OID 44754239)
-- Name: message_template_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.message_template_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.message_template_id_seq OWNER TO postgres;

--
-- TOC entry 2215 (class 0 OID 0)
-- Dependencies: 189
-- Name: message_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.message_template_id_seq OWNED BY public.message.template_id;


--
-- TOC entry 188 (class 1259 OID 44754226)
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification (
    notification_id text NOT NULL,
    user_id text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    rating smallint
);


ALTER TABLE public.notification OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 44754319)
-- Name: task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task (
    task_id integer NOT NULL,
    activity_id smallint,
    feedback character varying(255),
    duration smallint,
    start_daytime timestamp without time zone,
    activity_done boolean,
    active boolean
);


ALTER TABLE public.task OWNER TO postgres;

--
-- TOC entry 197 (class 1259 OID 44754317)
-- Name: task_task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_task_id_seq OWNER TO postgres;

--
-- TOC entry 2216 (class 0 OID 0)
-- Dependencies: 197
-- Name: task_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_task_id_seq OWNED BY public.task.task_id;


--
-- TOC entry 187 (class 1259 OID 44754217)
-- Name: template; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template (
    template_id integer NOT NULL,
    contenten text NOT NULL,
    contentde text,
    contentit text,
    contentnl text,
    pam text,
    mpam smallint,
    weekly text,
    daily text,
    difficulty text,
    purpose text,
    activity text,
    category text
);


ALTER TABLE public.template OWNER TO postgres;

--
-- TOC entry 186 (class 1259 OID 44754215)
-- Name: template_template_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.template_template_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.template_template_id_seq OWNER TO postgres;

--
-- TOC entry 2217 (class 0 OID 0)
-- Dependencies: 186
-- Name: template_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.template_template_id_seq OWNED BY public.template.template_id;


--
-- TOC entry 185 (class 1259 OID 44754207)
-- Name: user_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_info (
    user_id text NOT NULL,
    age smallint,
    value_mpam integer[],
    value_ipaq smallint,
    morning_reminder_id smallint,
    evening_reminder_id smallint,
    gender character varying(255),
    firebaseinstanceid character varying(255),
    useridoauth character varying(255),
    nickname character varying(255),
    language character varying(255),
    mqttuser character varying(255)
);


ALTER TABLE public.user_info OWNER TO postgres;

--
-- TOC entry 2055 (class 2604 OID 44754294)
-- Name: activity activity_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity ALTER COLUMN activity_id SET DEFAULT nextval('public.activity_activity_id_seq'::regclass);


--
-- TOC entry 2053 (class 2604 OID 44754265)
-- Name: activity_type type_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_type ALTER COLUMN type_id SET DEFAULT nextval('public.activity_type_type_id_seq'::regclass);


--
-- TOC entry 2054 (class 2604 OID 44754278)
-- Name: goal goal_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal ALTER COLUMN goal_id SET DEFAULT nextval('public.goal_goal_id_seq'::regclass);


--
-- TOC entry 2052 (class 2604 OID 44754244)
-- Name: message template_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message ALTER COLUMN template_id SET DEFAULT nextval('public.message_template_id_seq'::regclass);


--
-- TOC entry 2056 (class 2604 OID 44754322)
-- Name: task task_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task ALTER COLUMN task_id SET DEFAULT nextval('public.task_task_id_seq'::regclass);


--
-- TOC entry 2051 (class 2604 OID 44754220)
-- Name: template template_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template ALTER COLUMN template_id SET DEFAULT nextval('public.template_template_id_seq'::regclass);


--
-- TOC entry 2072 (class 2606 OID 44754301)
-- Name: activity activity_goal_id_user_id_type_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_goal_id_user_id_type_id_key UNIQUE (goal_id, user_id, type_id);


--
-- TOC entry 2074 (class 2606 OID 44754299)
-- Name: activity activity_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (activity_id);


--
-- TOC entry 2066 (class 2606 OID 44754272)
-- Name: activity_type activity_type_activity_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_type
    ADD CONSTRAINT activity_type_activity_name_key UNIQUE (activity_name);


--
-- TOC entry 2068 (class 2606 OID 44754270)
-- Name: activity_type activity_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_type
    ADD CONSTRAINT activity_type_pkey PRIMARY KEY (type_id);


--
-- TOC entry 2080 (class 2606 OID 44754349)
-- Name: apscheduler_jobs apscheduler_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apscheduler_jobs
    ADD CONSTRAINT apscheduler_jobs_pkey PRIMARY KEY (id);


--
-- TOC entry 2070 (class 2606 OID 44754283)
-- Name: goal goal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal
    ADD CONSTRAINT goal_pkey PRIMARY KEY (goal_id);


--
-- TOC entry 2064 (class 2606 OID 44754249)
-- Name: message message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_pkey PRIMARY KEY (template_id, notification_id);


--
-- TOC entry 2062 (class 2606 OID 44754233)
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (notification_id);


--
-- TOC entry 2076 (class 2606 OID 44754326)
-- Name: task task_activity_id_start_daytime_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_activity_id_start_daytime_key UNIQUE (activity_id, start_daytime);


--
-- TOC entry 2078 (class 2606 OID 44754324)
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (task_id);


--
-- TOC entry 2060 (class 2606 OID 44754225)
-- Name: template template_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template
    ADD CONSTRAINT template_pkey PRIMARY KEY (template_id);


--
-- TOC entry 2058 (class 2606 OID 44754214)
-- Name: user_info user_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_info
    ADD CONSTRAINT user_info_pkey PRIMARY KEY (user_id);


--
-- TOC entry 2081 (class 1259 OID 44754350)
-- Name: ix_apscheduler_jobs_next_run_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_apscheduler_jobs_next_run_time ON public.apscheduler_jobs USING btree (next_run_time);


--
-- TOC entry 2088 (class 2606 OID 44754312)
-- Name: activity activity_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goal(goal_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2086 (class 2606 OID 44754302)
-- Name: activity activity_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.activity_type(type_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2087 (class 2606 OID 44754307)
-- Name: activity activity_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_info(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2085 (class 2606 OID 44754284)
-- Name: goal goal_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.goal
    ADD CONSTRAINT goal_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_info(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2084 (class 2606 OID 44754255)
-- Name: message message_notification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_notification_id_fkey FOREIGN KEY (notification_id) REFERENCES public.notification(notification_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2083 (class 2606 OID 44754250)
-- Name: message message_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.template(template_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2082 (class 2606 OID 44754234)
-- Name: notification notification_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_info(user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2089 (class 2606 OID 44754327)
-- Name: task task_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activity(activity_id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2020-08-27 11:39:06

--
-- PostgreSQL database dump complete
--

