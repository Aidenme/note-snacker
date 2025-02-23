class Book:
    def __init__(self, title, author, button):
        self.title = title
        self.author = author
        self.button = button
        self.soup = None

    def __str__(self):
        return self.title
    
    def select(self):
        self.button.click()

    def checkSoup(self):
        if self.soup == None:
            print("Book is missing its soup!")
            return False
        else:
            print("Book has its soup!")
            return True