class Library:

    def __init__(self):
        self.book = []

    def add_book(self, title, author):
        self.book.append({'title': title, 'author': author})
        print(f"Added book {title} by {author}✅")

    def remove_book(self, title):
        for book in self.book:
            if book['title'].lower() == title.lower():
                self.book.remove(book)
                return True
        return False

    def search_book(self, title):
        return [book for book in self.book if book['title'].lower() == title.lower()]

    def show_books(self):
        return self.book