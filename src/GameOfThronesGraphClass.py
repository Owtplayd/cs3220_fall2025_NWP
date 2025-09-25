from src.DynastyClass import Dynasty

class GameOfThronesGraph:
    def __init__(self, corpus):
        #initialisation of dictionary that will store all houses. They keys are Houses' (Dynasty) names, the values are Dynasty objects.
        self.houses = {}
        #Load the show corpus
        for data_item in corpus:
            house=Dynasty(data_item['name'])
            for character in data_item['characters']:
                house.append(character)
            self.houses[data_item['name']]=house

    def __iter__(self):
        for house in self.houses.values():
            yield house
            
    def __contains__(self, h): #Check if h (house's name) is a key in dict houses
        if h in self.houses:
            return True
        else:
            return False