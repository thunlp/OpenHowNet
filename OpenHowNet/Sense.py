"""
Sense Class
=============
"""

class Sense(object):
    """Contains variables of a sense.

    Initialized by an item in HowNet.
    Contains numbering, word, POS of word, sememe tree, etc.

    Attributes:
        No: the id of the sense in HowNet.
        en_word: the word describing the sense in HowNet in English.
        en_grammar: the POS of the word in English.
        ch_word: the word describing the sense in HowNet in Chinese.
        ch_grammar: the POS of the word in Chinese.
        Def: the sememe tree of the sense.
    """

    def __init__(self, hownet_sense):
        """Initialize a sense object by a hownet item.

        Initialize the attributes of the sense.

        :param hownet_sense: (Dict)The Annotation of the sense in HowNet.
        """
        self.No = hownet_sense['No']
        self.en_word = hownet_sense['en_word']
        self.en_grammar = hownet_sense['en_grammar']
        self.ch_word = hownet_sense['ch_word']
        self.ch_grammar = hownet_sense['ch_grammar']
        self.Def = hownet_sense['Def']
        self.sememes = []
        self.synonym = []

    def __repr__(self):
        """
        Define how to print the sense.
        """
        return 'No.'+self.No


