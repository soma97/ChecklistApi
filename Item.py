import datetime

class Item:
    def __init__(self,id,name,date_time,item_freq,is_done,chk_id):
        self.id=id
        self.name=name
        self.date_time=date_time
        self.item_freq=item_freq  #daily, weekly, monthly
        self.done=is_done
        self.chk_id=chk_id

    def set_done(self,is_done):
        self.done=is_done

    def __add__(self, other):
        return self.name + str(other)

    def __str__(self):
        return self.name

    

