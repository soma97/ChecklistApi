
def insert_decorator(func):
    def insert_info(*args,**kwargs):
        print('Inserting item...')
        func(*args,**kwargs)
    return insert_info

class Checklist:
    def __init__(self, id, name, username):
        self.id=id
        self.name = name
        self.username=username
        self.items=[]
