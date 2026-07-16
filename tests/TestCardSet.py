import unittest
import sys
import random

sys.path.append('.')
from env.utils import CardSuit, TrumpSuit
from env.CardSet import CardSet, MoveType

class TestCardSet(unittest.TestCase):

    def setUp(self) -> None:
        random.seed(123)

        self.cardset_simple = CardSet({
            '2♦': 2,
            '2♥': 2,
            '3♦': 2,
            '3♥': 2,
            '4♦': 2,
            '4♥': 2,
            'XJ': 2
        })

        self.cardset_all_suits = CardSet({
            '8♣': 1,
            '10♠': 2,
            'J♠': 2,
            'Q♠': 1,
            '2♦': 2,
            '9♦': 1,
            '10♦': 1,
            '8♥': 1,
            'DJ': 2
        })

        self.cardset_big_suit = CardSet({
            'A♥': 2,
            'K♥': 2,
            'Q♥': 2,
            'J♥': 2,
            '10♥': 2,
            '4♥': 2,
            '2♥': 2,

            '3♣': 2,
        })

        self.cardset_multiple_small_tractors = CardSet({
            'K♦': 2,
            'Q♦': 2,
            '10♦': 2,
            '9♦': 2,
            '7♦': 2,
            '6♦': 2
        })

        return super().setUp()

    def test_total_points(self):
        cardset = CardSet()
        cardset.add_card('10♣')
        cardset.add_card('7♣')
        cardset.add_card('5♠')
        cardset.add_card('5♠')
        self.assertEqual(cardset.total_points(), 20)
    
    def test_shuffle_deck(self):
        cardset, order = CardSet.new_deck()
        cardset2, order2 = cardset.new_deck()
        assert cardset.size == cardset2.size == 108
        assert len(order) == len(cardset)
        assert order != order2
    
    def test_declaration_options(self):
        fullset, _ = CardSet.new_deck()
        self.assertEqual(len(fullset.trump_declaration_options(14)), 6)

        cardset = CardSet({
            '2' + TrumpSuit.CLUB: 1,
            '2' + TrumpSuit.DIAMOND: 2,
            '2' + TrumpSuit.SPADE: 1,
            'DJ': 1,
            'XJ': 1
        })
        self.assertEqual(len(cardset.trump_declaration_options(2)), 3)
    
    def test_lead_actions_jokers(self):
        cardset = CardSet({
            'DJ': 2,
            'XJ': 2,
            '2' + TrumpSuit.DIAMOND: 2,
            '2' + TrumpSuit.CLUB: 2,
            '2' + TrumpSuit.SPADE: 2
        })
        moves1 = cardset.get_leading_moves(TrumpSuit.SPADE, 2)
        moves2 = cardset.get_leading_moves(TrumpSuit.XJ, 2)
        self.assertEqual(len(moves1), 19) # 5 singles, 5 pairs, 4 length-2 tractors, 3 length-3 tractors, 2 length-4 tractors
        self.assertEqual(len(moves2), 17) # 5 singles, 5 pairs, 4 length-2 tractors, 3 length-3 tractor
    
    def test_lead_actions_skip_dominant_rank(self):
        moves = self.cardset_simple.get_leading_moves(dominant_suit=TrumpSuit.HEART, dominant_rank=3)
        self.assertEqual(len(moves), 19) # 7 singles, 7 pairs, 4 length-2 tractors, 1 length-3 tractor

        moves = self.cardset_big_suit.get_leading_moves(dominant_suit=TrumpSuit.HEART, dominant_rank=3)
        self.assertEqual(len(moves), 32)
    
    def test_count_suit(self):
        # for suit in [CardSuit.CLUB, CardSuit.DIAMOND, CardSuit.HEART, CardSuit.SPADE, CardSuit.TRUMP]:
        self.assertEqual(self.cardset_simple.count_suit(CardSuit.TRUMP, TrumpSuit.HEART, 3), 10)
        self.assertEqual(self.cardset_simple.count_suit(CardSuit.HEART, TrumpSuit.HEART, 3), 0) # Since HEART is trump, there is no card in the HEART category, since they would all be trump cards
        self.assertEqual(self.cardset_simple.count_suit(CardSuit.DIAMOND, TrumpSuit.HEART, 3), 4) # 3s are trump cards, not diamond cards
        self.assertEqual(self.cardset_simple.count_suit(CardSuit.HEART, TrumpSuit.DJ, 3), 4)

    def test_matching_moves_single(self):
        # Analysis: 5♥ is a trump card in this situation, so the player's action set contains all single trump cards.
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Single('5♥'), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 5) # XJ, 3♦, 4♥, 3♥, 2♥ are the 5 valid moves
    
        # Analysis: the player has no ♣ suit cards, so they can choose any of the 7 cards to play.
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Single('5♣'), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 7)

        # Analysis: in NT mode, only the 3s and jokers are trump cards. So 3 action choices in total.
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Single('3♠'), TrumpSuit.XJ, 3)
        self.assertEqual(len(matching_moves), 3) # 3♦, 3♥, XJ

        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Single('7♥'), TrumpSuit.XJ, 3)
        self.assertEqual(len(matching_moves), 2) # 4♥ and 2♥
    
    def test_matching_moves_pair(self):
        matching_moves = self.cardset_all_suits.get_matching_moves(MoveType.Pair('2♠'), TrumpSuit.HEART, 2)
        self.assertEqual(len(matching_moves), 2) # The player can play a pair of 2♦ or jokers

        matching_moves = self.cardset_all_suits.get_matching_moves(MoveType.Pair('3♠'), TrumpSuit.HEART, 2)
        self.assertEqual(len(matching_moves), 2) # Can play a pair of 10♠ or J♠

        # Analysis: the player only has 1 CLUB card. They need to play 1 additional card. There are 8 to choose from.
        matching_moves = self.cardset_all_suits.get_matching_moves(MoveType.Pair('3♣'), TrumpSuit.HEART, 2)
        self.assertEqual(len(matching_moves), 8)

        # Analysis: the player has no CLUB cards. So they can pick any two cards to play. If they play a trump pair, it's a RUFF so it's counted as a pair. If they choose any two other cards, it's counted as a passive combo.
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Pair('3♣'), TrumpSuit.HEART, 2)
        self.assertEqual(len(matching_moves), 28) # 7 pairs + 21 two card combos

        matching_moves = self.cardset_all_suits.get_matching_moves(MoveType.Pair('4♦'), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 1)
    
    def test_matching_moves_tractor(self):
        # Analysis: the player has 3 exact matches (tractor of length 2)
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Tractor(CardSet({'5♥': 2, '6♥': 2})), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 3) # Either [2♥ 2♥ 4♥ 4♥], [3♦ 3♦ 3♥ 3♥], or [3♥ 3♥ XJ XJ]

        # Analysis: the player doesn't have a single match in the same suit. So they can choose any 4 cards.
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Tractor(CardSet({'5♠': 2, '6♠': 2})), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 161)

        # Analysis: the player doesn't have a tractor, but has one or more pairs. They have to play them first, then choose cards of the same suit, then any card.
        matching_moves = self.cardset_all_suits.get_matching_moves(MoveType.Tractor(CardSet({'5♦': 2, '6♦': 2})), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 1) # The player has 4 diamonds and needs to play all of them.

        # Analysis: the player has [3♦ 3♦ 3♥ 3♥ XJ XJ] as a length-3 tractor
        matching_moves = self.cardset_simple.get_matching_moves(MoveType.Tractor(CardSet({'5♥': 2, '6♥': 2, '7♥': 2})), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 1)

        matching_moves = self.cardset_big_suit.get_matching_moves(MoveType.Tractor(CardSet({'6♥': 2, '7♥': 2})), TrumpSuit.HEART, 3)
        self.assertEqual(len(matching_moves), 6)

        # Analysis: the player has no length-3 tractors. They need to pick a length-2 tractor, and then pick some other pair.
        matching_moves = self.cardset_multiple_small_tractors.get_matching_moves(MoveType.Tractor(CardSet({'3♦': 2, '4♦': 2, '5♦': 2})), TrumpSuit.HEART, 2)
        self.assertEqual(len(matching_moves), 12)

        # Analysis: the player has no length-4 tractors. They need to pick two length-2 tractors to play.
        matching_moves = self.cardset_multiple_small_tractors.get_matching_moves(MoveType.Tractor(CardSet({'2♦': 2, '3♦': 2, '4♦': 2, '5♦': 2})), TrumpSuit.HEART, 14)
        self.assertEqual(len(matching_moves), 3)


    def test_combo_moves(self):
        decomposition = self.cardset_multiple_small_tractors.decompose(TrumpSuit.DJ, 2)
        self.assertEqual(len(decomposition), 3)

        # If the player can play combos, they can play any card combination of the same suit.
        small_cardset = CardSet({'A♥': 1, 'K♥': 2, 'Q♥': 2, 'A♠': 1})
        combo_moves = small_cardset.get_leading_moves(TrumpSuit.DJ, 2, include_combos=True)
        self.assertEqual(len(combo_moves), 18) # 4 singles + 2 pairs + 1 tractor + 3 length-2 combos + 5 length-3 combos + 2 length-4 combos + 1 length-5 combo 

        combo_moves = self.cardset_multiple_small_tractors.get_leading_moves(TrumpSuit.DJ, 2, include_combos=True)
        self.assertEqual(len(combo_moves), 728) # Hard to tell if this is right

        combo_lead_move = MoveType.Combo(CardSet({'A♦': 2, 'K♦': 1}))
        matching_moves = self.cardset_all_suits.get_matching_moves(combo_lead_move, TrumpSuit.DJ, 3)
        self.assertEqual(len(matching_moves), 2) # Must play the pair of 2s, then choose either 9♦ or 10♦

    def test_cardset_compare_single(self):
        # Single card can beat another single card if the rank is higher, or if it's a trump card but the other one is not
        single_k_move = MoveType.Single('K♦')
        single_ace = CardSet({'A♦': 1})
        single_queen = CardSet({'Q♦': 1})
        single_jack_heart = CardSet({'J♥': 1})
        single_k_heart = CardSet({'K♥': 1})
        
        # Same suit cards. Compare rank only.
        self.assertTrue(all([single_ace.is_bigger_than(single_k_move, suit, 2) for suit in (TrumpSuit.CLUB, TrumpSuit.DIAMOND, TrumpSuit.DJ, TrumpSuit.HEART, TrumpSuit.SPADE)]))
        self.assertFalse(all([single_queen.is_bigger_than(single_k_move, suit, 2) for suit in (TrumpSuit.CLUB, TrumpSuit.DIAMOND, TrumpSuit.DJ, TrumpSuit.HEART, TrumpSuit.SPADE)]))

        # Trump against non-trump (ruff)
        self.assertTrue(single_jack_heart.is_bigger_than(single_k_move, TrumpSuit.HEART, 2))

        # Non-trump against non-trump of different suit
        self.assertFalse(single_jack_heart.is_bigger_than(single_k_move, TrumpSuit.CLUB, 2))

        # Dominant rank is larger than other non-joker trump cards
        self.assertTrue(single_queen.is_bigger_than(single_k_move, TrumpSuit.DIAMOND, 12))

        # Dominant card should be larger than other dominant-rank cards
        self.assertTrue(single_k_heart.is_bigger_than(single_k_move, TrumpSuit.HEART, 13))
        self.assertFalse(single_k_heart.is_bigger_than(single_k_move, TrumpSuit.XJ, 13))
        self.assertFalse(single_k_heart.is_bigger_than(single_k_move, TrumpSuit.XJ, 12))
    
    def test_cardset_compare_pair(self):
        pair_ace_diamond = CardSet({'A♦': 2})
        pair_king_heart = CardSet({'K♥': 2})
        pair_queen_diamond = CardSet({'Q♦': 2})
        pair_jokers = CardSet({'XJ': 2})
        non_pair_jokers = CardSet({'XJ': 1, 'DJ': 1})

        target_move = MoveType.Pair('K♦')

        self.assertTrue(all([pair_ace_diamond.is_bigger_than(target_move, suit, 2) for suit in (TrumpSuit.CLUB, TrumpSuit.DIAMOND, TrumpSuit.DJ, TrumpSuit.HEART, TrumpSuit.SPADE)]))
        self.assertFalse(all([pair_king_heart.is_bigger_than(target_move, suit, 2) for suit in (TrumpSuit.CLUB, TrumpSuit.DIAMOND, TrumpSuit.DJ, TrumpSuit.SPADE)]))
        self.assertTrue(pair_king_heart.is_bigger_than(target_move, TrumpSuit.HEART, 2))
        self.assertTrue(pair_king_heart.is_bigger_than(target_move, TrumpSuit.HEART, 13))
        self.assertFalse(pair_queen_diamond.is_bigger_than(target_move, TrumpSuit.SPADE, 2))

        # Two different jokers cannot beat any pair
        self.assertFalse(non_pair_jokers.is_bigger_than(target_move, TrumpSuit.DJ, 2))

        # Pair jokers beat any non-joker pair in any suit and any rank
        self.assertTrue(all([pair_jokers.is_bigger_than(target_move, suit, 13) for suit in (TrumpSuit.CLUB, TrumpSuit.DIAMOND, TrumpSuit.DJ, TrumpSuit.HEART, TrumpSuit.SPADE)]))

    def test_cardset_compare_tractor(self):
        target_tractor = CardSet({ '6♦': 2, '8♦': 2 }) # Assume 7 is dominant rank
        target_move = MoveType.Combo(target_tractor) # Could use MoveType.Tractor(...) also

        option1 = CardSet({ '7♥': 2, '7♦': 2 })
        option2 = CardSet({ 'XJ': 2, '7♥': 2 })
        option3 = CardSet({ '10♦': 2, 'J♦': 2 })
        
        # If either ♥ or ♦ is trump suit, then option1 forms a tractor
        self.assertTrue(all([option1.is_bigger_than(target_move, suit, 7) for suit in (TrumpSuit.DIAMOND, TrumpSuit.HEART)]))

        # Otherwise, 7♦7♦ 7♥7♥ is not a tractor
        self.assertFalse(all([option1.is_bigger_than(target_move, suit, 7) for suit in (TrumpSuit.DJ, TrumpSuit.SPADE, TrumpSuit.CLUB)]))

        # Option2 is a tractor if the trump suit is ♥ or NT 
        self.assertTrue(all([option2.is_bigger_than(target_move, suit, 7) for suit in (TrumpSuit.HEART, TrumpSuit.XJ)]))
        self.assertFalse(all([option2.is_bigger_than(target_move, suit, 7) for suit in (TrumpSuit.CLUB, TrumpSuit.SPADE, TrumpSuit.DIAMOND)]))

        # Option3 is always a tractor given dominant rank = 7, and beats the target tractor
        self.assertTrue(all([option3.is_bigger_than(target_move, suit, 7) for suit in (TrumpSuit.CLUB, TrumpSuit.DIAMOND, TrumpSuit.HEART, TrumpSuit.SPADE, TrumpSuit.DJ)]))

    def test_cardset_compare_combo(self):
        target1 = CardSet({'A♦': 1, 'K♦': 2})
        target2 = CardSet({'A♦': 1, 'K♦': 1, '8♦': 2, '9♦': 2})
        
        option1 = CardSet({'3♥': 2, '4♥': 1})
        option2 = CardSet({'3♥': 2, '5♥': 2, '7♥': 2})

        # Since 3♦ is a dominant card pair, it's larger than a pair of K♦. The single card doesn't matter in this case.
        self.assertTrue(option1.is_bigger_than(MoveType.Combo(target1), TrumpSuit.HEART, 3))
        self.assertTrue(option1.is_bigger_than(MoveType.Combo(target1), TrumpSuit.HEART, 4))
        self.assertFalse(option1.is_bigger_than(MoveType.Combo(target1), TrumpSuit.DIAMOND, 3))
        self.assertFalse(option1.is_bigger_than(MoveType.Combo(target1), TrumpSuit.DJ, 2))

        # The player beats the target if they have a tractor and all cards are trump cards.
        self.assertTrue(option2.is_bigger_than(MoveType.Combo(target2), TrumpSuit.HEART, 6))
        self.assertFalse(option2.is_bigger_than(MoveType.Combo(target2), TrumpSuit.HEART, 2))
        self.assertFalse(option2.is_bigger_than(MoveType.Combo(target2), TrumpSuit.DJ, 6))

    def test_same_suit_combo_needs_higher_rank_at_every_component(self):
        # Regression: a low pair + low single in the same suit used to
        # "beat" a high pair + high single because the combo branch of
        # is_bigger_than short-circuited on matching shape without any
        # rank comparison. Concretely: W leads A♥ + 8♥8♥, N follows
        # 4♥4♥ + 3♥ — N was incorrectly awarded the trick.
        target = MoveType.Combo(CardSet({'A♥': 1, '8♥': 2}))
        follower = CardSet({'4♥': 2, '3♥': 1})
        # Hearts non-trump (dom 2, trump = spades): same-suit follow with
        # every component strictly lower — must NOT beat.
        self.assertIsNone(follower.is_bigger_than(target, TrumpSuit.SPADE, 2))
        # Hearts IS trump: still same-suit follow, still every component
        # lower — must NOT beat.
        self.assertIsNone(follower.is_bigger_than(target, TrumpSuit.HEART, 5))

        # Sanity: same-shape same-suit with every component strictly
        # higher does beat.
        target_b = MoveType.Combo(CardSet({'K♦': 1, '4♦': 2}))
        beater = CardSet({'A♦': 1, '5♦': 2})
        self.assertIsNotNone(beater.is_bigger_than(target_b, TrumpSuit.SPADE, 2))
        # Same-shape but ONE component fails to outrank → must NOT beat.
        near_miss = CardSet({'A♦': 1, '3♦': 2})   # A > K ✓ but 3 < 4 ✗
        self.assertIsNone(near_miss.is_bigger_than(target_b, TrumpSuit.SPADE, 2))

    def test_trump_ruff_of_nontrump_combo_needs_matching_shape(self):
        # All-trump follow with matching shape beats a non-trump combo
        # (no rank comparison — trump auto-dominates).
        target = MoveType.Combo(CardSet({'A♥': 1, '8♥': 2}))  # non-trump when trump=spades
        # Follower plays a trump pair + trump single, matching shape.
        ruff = CardSet({'6♠': 2, '3♠': 1})
        self.assertIsNotNone(ruff.is_bigger_than(target, TrumpSuit.SPADE, 2))
        # Same-total-cards but wrong shape (three singles, no pair) → does not beat.
        wrong_shape = CardSet({'6♠': 1, '3♠': 1, '4♠': 1})
        self.assertIsNone(wrong_shape.is_bigger_than(target, TrumpSuit.SPADE, 2))
        # Mixed trump + non-trump-off-suit follow can never beat.
        mixed = CardSet({'6♠': 2, '3♣': 1})  # 3♣ is non-trump, non-target-suit
        self.assertIsNone(mixed.is_bigger_than(target, TrumpSuit.SPADE, 2))

    def test_trump_vs_trump_combo_needs_higher_rank(self):
        # When the leader's combo IS trump, a trump follow must strictly
        # outrank every component — trump auto-beat doesn't apply.
        target = MoveType.Combo(CardSet({'A♥': 1, '8♥': 2}))  # trump when trump=hearts
        # Lower trump pair + lower trump single: does not beat.
        low = CardSet({'4♥': 2, '3♥': 1})
        self.assertIsNone(low.is_bigger_than(target, TrumpSuit.HEART, 2))
        # Higher trump pair + higher trump single: beats.
        high = CardSet({'K♥': 2, 'J♥': 1})  # pair-K > pair-8 ✓, single-J < single-A ✗
        self.assertIsNone(high.is_bigger_than(target, TrumpSuit.HEART, 2))
        # Jokers beat non-joker trump — pair of XJs and the DJ single tops any trump combo shape.
        top = CardSet({'XJ': 2, 'DJ': 1})
        self.assertIsNotNone(top.is_bigger_than(target, TrumpSuit.HEART, 2))

    def test_round_winner_trick_outcomes(self):
        # Exhaustive coverage over lead type × winner type. Each block is
        # (players, trump_suit, dominant_rank, expected_winner_index,
        # short_note). Lets us regression-test every category of trick
        # resolution end-to-end through round_winner in one place.
        cases = [
            # ---- Single leads ----
            # Leader wins: nobody higher / trump.
            ([CardSet({'K♦': 1}), CardSet({'9♦': 1}), CardSet({'3♣': 1}), CardSet({'4♥': 1})],
             TrumpSuit.SPADE, 2, 0, 'single leader wins vs lower same-suit and off-suit'),
            # Same-suit follower beats with higher rank.
            ([CardSet({'K♦': 1}), CardSet({'A♦': 1}), CardSet({'3♣': 1}), CardSet({'4♥': 1})],
             TrumpSuit.SPADE, 2, 1, 'single: same-suit ace beats king'),
            # Trump ruff.
            ([CardSet({'K♦': 1}), CardSet({'9♦': 1}), CardSet({'3♠': 1}), CardSet({'4♥': 1})],
             TrumpSuit.SPADE, 2, 2, 'single: trump ruff beats non-trump lead'),
            # Two trump ruffs, higher wins.
            ([CardSet({'K♦': 1}), CardSet({'3♠': 1}), CardSet({'A♠': 1}), CardSet({'DJ': 1})],
             TrumpSuit.SPADE, 2, 3, 'single: highest of multiple trumps wins'),
            # Trump lead can't be beat by off-suit.
            ([CardSet({'A♠': 1}), CardSet({'K♦': 1}), CardSet({'K♣': 1}), CardSet({'K♥': 1})],
             TrumpSuit.SPADE, 2, 0, 'trump single lead survives non-trump follows'),

            # ---- Pair leads ----
            ([CardSet({'K♦': 2}), CardSet({'9♦': 2}), CardSet({'3♣': 2}), CardSet({'4♥': 2})],
             TrumpSuit.SPADE, 2, 0, 'pair leader wins vs lower same-suit and off-suit pairs'),
            ([CardSet({'K♦': 2}), CardSet({'A♦': 2}), CardSet({'3♣': 2}), CardSet({'4♥': 2})],
             TrumpSuit.SPADE, 2, 1, 'pair: same-suit higher pair beats'),
            ([CardSet({'K♦': 2}), CardSet({'9♦': 2}), CardSet({'3♠': 2}), CardSet({'4♥': 2})],
             TrumpSuit.SPADE, 2, 2, 'pair: trump pair ruffs non-trump pair'),
            # Trump singles can't ruff a non-trump pair.
            ([CardSet({'K♦': 2}), CardSet({'9♦': 2}),
              CardSet({'3♠': 1, 'A♠': 1}), CardSet({'4♥': 2})],
             TrumpSuit.SPADE, 2, 0, 'pair: two non-pair trumps do NOT beat a pair'),

            # ---- Tractor leads ----
            ([CardSet({'9♥': 2, '10♥': 2}), CardSet({'A♥': 2, 'K♥': 2}),
              CardSet({'6♠': 2, '7♠': 2}), CardSet({'2♠': 2, '2♣': 2})],
             TrumpSuit.SPADE, 2, 3, 'tractor: biggest trump tractor wins'),
            ([CardSet({'9♥': 2, '10♥': 2}), CardSet({'A♥': 2, 'K♥': 2}),
              CardSet({'8♦': 1, '9♦': 1, '2♣': 1, '3♣': 1}),  # not a tractor: singles fill
              CardSet({'4♣': 1, '5♣': 1, '6♣': 1, '7♣': 1})],
             TrumpSuit.SPADE, 2, 1, 'tractor: non-tractor same-suit follows do NOT beat'),

            # ---- Combo leads (pair + single) ----
            # Regression case: same-suit lower must NOT beat.
            ([CardSet({'A♥': 1, '8♥': 2}), CardSet({'4♥': 2, '3♥': 1}),
              CardSet({'6♣': 1, '7♥': 1, 'DJ': 1}),  # mixed fill
              CardSet({'A♦': 1, 'K♥': 1, '6♥': 1})],  # mixed fill
             TrumpSuit.SPADE, 2, 0, 'combo: mixed-suit fills and lower same-suit all fail'),
            # Non-trump combo, all-trump ruff of matching shape wins.
            ([CardSet({'A♦': 1, '8♦': 2}),   # non-trump combo (trump=spades)
              CardSet({'6♦': 1, '7♦': 1, '9♦': 1}),  # non-trump singles: shape mismatch
              CardSet({'3♠': 2, '4♠': 1}),   # all-trump matching shape
              CardSet({'10♦': 1, 'J♦': 2})],  # same-suit HIGHER: pair-J > pair-8, single-10 < single-A — near miss
             TrumpSuit.SPADE, 2, 2, 'combo: only clean trump ruff of matching shape beats'),
            # Two trump ruffs of matching shape, higher rank wins.
            ([CardSet({'A♦': 1, '8♦': 2}),   # non-trump combo
              CardSet({'6♦': 1, '7♦': 1, '9♦': 1}),
              CardSet({'3♠': 2, '4♠': 1}),   # trump ruff
              CardSet({'K♠': 2, 'Q♠': 1})],   # bigger trump ruff
             TrumpSuit.SPADE, 2, 3, 'combo: highest trump ruff wins when two ruff'),

            # ---- Combo leads (pair + pair + single) ----
            # Sanity: leader wins when nobody beats.
            ([CardSet({'A♥': 2, 'K♥': 1, 'Q♥': 2}),
              CardSet({'5♥': 2, '3♥': 1, '7♥': 1, 'J♥': 1}),  # only one pair, mixed
              CardSet({'2♣': 1, '3♣': 1, '4♣': 1, '5♣': 1, '6♣': 1}),  # off-suit
              CardSet({'2♦': 1, '3♦': 1, '4♦': 1, '5♦': 1, '6♦': 1})],  # off-suit
             TrumpSuit.SPADE, 8, 0, 'combo (2 pairs + single): leader keeps when no one matches shape'),
        ]

        for i, (players, trump, dom, expected, note) in enumerate(cases):
            got = CardSet.round_winner(players, trump, dom)
            self.assertEqual(got, expected, f"case #{i} ({note}): expected {expected}, got {got}")

    def test_multi_compare_combo(self):
        # Player0 hands leading position to player2 in an NT game
        player0_cards = CardSet({'10♥': 1})
        player1_cards = CardSet({'A♥': 1}) # beats player0
        player2_cards = CardSet({'2♦': 1}) # Ruff
        player3_cards = CardSet({'4♥': 1}) # follows
        self.assertEqual(CardSet.round_winner([player0_cards, player1_cards, player2_cards, player3_cards], TrumpSuit.XJ, 2), 2)

        # The player with the single largest card wins
        player0_cards = CardSet({ 'A♥': 1, 'K♥': 1 }) # Combo
        player1_cards = CardSet({ '2♠': 1, 'A♠': 1 }) # Ruff
        player2_cards = CardSet({ 'XJ': 1, '5♠': 1 }) # Bigger ruff
        player3_cards = CardSet({ 'Q♥': 1, '6♦': 1 }) # nothing

        # Player 2 has the largest ruff, therefore wins the trick.
        self.assertEqual(CardSet.round_winner([player0_cards, player1_cards, player2_cards, player3_cards], TrumpSuit.SPADE, 2), 2)

        # Player with the largest trump pair wins (given that they play 5 trump cards containing 2 pairs)
        player0_cards = CardSet({ 'A♥': 2, 'K♥': 1, 'Q♥': 2 }) # Combo with 2 pairs and 1 single
        player1_cards = CardSet({ '5♥': 2, '3♥': 1, '7♥': 1, 'J♥': 1 }) # Match suit
        player2_cards = CardSet({ '6♠': 2, '7♠': 2, '2♣': 1 }) # Uses a tractor to ruff the combo
        player3_cards = CardSet({ 'A♠': 2, '5♠': 2, '10♠': 1 }) # Beats player2 because only the largest pair matters here.
        self.assertEqual(CardSet.round_winner([player0_cards, player1_cards, player2_cards, player3_cards], TrumpSuit.SPADE, 2), 3)

        # Player with the largest tractor wins
        player0_cards = CardSet({ '9♥': 2, '10♥': 2 }) # 1 tractor
        player1_cards = CardSet({ 'A♥': 2, 'K♥': 2 }) # Beats player0 in same suit
        player2_cards = CardSet({ '6♠': 2, '7♠': 2 }) # Ruffs using a tractor
        player3_cards = CardSet({ '2♠': 2, '2♣': 2 }) # Ruffs using bigger tractor
        self.assertEqual(CardSet.round_winner([player0_cards, player1_cards, player2_cards, player3_cards], TrumpSuit.SPADE, 2), 3)

        # Example where player0 is the biggest
        player0_cards = CardSet({'Q♥': 2})
        player1_cards = CardSet({'3♥': 2})
        player2_cards = CardSet({ '10♠': 1, 'J♥': 1 }) # player2 escapes 10 points in trump suit
        player3_cards = CardSet({ '5♥': 1, '9♥': 1 })
        self.assertEqual(CardSet.round_winner([player0_cards, player1_cards, player2_cards, player3_cards], TrumpSuit.SPADE, 2), 0)

    def test_tensor_conversion(self):
        t1 = self.cardset_simple.tensor
        self.assertEqual(self.cardset_simple, CardSet.from_tensor(t1))

        t2 = self.cardset_all_suits.tensor
        self.assertEqual(self.cardset_all_suits, CardSet.from_tensor(t2))
    
    def test_multiplier(self):
        base1 = MoveType.Combo(CardSet({ 'DJ': 1 }))
        base2 = MoveType.Combo(CardSet({ 'A♥': 1, 'K♥': 1 }))
        self.assertEqual(base1.get_multiplier(TrumpSuit.DJ, 2), 2)
        self.assertEqual(base2.get_multiplier(TrumpSuit.CLUB, 2), 2)

        double1 = MoveType.Combo(CardSet({ 'A♥': 2, 'K♥': 1 }))
        double2 = MoveType.Combo(CardSet({ '2♥': 2, '2♣': 2 }))
        self.assertEqual(double1.get_multiplier(TrumpSuit.CLUB, 2), 4)
        self.assertEqual(double2.get_multiplier(TrumpSuit.DJ, 2), 4) # Not a tractor
        self.assertEqual(double2.get_multiplier(TrumpSuit.CLUB, 2), 16) # Tractor

        tractor1 = MoveType.Combo(CardSet({ 'A♥': 1, '8♥': 2, '9♥': 2, '10♥': 2 }))
        self.assertEqual(tractor1.get_multiplier(TrumpSuit.HEART, 2), 64)

    def test_legal_combo(self):
        leading_move = MoveType.Combo(CardSet({'A♣': 1, 'Q♣': 2}))
        player1 = CardSet({'K♣': 2, '10♣': 1, '4♣': 1})
        player2 = CardSet({'J♣': 2, 'DJ': 1 })
        player3 = CardSet({'A♣': 1, '9♣': 2})

        self.assertEqual(CardSet.is_legal_combo(leading_move, [player1, player2, player3], TrumpSuit.HEART, 2), (False, CardSet({'Q♣': 2})))
        self.assertEqual(CardSet.is_legal_combo(leading_move, [player2, player3], TrumpSuit.DIAMOND, 2), (True, None))
        self.assertEqual(CardSet.is_legal_combo(leading_move, [player2], TrumpSuit.CLUB, 2), (False, CardSet({'A♣': 1})))
        self.assertEqual(CardSet.is_legal_combo(leading_move, [player1, player2], TrumpSuit.CLUB, 4), (False, CardSet({'A♣': 1})))

        leading_move = MoveType.Combo(CardSet({'K♣': 1, '6♣': 2, '7♣': 2}))
        player1 = CardSet({'A♣': 1})
        player2 = CardSet({'8♣': 2, '10♣': 2, 'K♣': 1})
        player3 = CardSet({'DJ': 2, 'XJ': 2, '2♣': 1})

        self.assertEqual(CardSet.is_legal_combo(leading_move, [player1], TrumpSuit.DIAMOND, 2), (False, CardSet({'K♣': 1})))
        self.assertEqual(CardSet.is_legal_combo(leading_move, [player2, player3], TrumpSuit.HEART, 2), (True, None))
        self.assertEqual(CardSet.is_legal_combo(leading_move, [player2], TrumpSuit.HEART, 9), (False, CardSet({'6♣': 2, '7♣': 2})))
        self.assertEqual(CardSet.is_legal_combo(leading_move, [player3], TrumpSuit.CLUB, 2), (False, CardSet({'K♣': 1})))

    def test_trump_suit_tensor(self):
        self.assertEqual(TrumpSuit.from_tensor(TrumpSuit.DIAMOND.tensor), TrumpSuit.DIAMOND)
        self.assertEqual(TrumpSuit.from_tensor(TrumpSuit.CLUB.tensor), TrumpSuit.CLUB)
        self.assertEqual(TrumpSuit.from_tensor(TrumpSuit.HEART.tensor), TrumpSuit.HEART)
        self.assertEqual(TrumpSuit.from_tensor(TrumpSuit.SPADE.tensor), TrumpSuit.SPADE)
        self.assertEqual(TrumpSuit.from_tensor(TrumpSuit.XJ.tensor), TrumpSuit.XJ)
        self.assertEqual(TrumpSuit.from_tensor(TrumpSuit.DJ.tensor), TrumpSuit.DJ)
    
    def test_dynamic_tensor(self):
        full_deck, order = CardSet.new_deck()

        for suit in [TrumpSuit.DIAMOND, TrumpSuit.CLUB, TrumpSuit.XJ, TrumpSuit.DJ]:
            for rank in range(2, 15):
                self.assertEqual(CardSet.from_dynamic_tensor(full_deck.get_dynamic_tensor(suit, rank), suit, rank), full_deck)
        
        half_deck = CardSet()
        for card in order[:28]:
            half_deck.add_card(card)
        
        for suit in [TrumpSuit.HEART, TrumpSuit.SPADE, TrumpSuit.XJ, TrumpSuit.DJ]:
            for rank in range(2, 15):
                self.assertEqual(CardSet.from_dynamic_tensor(half_deck.get_dynamic_tensor(suit, rank), suit, rank), half_deck)
    
    def test_random_hand(self):
        random.seed(10)
        full_deck, order = CardSet.new_deck()
        cardset = CardSet()
        for card in order[:25]:
            cardset.add_card(card)
        print(cardset)

if __name__ == '__main__':
    unittest.main()