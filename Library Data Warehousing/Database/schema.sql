CREATE TABLE publishers (
    pub_id      SERIAL      PRIMARY KEY,
    pub_name    TEXT        NOT NULL
);


CREATE TABLE books (
    isbn        TEXT        PRIMARY KEY,
    title       TEXT        NOT NULL,
    edition     NUMERIC,
    descr       TEXT,
    pub_date    DATE,
    publisher   INT         REFERENCES publishers(pub_id),
    language    TEXT,
    original    BOOLEAN,
    "count"     SMALLINT
);


CREATE TYPE role AS ENUM ('author', 'translator');

CREATE TABLE roles (
    role_id     SERIAL      PRIMARY KEY,
    person_name TEXT        NOT NULL,
    book_isbn   TEXT        REFERENCES books(isbn),
    "role"      role
);


CREATE TABLE genres (
    genre_id    SERIAL      PRIMARY KEY,
    genre       TEXT        NOT NULL
);


CREATE TABLE book_genres (
    isbn        TEXT        REFERENCES books(isbn),
    genre_id    INT         REFERENCES genres(genre_id)
);


CREATE TABLE users (
    user_id     SERIAL      PRIMARY KEY,
    name        TEXT        NOT NULL,
    birth_date  DATE,
    join_date   DATE,
    phone_no    TEXT,
    address     TEXT
);


/* function used to ensure book availability */
CREATE FUNCTION available(isbn TEXT) RETURNS BOOLEAN AS
$$
    SELECT CASE
        WHEN (SELECT "count" FROM books WHERE books.isbn = available.isbn) > 0
            THEN TRUE
        ELSE FALSE
    END;
$$ LANGUAGE SQL;

CREATE TABLE borrows (
    user_id     INT         REFERENCES users(user_id),
    book_isbn   TEXT        REFERENCES books(isbn),

    CHECK (available(book_isbn) = TRUE)
);


/* The following triggers update the count
of available books each time a user borrows
or returns a book. */
CREATE FUNCTION update_book_count() RETURNS TRIGGER AS
$update_book_count$
    BEGIN
        IF TG_OP = 'DELETE'
        THEN
            UPDATE books
                SET "count" = "count" + 1
                WHERE isbn = OLD.book_isbn;

        ELSEIF TG_OP = 'INSERT'
        THEN
            UPDATE books
                SET "count" = "count" - 1
                WHERE isbn = NEW.book_isbn;
        END IF;
        RETURN NULL;
    END;
$update_book_count$ LANGUAGE plpgsql;

CREATE TRIGGER borrow_status_changed
    AFTER INSERT OR DELETE ON borrows
    FOR EACH ROW
    EXECUTE FUNCTION update_book_count();
