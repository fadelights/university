CREATE TEMPORARY VIEW author_data AS (
    SELECT      isbn, array_agg(person_name) AS authors
    FROM        books INNER JOIN roles ON books.isbn = roles.book_isbn
    WHERE       role = 'author'
    GROUP BY    isbn
);

CREATE TEMPORARY VIEW translator_data AS (
    SELECT      isbn, array_agg(person_name) AS translators
    FROM        books INNER JOIN roles ON books.isbn = roles.book_isbn
    WHERE       role = 'translator'
    GROUP BY    isbn
);

CREATE TEMPORARY VIEW genre_data AS (
    SELECT      isbn, array_agg(genre) AS genres
    FROM        books INNER JOIN book_genres USING (isbn)
                      INNER JOIN genres USING (genre_id)
    GROUP BY    isbn
);

-- gather all book data into one table for easier migration
CREATE TEMPORARY VIEW book_data AS (
    SELECT books.isbn,
           books.title,
           books.edition,
           books.descr,
           genre_data.genres,
           author_data.authors,
           translator_data.translators,
           books.pub_date,
           publishers.pub_name AS publisher,
           books.language,
           books.original

    FROM books LEFT JOIN genre_data USING (isbn)
               LEFT JOIN author_data USING (isbn)
               LEFT JOIN translator_data USING (isbn)
               LEFT JOIN publishers ON books.publisher = publishers.pub_id
);

-- the warehouse needs the `count` column as measure
CREATE TEMPORARY VIEW borrow_data AS (
    SELECT borrows.user_id,
           borrows.book_isbn AS isbn,
           books.count AS remain_count
    
    FROM borrows LEFT JOIN books ON borrows.book_isbn = books.isbn
);
