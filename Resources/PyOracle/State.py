####################################################################################
# State.py
# modified 09.18.2012
# greg surges
# copyleft 2011 - 2012
####################################################################################

import Transition

class State():
    def __init__(self, number):
        self.transition = []
        self.suffix = 0
        self.reverse_suffix = []
        self.number = number
        self.lrs = 0

    def __str__(self):
        string_val = ""
        string_val += "number:" 
        string_val += str(self.number)
        string_val += "\nprefixes:" 
        string_val += str([t.pointer.number for t in self.transition])
        if self.suffix:
            string_val += "\nsuffix:"
            string_val += str(self.suffix.number)
        else:
            string_val += "\nsuffix:"
            string_val += str(self.suffix)
        if self.reverse_suffix:
            string_val += "\nreverse suffix:"
            string_val += str([x.number for x in self.reverse_suffix])
        else:
            string_val += "\nreverse suffix:"
            string_val += str(self.reverse_suffix)
        string_val += '\nlrs:'
        string_val += str(self.lrs)
        return string_val

    def add_transition(self, data, prefix_pointer):
        self.transition.append(Transition.Transition(data, prefix_pointer))

    def add_suffix(self, suffix_pointer):
        self.suffix = suffix_pointer
    
    def add_reverse_suffix(self, suffix_pointer):
        self.reverse_suffix.append(suffix_pointer)
