#!/home/andrew/anaconda3/bin/python3.5
import pandas as pd
import json

class AllSets:
    def __init__(self):
        self.cards = dict(json.load(open("AllCards-x.json")))
       # self.modern_cards = pd.DataFrame(json.load(open("modern_cards.json"))).sort_values(by="releaseDate")
       # self.sets = self.cards.keys()
       # self.modern_sets = self.modern_cards.index.values 


class MTG_DB(AllSets):
    #@profile
    def __init__(self):
        super().__init__()
        self.matches = []

    #@profile
    def search(self, string, field):
        for card in self.cards.keys():
            try:
                search = self.cards[card][field]

                if str(search) == "nan": 
                    continue

                if (field in ["cmc", "power", "toughness"]) or isinstance(search, float):
                    if int(string) == search:
                        self.matches.append(self.cards[card])

                if (field in ["rulings", "legalities", "printings"]) and search:
                    for item in search:
                        if string in item.values():
                            self.matches.append(self.cards[card]) 

                elif (string in search):
                    self.matches.append(self.cards[card])
            except KeyError:
                continue

        self.matches = pd.DataFrame(self.matches)
        if not self.matches.empty:
            return MTGCard(self.matches)
        else:
            print("No matches found in %s for \'%s\'" % (
                                     field, string))
            return False


class MTGCard:
    def __init__(self, df):
        """
        :var df = dataframe (result of Match.search or AllSets.search)
        """
        self.df = df
        self.columns = df.columns
        self.set_mappings = dict(eval(json.load(open("set_map.json"))))
    
    #@profile
    def __getitem__(self, x):
        """ 
        displays each card in pretty nice format 
        """
        legalities = []
        printings = []
        result = self.df.iloc[x]
        item = result["name"]

#        if (str(result) == "nan") or not isinstance(result, pd.Series):
#            result = self.df.ix[item]

        for item in result["printings"]:
            printings = self.set_mappings[item]

        if isinstance(result["legalities"], float): 
            return False

        for item in result["legalities"]:
            if item["format"] == "Modern": 
                legalities += item.items()

        if "Creature" in result["type"]:
            try:
                print("\n%s %s\n%s (%s\%s)\n%s %s\n%s" % (
                        result["name"], result["manaCost"], 
                        result["type"], result["power"], result["toughness"],
			printings, legalities, result["text"]))
                return result
            except UnicodeEncodeError as e:
                print("Warning: cannot encode %s\n%s" % (result["name"], e))
        else:
            try:
                print("\n%s %s\n%s\n%s %s\n%s" % (
                        result["name"], result["manaCost"], result["type"],
			printings, legalities, result["text"]))
                return result
            except UnicodeEncodeError as e:
                print("\n>>> Warning: cannot encode %s\n%s" % (result["name"], e))


if __name__ == "__main__":
    from sys import argv

    field, string = argv[1], argv[2]
    mag = MTG_DB()
    results = mag.search(string, field) 

    if results:
        pretty_results = [results[x] for x in range(len(results.df))]
    else:
        print("No results found for %s in \'%s\'" % (string, field))
