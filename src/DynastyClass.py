class Dynasty:
    def __init__(self,name):
        self._name=name
        self.characters=[]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value!="":# Validation: Ensure value is not an empty string
            self._name = value

    def append(self, ch):
            assert isinstance(ch, str) #this code will check if character is an instance
                                            #of the String class. If not, an exception
                                            #will be raised
            #append the genre to our list
            self.characters.append(ch)

    def __iter__(self):
            for ch in self.characters:
                yield ch

    def __contains__(self, ch):
        if ch in self.characters:
            return True
        else:
            return False

    def __str__(self):
        return f'This is a House of {self.name}!'
    
    def getStrength(self):
        return len(self.characters)