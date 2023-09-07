CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 
-- Drop if exist
-- 
DROP TABLE IF EXISTS templates;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS t_category;
-- DROP TABLE IF EXISTS ;


-- 
-- Declare function for autoupdate in `updated` column
-- 
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


create table templates (
    id uuid DEFAULT uuid_generate_v4 (),
    name varchar(100),
    description varchar(500),
    category integer,
    template json NOT NULL,
    created TIMESTAMP DEFAULT NOW(),
    updated TIMESTAMP DEFAULT NOW(),
    template_user uuid,
    PRIMARY KEY (id)
);

create table schemas (
    id uuid DEFAULT uuid_generate_v4 (),
    name varchar(100),
    description varchar(500),
    category integer,
    schema json NOT NULL,
    created TIMESTAMP DEFAULT NOW(),
    updated TIMESTAMP DEFAULT NOW(),
    schema_user uuid,
    template uuid NOT NULL,
    PRIMARY KEY (id)
);

-- 
-- Trigger on update on `templates` table
-- 
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON templates
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


create table t_categories (
    id SERIAL NOT NULL,
    name VARCHAR(50),
    description VARCHAR(500),
    PRIMARY KEY (id)
);

create table users (
    id uuid DEFAULT uuid_generate_v4 (),
    created TIMESTAMP DEFAULT NOW(),
    updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id)
);

ALTER TABLE ONLY schemas 
ADD CONSTRAINT fk_schemas_templates FOREIGN KEY (template) REFERENCES templates;

-- ALTER TABLE ONLY templates 
-- ADD CONSTRAINT fk_templates_users FOREIGN KEY (template_user) REFERENCES users;
