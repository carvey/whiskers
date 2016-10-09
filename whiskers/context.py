

class ApplicationContext:

    def __init__(self):
        pass

    def add(self, key, value):
        self.__dict__[key] = value

    # def list_context(self):

app = ApplicationContext()