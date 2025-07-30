"""The Hand class represents a dealt hand of thirteen cards."""

from .card import Card
from .denomination import Denomination
from .suit import Suit, Spades, Hearts, Diamonds, Clubs
from .constants import (SUIT_NAMES, RANKS, SUITS, HONOUR_POINTS, SEATS,
                        BALANCED_SHAPES, SEMI_BALANCED_SHAPES,
                        CARD_NAMES, DISPLAY_SUIT_ORDER)

__all__ = ['Hand']


CANDIDATES_4441 = {'S': SUITS['H'], 'H': SUITS['S'],
                    'D': SUITS['H'], 'C': SUITS['S']}


class Hand(object):
    """
    A hand object for the bridgeobjects module.

    A hand can be created using a list of card names,
    a *PBN* string, a list of card objects,
    or with no cards (an invalid hand).

    Parameters
    ----------
        cards: (list) a list of card names. e.g. ['AS', 'TS', 'QC' ... ]
    or
        cards: (list) a list of card objects.
        e.g. [Card('AS'), Card('TS'), Card('QC'), ... ]
    or
        cards: (str) a string representing the cards in PBN format,
        e.g. ('A8654.KQ5.T.QJT6')

    Example
    -------

        card_list = ["JS", "8S", "5S", "4S", "3S", "2S",
                        "JH", "8H", "6H", "AD", "JD", "KC", "JC"]
        hand = Hand(card_list)

    Example
    -------

        hand = Hand('A8654.KQ5.T.QJT6')

    Cards are sorted in descending order by suit and rank.
    """

    def __init__(self, cards: list[Card] | str | None = None):
        """
        Create a list of cards from the input parameter and
        check that the hand is valid and assign properties.
        """
        # display attributes
        self._suit_order = DISPLAY_SUIT_ORDER
        self._cards = []

        # attributes set once the cards are known for the hand
        self._high_card_points = -1
        self._shape: list[int] = [0 for seat in SEATS]
        self._equal_long_suits = False
        self._suits_by_length = None
        self._longest_suit = None
        self._second_suit = None
        self._third_suit = None
        self._shortest_suit = None

        self._spades = -1
        self._hearts = -1
        self._diamonds = -1
        self._clubs = -1

        self._aces = -1
        self._kings = -1
        self._queens = -1
        self._jacks = -1
        self._tens = -1
        self._nines = -1
        self._tens_and_nines = -1

        self._is_valid = False

        # set the hand's minor properties
        # These are initialised to None, and
        # evaluated the first time they are required.
        self._cards_by_suit: dict[str, list[Card]] = {}
        self._distribution_points = 0
        self._is_balanced = None
        self._is_semi_balanced = None
        self._rule_of_nineteen = None
        self._rule_of_twenty = None

        if cards:
            self._cards = self._set_cards(cards)

    def _set_cards(self, cards: list[Card] | str) -> list[Card]:
        """Return the hand's cards as a list of Card objects."""
        if not cards:
            return []

        card_list = []
        if isinstance(cards, str):
            card_list = self._get_cards_from_pbn_string(cards)

        elif not isinstance(cards, list):
            raise TypeError('Invalid type - cards')

        else:
            if isinstance(cards[0], str):
                card_list = self._get_card_list_from_card_names(cards)
            else:
                card_list = self._get_card_list_from_list_of_cards(cards)

        self._cards = card_list
        if self._cards:
            self._shape = self._get_shape()
            self._longest_suit = self._get_longest_suit()

        return card_list

    def _get_card_list_from_card_names(self, cards: list[str]) -> list[Card]:
        """Return a list of cards from list of card names."""
        card_list = []
        for card in cards:
            if not isinstance(card, str):
                type_desc = type(card).__name__
                raise TypeError(f'Invalid card type for "{card}" ({type_desc})')
            elif card not in CARD_NAMES:
                raise ValueError(f'{card} is not a valid card name')
            card_list.append(Card(card))
        return card_list

    def _get_card_list_from_list_of_cards(self, cards: list[str]) -> list[Card]:
        """Return a list of cards from a list of cards."""
        card_list = []
        for card in cards:
            if not isinstance(card, Card):
                raise TypeError(f'Invalid card type {card}')
            card_list.append(card)
        return card_list

    def __repr__(self) -> str:
        return f'Hand("{self._get_pbn_string()}")'

    def __str__(self) -> str:
        sorted_cards = sorted(self._cards, key=lambda x: x.order, reverse=True)
        cards = [card.name for card in sorted_cards]
        return f'Hand({", ".join(cards)})'

    def __eq__(self, other) -> bool:
        """Provide eq functionality for hands"""
        if self._get_pbn_string() == other:
            return True
        else:
            return False

    @property
    def cards(self) -> list[Card]:
        """
        The hand's cards.

        Returns a list of Card objects, one for each card in the hand.
        """
        return self._cards

    @cards.setter
    def cards(self, value: list[Card] | str) -> list[Card]:
        """Sets the hand's cards."""
        # value can be a list of card names, a list of Card objects or
        # a PBN string.
        self._cards = self._set_cards(value)

    @property
    def is_valid(self) -> bool:
        """
        Indicates whether or not the hand is valid.

        Returns True if valid and False if not. Invalid hands might have
        too few or too many cards, or duplicate cards.
        """
        return self._check_is_valid()

    @property
    def spades(self) -> int:
        """Return the number of spade cards in the hand as an integer."""
        return self._spades

    @property
    def hearts(self) -> int:
        """Return the number of heart cards in the hand as an integer."""
        return self._hearts

    @property
    def diamonds(self) -> int:
        """Return the number of diamond cards in the hand as an integer."""
        return self._diamonds

    @property
    def clubs(self) -> int:
        """Return the number of club cards in the hand as an integer."""
        return self._clubs

    @property
    def aces(self) -> int:
        """Return the number of aces in the hand as an integer."""
        if self._aces < 0:
            self._assign_honours()
        return self._aces

    @property
    def kings(self) -> int:
        """Return the number of kings in the hand as an integer."""
        if self._kings < 0:
            self._assign_honours()
        return self._kings

    @property
    def queens(self) -> int:
        """Return the number of queens in the hand as an integer."""
        if self._queens < 0:
            self._assign_honours()
        return self._queens

    @property
    def jacks(self) -> int:
        """Return the number of jacks in the hand as an integer."""
        if self._jacks < 0:
            self._assign_honours()
        return self._jacks

    @property
    def tens(self) -> int:
        """Return the number of tens in the hand as an integer."""
        if self._tens < 0:
            self._assign_honours()
        return self._tens

    @property
    def nines(self) -> int:
        """Return the number of nines in the hand as an integer."""
        if self._nines < 0:
            self._assign_honours()
        return self._nines

    @property
    def tens_and_nines(self) -> int:
        """Returns a count of the tens + nines in the hand."""
        if self._tens_and_nines < 0:
            self._assign_honours()
        return self._tens_and_nines

    @property
    def seven_card_suit_or_better(self) -> bool:
        """Return True if the longest suit has seven or more cards."""
        return self._shape[0] >= 7

    @property
    def seven_card_suit(self) -> bool:
        """Return True if the longest suit has precisely seven cards."""
        return 7 in self._shape

    @property
    def six_card_suit_or_better(self) -> bool:
        """Return True if the longest suit has six or more cards."""
        return self._shape[0] >= 6

    @property
    def six_card_suit(self) -> bool:
        """Return True if the longest suit has precisely six cards."""
        return 6 in self._shape

    @property
    def five_card_suit_or_better(self) -> bool:
        """Return True if the longest suit has five or more cards."""
        return self._shape[0] >= 5

    @property
    def five_card_suit(self) -> bool:
        """Return True if the longest suit has precisely five cards."""
        return 5 in self._shape

    @property
    def five_card_major_or_better(self) -> bool:
        """Return True if the hand has a major suit with five or more cards."""
        return self._spades >= 5 or self._hearts >= 5

    @property
    def five_card_major(self) -> bool:
        """Return True if the hand has a major suit with precisely 5 cards."""
        return self._spades == 5 or self._hearts == 5

    @property
    def five_card_major_suit(self) -> Suit:
        """Return the suit if the hand has a major suit with 5 or more cards."""
        return self._get_major_suit(5)

    @property
    def four_card_major_or_better(self) -> bool:
        """Return True if the hand has a major suit with four or more cards."""
        return self._spades >= 4 or self._hearts >= 4

    @property
    def four_card_major(self) -> bool:
        """Return True if the hand has a major suit with 4 or more cards."""
        return self._spades >= 4 or self._hearts >= 4

    @property
    def four_card_major_suit(self) -> Suit:
        """Return the suit if the hand has a major suit with 4 or more cards."""
        return self._get_major_suit(4)

    @property
    def equal_long_suits(self) -> bool:
        """Return True if the two longest suits are the same length."""
        if len(self._shape) < 4:
            self._shape = self._get_shape(self.cards)
        self._equal_long_suits = self._shape[0] == self._shape[1]
        return self._equal_long_suits

    @property
    def shape(self) -> list[int]:
        """Return the shape of the hand as a list in descending
           order by holding e.g. [4, 3, 3, 3]."""
        # if len(self._shape) != 4:
        #     self._get_suit_lengths()
        #     self._shape = self._get_shape()
        return self._shape

    def suit_length(self, suit: Suit | str) -> int:
        """Return the length of a suit."""
        if isinstance(suit, str):
            suit = Suit(suit)
        if suit.is_suit:
            return self.suit_holding[suit]
        else:
            raise TypeError("suit must be a suit instance")

    @property
    def suits_by_length(self) -> list[Suit] | None:
        """Return the list of hand's suits, in descending order by holding."""
        if self._suits_by_length is None:
            self._suits_by_length = self._get_suits_by_length()
        return self._suits_by_length

    @property
    def longest_suit(self) -> Suit | None:
        """
        Return the longest suit in the hand as a Suit object.

        If the hand contains two five card suits, return the higher ranking;
        if the hand contains two four card suits, return the lower ranking;

        if the hand is 4441 shape:

        1. if the singleton is a black suit, return the middle ranking
        of the four card suits;

        2. if the singleton is a red suit, return the
        suit below the singleton.
        """
        if not self._longest_suit:
            self._longest_suit = self._get_longest_suit()
        return self._longest_suit

    @property
    def second_suit(self) -> Suit | None:
        """
        Return the second longest suit in the hand as a Suit object.

        If the hand contains two five card suits, return the lower ranking;
        if the hand contains two four card suits, return the higher ranking;

        if the hand is 4441 shape:

        1. if the singleton is spades or diamonds, return hearts;

        2. if the singleton is a hearts or clubs, return spades.
        """
        if not self._second_suit:
            self._second_suit = self._get_second_suit()
        return self._second_suit

    @property
    def third_suit(self) -> Suit | None:
        """Return the third longest suit in the hand as a Suit object."""
        if not self._third_suit:
            self._third_suit = self._get_third_suit()
        return self._third_suit

    @property
    def shortest_suit(self) -> Suit | None:
        """Return the shortest suit in the hand as a Suit object."""
        if not self._shortest_suit:
            self._shortest_suit = self._get_shortest_suit()
        return self._shortest_suit

    @property
    def distribution_points(self) -> int:
        """
        Return the distribution points count for the hand.

        Add 3 for a void, 2 for a singleton and 1 for a doubleton.
        """
        if not self._distribution_points:
            self._distribution_points = self._get_distribution_points()
        return self._distribution_points

    @property
    def high_card_points(self) -> int:
        """
        Return the (Milton Work) high card points for the hand.

        Add 4 for an ace, 3 for a king, 2 for a queen and 1 for a jack.
        """
        if self._high_card_points < 0:
            self._high_card_points = self._get_high_card_points()
        return self._high_card_points

    @property
    def hcp(self) -> int:
        """An alias for high_card_points."""
        return self.high_card_points

    @property
    def four_four_four_one(self) -> bool:
        """Return True if the hand shape is [4, 4, 4, 1]."""
        return self.shape == [4, 4, 4, 1]

    @property
    def five_four_or_better(self) -> bool:
        """Return True if hand contains 5 card suit and
            a 4 card suit or better.
        """
        return self.shape[0] >= 5 and self.shape[1] >= 4

    @property
    def five_five_or_better(self) -> bool:
        """Return True if hand contains two five card suits or better."""
        return self.shape[0] >= 5 and self.shape[1] >= 5

    @property
    def five_four(self) -> bool:
        """Return True if hand contains a 5 card suit and a 4 card suit."""
        return self.shape[0] >= 5 and self.shape[1] == 4

    @property
    def five_five(self) -> bool:
        """Return True if hand contains two five card suits."""
        return self.shape[0] >= 5 and self.shape[1] >= 5

    @property
    def six_four(self) -> bool:
        """Return True if hand contains a 6 and a 4 card suit."""
        return self.shape[0] >= 6 and self.shape[1] >= 4

    @property
    def six_six(self) -> bool:
        """Return True if hand contains two 6 card suits."""
        return self.shape[0] >= 6 and self.shape[1] >= 6

    @property
    def seven_six(self) -> bool:
        """Return True if hand contains one 7 and one 6 card suit."""
        return self.shape[0] == 7 and self.shape[1] == 6

    @property
    def is_balanced(self) -> bool:
        """Return True if 'shape' matches one of the balanced shapes."""
        return self._get_is_balanced()

    @property
    def is_semi_balanced(self) -> bool:
        """
            Return True if 'shape' matches one of the balanced or
            semi-balanced shapes.
        """
        return self._get_is_semi_balanced()

    @property
    def rule_of_nineteen(self) -> bool:
        """Return True if the hand fits the rule on nineteen.

           I.e. if the sum of the cards in the two longest suits, plus
           the high card points is greater than or equal to nineteen.
        """
        return self._get_rule_of_n(19)

    @property
    def rule_of_twenty(self) -> bool:
        """Return True if the hand fits the rule of twenty.

           I.e. if the sum of the cards in the two longest suits, plus
           the high card points is greater than or equal to twenty.
        """
        return self._get_rule_of_n(20)

    @property
    def suit_holding(self) -> dict[object, int]:
        """Return a dict holding the number of spades etc.."""
        return self._suit_holding()

    def _suit_holding(self) -> dict[object, int]:
        """Return a dict holding the number of spades etc."""
        return {
            SUITS['S']: self._spades,
            SUITS['H']: self._hearts,
            SUITS['D']: self._diamonds,
            SUITS['C']: self._clubs,
            'S': self._spades,
            'H': self._hearts,
            'D': self._diamonds,
            'C': self._clubs,
            Spades: self._spades,
            Hearts: self._hearts,
            Diamonds: self._diamonds,
            Clubs: self._clubs,
        }

    @property
    def cards_by_suit(self) -> dict[str, list[Card]]:
        """Return a dict holding the cards by suit."""
        if not self._cards_by_suit:
            self._cards_by_suit = self._get_cards_by_suit()
        return self._cards_by_suit

    @property
    def honours(self) -> dict[str, int]:
        """Return a dict of the count of honours  by suit name."""
        honours = {}
        honour_names = 'AKQJT'
        for suit_name in SUITS:
            honour_count = 0
            for honour in honour_names:
                if Card(''.join([honour, suit_name])) in self.cards:
                    honour_count += 1
            honours[suit_name] = honour_count
        return honours

    @property
    def suit_order(self) -> str:
        """Return the value of suit order as a string."""
        return self._suit_order

    @suit_order.setter
    def suit_order(self, value: str) -> list[str]:
        """Set the value of suit order as a string."""
        if not isinstance(value, str):
            raise TypeError('Suit order must be a string')
        elif not len(value) == 4:
            raise ValueError('Suit order must be 4 characters')
        suit_names = [name for name in SUIT_NAMES]
        for suit in value:
            if suit not in suit_names:
                raise ValueError(f'{value} is an ill-formed suit_order')
            suit_names.remove(suit)
        self._suit_order = value

    @property
    def suit_lengths(self) -> dict[str: int]:
        """ Return a dict of suit names: length."""
        return {
            'S': self._spades,
            'H': self._hearts,
            'D': self._diamonds,
            'C': self._clubs
        }

    def sorted_cards(self, suit_order: str = '',
                     high_card_left: bool = True) -> list[Card]:
        """Return the card list sorted according to the
            suit order and high card left.
        """
        if not suit_order:
            suit_order = self._suit_order
        return self.sort_card_list(self.cards, suit_order=suit_order,
                                   high_card_left=high_card_left)

    def suit_points(self, suit: Suit | Denomination | str) -> int:
        """Return the number of high card points in that suit."""
        return self._get_suit_points(suit)

    def rule_of_fourteen(self, suit: Suit) -> bool:
        """Return True if the suit meets the rule of fourteen.

           I.e. if the number of points plus the high card points
           in that suit is equal to or greater than fourteen.
        """
        return self._get_rule_of_fourteen(suit)

    def solid_suit_honours(self, suit: Suit) -> bool:
        """Return True if the the hand has A, K, Q, J. in 'suit'"""
        return self._get_solid_suit_honours(suit)

    @staticmethod
    def maximum_points_for_shape(shape: list[int]) -> int:
        """Return the maximum points achievable given a shape."""
        points = 0
        honour_list = 'AKQJ'
        for cards in shape:
            honours = honour_list[:cards]
            for honour in honours:
                points += HONOUR_POINTS[honour]
        return points

    def cards_in_suit(self, suit: Suit) -> int:
        """Return the number of cards of 'suit' in the hand."""
        cards = 0
        for card in self._cards:
            if card.suit.name == suit.name:
                cards += 1
        return cards

    @staticmethod
    def _get_cards_from_pbn_string(pbn_string) -> list[Card]:
        """Return a list of cards from a string in PBN format."""
        suit_names = SUIT_NAMES[::-1]
        cards = []
        suit_cards = pbn_string.split(".")
        if len(suit_cards) != 4:
            raise ValueError(f'{pbn_string} is an ill-formed hand string')
        for suit, card_string in enumerate(suit_cards):
            suit_name = suit_names[suit]
            for card in card_string:
                if card not in RANKS:
                    raise ValueError(f'{card} is not a valid card rank')
                cards.append(Card(card + suit_name))
        return cards

    def _check_is_valid(self) -> bool:
        """Return True if the hand is well formed."""
        return (self._check_is_valid_length() and
                self._check_is_valid_duplicates())

    def _check_is_valid_length(self) -> bool:
        """Return True if the hand has 13 cards."""
        if len(self._cards) != 13:
            return False
        return True

    def _check_is_valid_duplicates(self) -> bool:
        """Return True if the hand has no duplicate cards."""
        duplicate_names = []
        names = [card.name for card in self._cards]
        for name in names:
            if name in duplicate_names:
                return False
            duplicate_names.append(name)
        return True

    def _get_suit_lengths(self, card_list: list[Card]) -> tuple[int]:
        """Set the number of cards in each suit as an integer."""
        (spades, hearts, diamonds, clubs) = (0, 0, 0, 0)
        for card in card_list:
            if card.suit == SUITS['S']:
                spades += 1
            elif card.suit == SUITS['H']:
                hearts += 1
            elif card.suit == SUITS['D']:
                diamonds += 1
            elif card.suit == SUITS['C']:
                clubs += 1
        return (spades, hearts, diamonds, clubs)

    def _get_shape(self) -> list[int]:
        """Return the shape of the hand, e.g. [4, 4, 4, 1]."""
        if self._spades < 0:
            (self._spades, self._hearts,
            self._diamonds, self._clubs) = self._get_suit_lengths(self.cards)
        shape = [self._spades, self._hearts, self._diamonds, self._clubs]
        return sorted(shape, reverse=True)

    def _get_suits_by_length(self) -> list[Suit]:
        """Return a list of suits in decreasing order of suit length."""
        holdings = {SUITS['S']: self._spades,
                    SUITS['H']: self._hearts,
                    SUITS['D']: self._diamonds,
                    SUITS['C']: self._clubs}
        suits_by_length = []
        key = lambda item: (item[1], item[0])
        for suit, holding in sorted(holdings.items(), key=key, reverse=True):
            del holding
            suits_by_length.append(suit)
        return suits_by_length

    def _get_honours(self, card_list: list[Card]) -> tuple[int]:
        """Set the number of aces, kings, ..., nines in a hand."""
        (aces, kings, queens, jacks,
         tens, nines, tens_and_nines) = (0, 0, 0, 0, 0, 0, 0)
        for card in card_list:
            if card.rank == 'A':
                aces += 1
            elif card.rank == 'K':
                kings += 1
            elif card.rank == 'Q':
                queens += 1
            elif card.rank == 'J':
                jacks += 1
            elif card.rank == 'T':
                tens += 1
            elif card.rank == '9':
                nines += 1
        tens_and_nines = tens + nines
        return (aces, kings, queens, jacks, tens, nines, tens_and_nines)

    def _assign_honours(self) -> tuple[int]:
        """Assign honours to internal values."""
        (self._aces, self._kings, self._queens,
         self._jacks, self._tens, self._nines,
         self._tens_and_nines) = self._get_honours(self.cards)

    def _get_major_suit(self, min_length: int) -> Suit | None:
        """Return suit if hand contains a major suit with the
            given number of cards or more. With cards greater then four,
            return the higher of equal length suits,
            otherwise return the lower ranking of two equal length suits.
        """
        if min_length >= 5:
            if self._spades >= min_length and self._spades >= self._hearts:
                return SUITS['S']
            elif self._hearts >= min_length:
                return SUITS['H']
        else:
            if self._hearts >= min_length and self._hearts >= self._spades:
                return SUITS['H']
            elif self._spades >= min_length:
                return SUITS['S']
        return None

    def _get_longest_suit(self) -> Suit:
        """Return the longest suit in the hand."""
        if len(self.shape) < 4:
            self._get_shape()
        if self._shape[0] > self._shape[1]:
            return self.suits_by_length[0]

        suit_one = self.suits_by_length[0]
        suit_two = self.suits_by_length[1]

        # 5/5 hands or 6/6
        if self._shape[1] >= 5:
            if suit_one > suit_two:
               return suit_one
            return suit_two  # Never be called!

        # 4/4 hands
        elif self._shape[2] <= 3:
            if suit_one > suit_two:
                return suit_two
            return suit_one  # Never be called!

        # 4441 hands
        singleton_suit = self.suits_by_length[3]
        candidates = {'S': SUITS['D'], 'H': SUITS['D'],
                        'D': SUITS['C'], 'C': SUITS['H']}
        return candidates[singleton_suit.name]

    def _get_second_suit(self) -> Suit:
        """Return the second longest suit in the hand."""
        if (self._shape[0] > self._shape[1] and
                (self.shape[2] != 4 or self.hcp >= 16)):
            return self._suits_by_length[1]

        suit_one = self._suits_by_length[0]
        suit_two = self._suits_by_length[1]

        # 5/5 hands (or 6/6)
        if self._shape[0] >= 5 and self.shape[1] >= 5:
            if suit_two < suit_one:
                return suit_two
            return suit_one  # Never be called!

        # 4/4 hands
        elif self._shape[2] <= 3:
            if suit_one > suit_two:
                return suit_one
            return suit_two  # Never be called!

        # 4441 hands
        elif self.four_four_four_one:
            singleton_suit = self._suits_by_length[3]
            return CANDIDATES_4441[singleton_suit.name]

        suit_one = self._suits_by_length[1]
        suit_two = self._suits_by_length[2]
        if suit_one.rank < suit_two.rank:
            return suit_one  # Never be called!
        return suit_two

    def _get_third_suit(self) -> Suit:
        """Return the third longest suit in the hand."""
        suit_three = self._suits_by_length[2]
        suit_four = self._suits_by_length[3]
        if self._shape[2] > self._shape[3]:
            return self._suits_by_length[2]

        # 4441 hands
        elif self._shape == [4, 4, 4, 1]:
            return self._get_third_suit_4441()
        elif self._shape[2] == self._shape[3]:
            if suit_three < suit_four:
                return suit_four  # Never called!
            return suit_three
        return suit_three  # Never called!

    def _get_third_suit_4441(self) -> Suit | None:
        """Return the third suit for 4441 hands."""
        singleton_suit = self._suits_by_length[3]
        first_suit = CANDIDATES_4441[singleton_suit.name]
        suits = []
        for suit in SUITS.values():
            if suit != singleton_suit and suit != first_suit:
                suits.append(suit)
        if suits[0] < suits[1]:
            second_suit = suits[1]
        else:
            second_suit = suits[0]  # Never called!
        for suit in SUITS.values():
            if (suit != first_suit and
                    suit != second_suit and
                    suit != singleton_suit):
                return suit
        return None

    def _get_shortest_suit(self) -> Suit:
        """Return the shortest suit in the hand."""
        long_suits = [self.longest_suit, self.second_suit, self.third_suit]
        suits = [Suit(suit) for suit in SUITS]
        for suit in long_suits:
            if suit in suits:
                suits.remove(suit)
        return suits[0]

    def _get_distribution_points(self) -> int:
        """Return the distribution points for the hand."""
        distribution_points = 0
        for shape in self._shape:
            if shape <= 3:
                distribution_points += 3 - shape
        return distribution_points

    def _get_high_card_points(self) -> int:
        """Return the high card points for the hand."""
        if self._aces < 0:
            (self._aces, self._kings, self._queens,
             self._jacks, self._tens, self._nines,
             self._tens_and_nines) = self._get_honours(self.cards)
        points = 0
        points += HONOUR_POINTS['A'] * self._aces
        points += HONOUR_POINTS['K'] * self._kings
        points += HONOUR_POINTS['Q'] * self._queens
        points += HONOUR_POINTS['J'] * self._jacks
        return points

    def _get_is_balanced(self) -> bool:
        """Return True if hand matches one of the balanced shapes."""
        return self._shape in BALANCED_SHAPES

    def _get_is_semi_balanced(self) -> bool:
        """Return True if 'shape' matches one of the
            balanced or semi-balanced shapes.
        """
        return (self._shape in BALANCED_SHAPES or
                self._shape in SEMI_BALANCED_SHAPES)

    def _get_rule_of_n(self, points: int) -> bool:
        """Return True if hand meets the Rule of Nineteen or Twenty."""
        if self.high_card_points + self._shape[0] + self._shape[1] >= points:
            return True
        return False

    def _get_suit_points(self, suit: Suit | Denomination | str) -> int:
        """Return the high card points for the suit."""
        suit_points = 0
        suit_name = suit
        if isinstance(suit, (Suit, Denomination)):
            suit_name = suit.name

        for card in self._cards:
            if card.suit.name == suit_name:
                if card.value >= 10:
                    suit_points += card.value-9
        return suit_points

    def _get_rule_of_fourteen(self, suit: Suit) -> bool:
        """Return True if hand number of cards plus
            the suit points equals or exceeds 14 for the given suit'.
        """
        suit_cards = 0
        for card in self._cards:
            if card.suit.name == suit.name:
                suit_cards += 1
        return self.suit_points(suit) + suit_cards >= 14

    def _get_solid_suit_honours(self, suit: Suit) -> bool:
        """Return True if the the hand has A, K, Q, J. in 'suit'"""
        honours = 0
        for card in self._cards:
            if card.suit.name == suit.name:
                if card.value >= 10:
                    honours += 1
        return honours == 4

    def _get_pbn_string(self) -> str:
        """Return hand as a string in pbn format."""
        hand_list = []
        for suit in SUIT_NAMES[::-1]:
            suit_cards = []
            for rank in reversed(RANKS[1:]):
                test_card = Card(rank, suit)
                if test_card in self._cards:
                    suit_cards.append(rank)
            hand_list.append(''.join(suit_cards))
        return '.'.join(hand_list)

    @staticmethod
    def sort_card_list(cards: list[Card], suit_order: str = '',
                       high_card_left: bool = True) -> list[Card]:
        """Return a list of cards sorted by suit and rank."""
        if not suit_order:
            suit_order = DISPLAY_SUIT_ORDER
        card_names = Hand._order_card_names(suit_order, high_card_left)
        sorted_cards = []
        for card_name in card_names:
            card = Card(card_name)
            if card in cards:
                sorted_cards.append(card)
        return sorted_cards

    @staticmethod
    def _order_card_names(suit_order: str, high_card_left: bool) -> list[str]:
        """Return a list of cards."""
        card_names = []
        if high_card_left:
            ranks = RANKS[:0:-1]
        else:
            ranks = RANKS[1:]
        for suit in suit_order:
            for rank in ranks:
                card_names.append(''.join([rank, suit]))
        return card_names

    def _get_cards_by_suit(self) -> dict[str, list[Card]]:
        """Return a dict by suit with cards for suit in descending order."""
        card_suits: dict[str, list[Card]] = {}
        for suit_name in SUIT_NAMES:
            card_suits[suit_name] = []
            for card in self._cards:
                if suit_name == card.suit.name:
                    card_suits[suit_name].append(card)
        return card_suits

    def honour_sequences(self) -> dict[str, list[Card]]:
        """Return a dict of honour sequences by suit (if any)."""
        honour_sequences = self._honours_and_sequences(min_length=3)
        return honour_sequences

    def touching_honours(self) -> dict[str, list[Card]]:
        """Return a dict of touching honours by suit (if any)."""
        touching_honours = self._honours_and_sequences()
        return touching_honours

    def _honours_and_sequences(self,
                               min_length: int = 2) -> dict[str, list[Card]]:
        """Return a dict of honour sequences by suit (if any)."""
        sequences: dict[str, list[Card]] = {}
        for suit in Suit.SHORT_NAMES:
            sequences[suit] = self._get_suit_sequence(suit, min_length)
        return sequences

    def _get_suit_sequence(self, suit: str, min_length: int) -> list[Card]:
        """Return a list of cards."""
        sequence = []
        last_card = None
        sequence_started = False
        for card in self.cards:
            # TODO check that sequence started does not corrupt tests
            if suit != card.suit.name:
                continue
            if card.value < 9 and sequence_started:  # i.e. 'T' or higher
                continue
            sequence_started = True
            if last_card:
                if last_card.value - card.value > 1:
                    break
                elif last_card.value - card.value == 1:
                    if last_card not in sequence:
                        sequence.append(last_card)
                    sequence.append(card)
            last_card = card
        if len(sequence) < min_length:
            return []
        return sequence

    def internal_sequences(self) -> list[Card]:
        """Return a list of internal sequences (if any)."""
        internal_sequences = []
        cards = self.cards
        for suit in Suit.SHORT_NAMES:
            ace = Card('A', suit)
            king = Card('K', suit)
            queen = Card('Q', suit)
            jack = Card('J', suit)
            ten = Card('T', suit)
            nine = Card('9', suit)

            if ace in cards and king not in cards:
                if queen in cards and jack in cards:
                    internal_sequences.append(queen)
            elif king in cards and queen not in cards:
                if jack in cards and ten in cards:
                    internal_sequences.append(jack)
            elif queen in cards and jack not in cards:
                if ten in cards and nine in cards:
                    internal_sequences.append(ten)
        return internal_sequences
