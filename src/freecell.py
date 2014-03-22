#!/usr/bin/env python
# encoding: utf-8

import sys
 

class Card (object):
    CARD_LABEL = "A23456789TJQK"
    SUIT_LABEL = "CDHS"
    PLAY_LABEL = "BRRB"

    def __init__ (self, card_id, suit_id):
        """constructor"""
        self.card_id = card_id
        self.suit_id = suit_id
        self.x = -1
        self.y = -1
        self.exposed = False
        self.dist = -1


    def __repr__ (self):
        """format card state as a string"""
        state = '*' if self.exposed else ')'
        return "%s%s(%d,%d,%c" % (self.CARD_LABEL[self.card_id], self.SUIT_LABEL[self.suit_id], self.x, self.y, state)


    def set_pos (self, x, y):
        """set the position in the Freecell layout"""
        self.x = x
        self.y = y


    def can_cover (self, other):
        return (other != self) and (self.card_id - other.card_id == 1) and (self.PLAY_LABEL[self.suit_id] != self.PLAY_LABEL[other.suit_id])


class Freecell (object):
    N_CARD = 52
    N_SUIT = 4
    N_TABLEAU = 8
    N_EMPTY = 4

    def __init__ (self, seed):
        """constructor"""
        self.deck = None
        self.layout = None
        self.shuffle(seed)

        self.tableau = [[] for t in range(0, self.N_TABLEAU + self.N_EMPTY)]
        self.foundation = [[] for s in range(0, self.N_SUIT)]


    @staticmethod
    def gen_msft_sequence (seed=1):
        # based on http://rosettacode.org/wiki/Deal_cards_for_FreeCell#Python
        max_int32 = (1 << 31) - 1
        seed = seed & max_int32
 
        while True:
            seed = (seed * 214013 + 2531011) & max_int32
            yield seed >> 16


    def shuffle (self, seed):
        # shuffle based on Jim Horne @MSFT, http://www.solitairelaboratory.com/mshuffle.txt
        rnd = Freecell.gen_msft_sequence(seed)
        self.deck = range(self.N_CARD - 1, -1, -1)

        for i, r in zip(range(self.N_CARD), rnd):
            j = (self.N_CARD - 1) - r % (self.N_CARD - i)
            self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

        # arrange the newly shuffled cards within the layout
        self.layout = [Card(c / self.N_SUIT, c % self.N_SUIT) for c in self.deck]

        for i0 in range(0, len(self.deck), self.N_TABLEAU):
            for x in range(0, self.N_TABLEAU):
                i = i0 + x

                if i < self.N_CARD:
                    y = i0 / self.N_TABLEAU
                    c = self.layout[i]
                    c.set_pos(x, y)


    def build_tableau (self):
        """determine the exposed cards per tableau"""
        for t in range(0, len(self.tableau)):
            self.tableau[t] = sorted([card for card in self.layout if card.x == t], key=lambda card: card.y, reverse=True)

            if len(self.tableau[t]) >= 1:
                self.tableau[t][0].exposed = True
                dist = 0

                for card in self.tableau[t]:
                    card.dist = dist
                    dist += 1


    def show (self):
        print self.foundation

        cards = [card for card in self.layout if card.x >= 0]
        cards.sort(key=lambda c: c.y)

        for y in range(0, max(map(lambda c: c.y, cards)) + 1):
            row = ["        " for t in range(0, len(self.tableau))]

            while (len(cards) > 0) and (cards[0].y == y):
                c = cards.pop(0)
                row[c.x] = c

            print " ", " ".join([str(card) for card in row])


    def analyze_state (self):
        # arrange cards by suits
        suits = [[] for t in range(0, self.N_SUIT)]
        vec_cost = [[] for s in range(0, self.N_SUIT)]

        for card in self.layout:
            suits[card.suit_id].append(card) 

        for suit in suits:
            suit.sort(key=lambda c: c.card_id)
            prev_card = None
            sum_cost = 0

            for card in suit:
                if card.y < 0:
                    # already played
                    pass
                else:
                    if not prev_card:
                        cost = card.dist
                        sum_cost += cost
                        vec_cost[card.suit_id] = [(sum_cost, card)]
                        #print
                        #print card, cost, sum_cost, vec_cost[card.suit_id]
                    else:
                        if card.x == prev_card.x:
                            cost = prev_card.y - card.y
                        else:
                            cost = card.dist + prev_card.dist

                        sum_cost += cost
                        vec_cost[card.suit_id].append((sum_cost, card))
                        #print card, card.dist, prev_card, prev_card.dist, cost, sum_cost, vec_cost[card.suit_id]

                    prev_card = card

        #print
        #print "empty", self.N_EMPTY - len(self.empty), len(self.empty_tableau)

        return vec_cost


    def test_game_over (self):
        """determine whether the game has been won"""
        return self.N_CARD < sum(map(lambda x: len(x), self.foundation))


    def tableau_goals (self, vec_cost):
        """determine the goals per tableau"""
        costs = []
        goals = [self.N_CARD for i in range(0, len(self.tableau))]

        for s in range(0, self.N_SUIT):
            if len(vec_cost[s]) > 1:
                costs.append((s, vec_cost[s][1]))
            elif len(vec_cost[s]) > 0:
                costs.append((s, vec_cost[s][0]))

        costs.sort(key=lambda x: x[1])
        print costs

        for suit, cost in costs:
            print Card.SUIT_LABEL[suit], cost, cost[1].x
            goals[cost[1].x] = cost[0]

        return goals


    def can_found (self, card):
        f = self.foundation[card.suit_id]

        if len(f) > 0:
            if (card.card_id - f[0].card_id) == 1:
                return True
            else:
                return False
        else:
            if card.card_id == 0:
                return True
            else:
                return False


    def game_gradient (self, goals):
        """for each exposed card, enumerate its options"""
        exposed = [ card for card in self.layout if card.exposed ]
        gradient = []

        for card in exposed:
            print card, card.x, goals[card.x]

            if self.can_found(card):
                print "move to foundation"
                gradient.append((0, 0, card, self.move_foundation(card)))
                continue

            moves = [e for e in exposed if e.can_cover(card)]

            if len(moves) > 0:
                print "move to tableau", moves
                tab = moves[0].x

                if tab < self.N_TABLEAU:
                    gradient.append((goals[card.x], 1, card, self.move_tableau(card, tab)))
                    continue

            if card.y > 0:
                for tab in range(0, len(self.tableau)):
                    if len(self.tableau[tab]) == 0:
                        print "move to empty tableau", tab
                        gradient.append((goals[card.x], 2, card, self.move_tableau(card, tab)))
                        break

        gradient.sort()
        return gradient


    def move_foundation (self, card):
        def move ():
            print "play foundation", card
            self.foundation[card.suit_id].insert(0, card)

            card.set_pos(-1, -1)
            card.exposed = False

        return move


    def move_tableau (self, card, x):
        def move ():
            print "play tableau", card
            card.set_pos(x, len(self.tableau[x]))
            card.exposed = True

            for c in self.tableau[x]:
                c.exposed = False

        return move

 
if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) == 2 else 11982
    print "Hand", seed

    fc = Freecell(seed)
    round = 0

    while True:
        round += 1
        print "Round", round

        fc.build_tableau()
        fc.show()

        if fc.test_game_over() or round > 5:
            break

        # traverse the gradient
        costs = fc.analyze_state()

        for s in range(0, fc.N_SUIT):
            print costs[s]

        goals = fc.tableau_goals(costs)
        print goals

        gradient = fc.game_gradient(goals)
        print gradient

        # make a move
        for move in gradient:
            print move
            func = move[3]
            func()
            break
