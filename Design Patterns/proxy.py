"""
You are building a Document Viewer System.
Each document (like a PDF or Word file) can be opened and viewed by users,
but some documents are restricted and require admin access to open.

You need to:
Create a class to represent a document that can be opened.
Introduce a proxy that controls access:
If the user is an admin, allow access.
If not, deny access and log the attempt.
"""

"""
1. Create abstract class
2. Create concrete class
3. Create proxy class
"""

class AbstractDocument:

    def __init__(self, file: str, restricted: bool):
        self.filename = file
        self.restricted = restricted

    def view(self):
        raise NotImplementedError("This should be implemented by sub classes")

class Document(AbstractDocument):

    def __init__(self, file: str, restricted: bool):
        super().__init__(file, restricted)

    def view(self):
        print(f"Opened {self.filename}")

class DocumentProxy(AbstractDocument):

    def __init__(self, user_type: str, doc: Document):
        self.user_type = user_type
        self.doc = doc

    def view(self):
        if self.user_type.lower() != "admin" and self.doc.restricted:
            print("Sorry, you don't have access to open this file!")
            return False
        else:
            self.doc.view()


if __name__=="__main__":
    doc1 = Document("hello.txt", False)
    doc2 = Document("critical.txt", True)
    dv = DocumentProxy("normal", doc1)
    dv.view()
    dv = DocumentProxy("normal", doc2)
    dv.view()
    dv = DocumentProxy("admin", doc1)
    dv.view()
    dv = DocumentProxy("admin", doc2)
    dv.view()
