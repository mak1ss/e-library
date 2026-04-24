ALTER TABLE book
ADD FULLTEXT INDEX ft_book_search (title, isbn, description);