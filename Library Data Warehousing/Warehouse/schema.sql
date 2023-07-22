/* no checks required in the data warehouse since
all data integrity is validated during creation
of the original database */

/* the following two tables are optimized for querying
by eliminating the need for joining multiple tables
(in contrast to traditional normalized databases) */
CREATE TABLE books (
    isbn            TEXT            PRIMARY KEY,
    title           TEXT,
    edition         NUMERIC,
    descr           TEXT,
    genres          TEXT[],
    authors         TEXT[],
    translators     TEXT[],
    pub_date        DATE,
    publisher       TEXT,
    language        TEXT,
    original        BOOLEAN,
    timestamp       TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE users (
    user_id         INT             PRIMARY KEY,
    name            TEXT,
    birth_date      DATE,
    join_date       DATE,
    phone_no        TEXT,
    address         TEXT,
    timestamp       TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);


/* creating history tables
to keep track of data changes */
CREATE TYPE hist_action AS ENUM ('updated', 'deleted');


CREATE TABLE books_history (
    isbn            TEXT,
    title           TEXT,
    edition         NUMERIC,
    descr           TEXT,
    genres          TEXT[],
    authors         TEXT[],
    translators     TEXT[],
    pub_date        DATE,
    publisher       TEXT,
    language        TEXT,
    original        BOOLEAN,
    timestamp       TIMESTAMP,
    action          hist_action
);


CREATE TABLE users_history (
    user_id         INT,
    name            TEXT,
    birth_date      DATE,
    join_date       DATE,
    phone_no        TEXT,
    address         TEXT,
    timestamp       TIMESTAMP,
    action          hist_action
);


/* the `borrows` table displays the addition
and removal of books through time */
CREATE TYPE lib_action AS ENUM ('borrowed', 'returned');


CREATE TABLE borrows (
    user_id         INT,
    isbn            TEXT,
    remain_count    SMALLINT,
    timestamp       TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    action          lib_action      DEFAULT 'borrowed'
);


/* creating triggers for `books` so no data
is actually deleted or updated (i.e. lost forever)*/
CREATE OR REPLACE FUNCTION add_bk_hist() RETURNS TRIGGER AS
$add_bk_hist$
    BEGIN
        IF TG_OP = 'UPDATE'
        THEN
            INSERT INTO books_history VALUES (OLD.*, 'updated');
            RETURN NEW;

        ELSEIF TG_OP = 'DELETE'
        THEN
            INSERT INTO books_history VALUES (OLD.*, 'deleted');
            RETURN OLD;

        END IF;
    END;
$add_bk_hist$ LANGUAGE plpgsql;


CREATE TRIGGER books_changed
    AFTER UPDATE OR DELETE ON books
    FOR EACH ROW
    EXECUTE FUNCTION add_bk_hist();


/* creating triggers for `users` so no data
is actually deleted or updated */
CREATE OR REPLACE FUNCTION add_usr_hist() RETURNS TRIGGER AS
$add_usr_hist$
    BEGIN
        IF TG_OP = 'UPDATE'
        THEN
            INSERT INTO users_history VALUES (OLD.*, 'updated');
            RETURN NEW;

        ELSEIF TG_OP = 'DELETE'
        THEN
            INSERT INTO users_history VALUES (OLD.*, 'deleted');
            RETURN OLD;

        END IF;
    END;
$add_usr_hist$ LANGUAGE plpgsql;


CREATE TRIGGER users_changed
    AFTER UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION add_usr_hist();


-- trigger for borrows
CREATE OR REPLACE FUNCTION update_borrow_status() RETURNS TRIGGER AS
$update_borrow_status$
    BEGIN
        IF TG_OP = 'DELETE'
        THEN
            INSERT INTO borrows(user_id, isbn, remain_count, action)
                VALUES (OLD.user_id, OLD.isbn, OLD.remain_count + 1, 'returned');
            RETURN NULL;
        END IF;
    END;
$update_borrow_status$ LANGUAGE plpgsql;


CREATE TRIGGER book_returned
    BEFORE DELETE ON borrows
    FOR EACH ROW
    EXECUTE FUNCTION update_borrow_status();
