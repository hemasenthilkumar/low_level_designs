"""
Loose Coupling Principle

- over time the components can become tangled and messy
- to resolve, components should be independant and easier to make changes

Benefits:
- Maintainability
- Extensibility
- Testability

Techniques:
- Dependency Injection - allows components tou recieve dependencies from external source
- Obserber pattern - publish changes to it state so other objects can react accordingly
"""

class MessageService:

    def __init__(self, sender):
        self.sender = sender 
    
    def send(self, message):
        self.sender.send_message(message)

class EmailSender:

    def send_message(self, message):
        print(f"Email send for {message}")

class SMSSender:

    def send_message(self, message):
        print(f"SMS sent for {message}")

if __name__ == "__main__":

    email = MessageService(EmailSender())
    sms = MessageService(SMSSender())

    email.send("Hi")
    sms.send("Welcome")