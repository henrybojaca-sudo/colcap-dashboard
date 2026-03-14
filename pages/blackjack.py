"""
Blackjack Game — Play against the dealer
"""

import streamlit as st
import random

st.set_page_config(
    page_title="Blackjack",
    page_icon="🃏",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────────
# CARD LOGIC
# ─────────────────────────────────────────────────────────────────

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

CARD_VALUES = {
    "A": 11, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10,
}


def new_deck():
    deck = [{"rank": r, "suit": s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def hand_value(hand):
    total = sum(CARD_VALUES[c["rank"]] for c in hand)
    aces = sum(1 for c in hand if c["rank"] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def card_str(card):
    suit_color = "red" if card["suit"] in ["♥", "♦"] else "black"
    return f'<span style="font-size:2rem; border:2px solid #ccc; border-radius:8px; padding:4px 10px; background:#fff; color:{suit_color}; display:inline-block; margin:3px;">{card["rank"]}{card["suit"]}</span>'


def render_hand(hand, hide_first=False):
    cards_html = ""
    for i, card in enumerate(hand):
        if hide_first and i == 0:
            cards_html += '<span style="font-size:2rem; border:2px solid #ccc; border-radius:8px; padding:4px 10px; background:#2c3e50; color:#2c3e50; display:inline-block; margin:3px;">🂠</span>'
        else:
            cards_html += card_str(card)
    st.markdown(cards_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "deck": new_deck(),
        "player_hand": [],
        "dealer_hand": [],
        "chips": 100,
        "bet": 0,
        "phase": "betting",   # betting | playing | dealer | result
        "message": "",
        "wins": 0,
        "losses": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def deal_card(hand):
    if len(st.session_state.deck) < 10:
        st.session_state.deck = new_deck()
    hand.append(st.session_state.deck.pop())


def start_round():
    st.session_state.player_hand = []
    st.session_state.dealer_hand = []
    for _ in range(2):
        deal_card(st.session_state.player_hand)
        deal_card(st.session_state.dealer_hand)
    st.session_state.phase = "playing"
    st.session_state.message = ""
    # Check natural blackjack
    if hand_value(st.session_state.player_hand) == 21:
        resolve_round("blackjack")


def resolve_round(outcome):
    bet = st.session_state.bet
    if outcome == "blackjack":
        st.session_state.chips += int(bet * 1.5)
        st.session_state.message = "🃏 Blackjack! You win 1.5x your bet!"
        st.session_state.wins += 1
    elif outcome == "win":
        st.session_state.chips += bet
        st.session_state.message = "✅ You win!"
        st.session_state.wins += 1
    elif outcome == "push":
        st.session_state.message = "🤝 Push — bet returned."
    elif outcome == "lose":
        st.session_state.chips -= bet
        st.session_state.message = "❌ Dealer wins."
        st.session_state.losses += 1
    elif outcome == "bust":
        st.session_state.chips -= bet
        st.session_state.message = "💥 Bust! You lose."
        st.session_state.losses += 1
    st.session_state.phase = "result"
    st.session_state.bet = 0


def dealer_play():
    while hand_value(st.session_state.dealer_hand) < 17:
        deal_card(st.session_state.dealer_hand)
    player_val = hand_value(st.session_state.player_hand)
    dealer_val = hand_value(st.session_state.dealer_hand)
    if dealer_val > 21 or player_val > dealer_val:
        resolve_round("win")
    elif player_val == dealer_val:
        resolve_round("push")
    else:
        resolve_round("lose")


# ─────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────

init_state()

st.title("🃏 Blackjack")
st.markdown("---")

# Chips display
col_chips, col_record = st.columns(2)
col_chips.metric("Chips", f"💰 {st.session_state.chips}")
col_record.metric("W / L", f"{st.session_state.wins} / {st.session_state.losses}")

st.markdown("---")

# ── BETTING PHASE ─────────────────────────────────────────────────
if st.session_state.phase == "betting":
    st.subheader("Place your bet")
    if st.session_state.chips <= 0:
        st.error("You're out of chips! Starting over...")
        st.session_state.chips = 100
        st.rerun()

    max_bet = st.session_state.chips
    bet = st.slider("Bet amount", min_value=1, max_value=max_bet, value=min(10, max_bet), step=1)

    if st.button("Deal", type="primary", use_container_width=True):
        st.session_state.bet = bet
        start_round()
        st.rerun()

# ── PLAYING PHASE ─────────────────────────────────────────────────
elif st.session_state.phase == "playing":
    st.subheader(f"Dealer's hand")
    render_hand(st.session_state.dealer_hand, hide_first=True)
    visible_dealer = hand_value(st.session_state.dealer_hand[1:])
    st.caption(f"Showing: {visible_dealer}")

    st.markdown("---")
    player_val = hand_value(st.session_state.player_hand)
    st.subheader(f"Your hand — {player_val}")
    render_hand(st.session_state.player_hand)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    if col1.button("Hit", type="primary", use_container_width=True):
        deal_card(st.session_state.player_hand)
        if hand_value(st.session_state.player_hand) > 21:
            resolve_round("bust")
        st.rerun()

    if col2.button("Stand", use_container_width=True):
        dealer_play()
        st.rerun()

    # Double down (only on first two cards, if enough chips)
    can_double = (
        len(st.session_state.player_hand) == 2
        and st.session_state.chips >= st.session_state.bet * 2
    )
    if col3.button("Double Down", disabled=not can_double, use_container_width=True):
        st.session_state.bet *= 2
        deal_card(st.session_state.player_hand)
        if hand_value(st.session_state.player_hand) > 21:
            resolve_round("bust")
        else:
            dealer_play()
        st.rerun()

# ── RESULT PHASE ──────────────────────────────────────────────────
elif st.session_state.phase in ("result", "dealer"):
    player_val = hand_value(st.session_state.player_hand)
    dealer_val = hand_value(st.session_state.dealer_hand)

    st.subheader(f"Dealer's hand — {dealer_val}")
    render_hand(st.session_state.dealer_hand)

    st.markdown("---")
    st.subheader(f"Your hand — {player_val}")
    render_hand(st.session_state.player_hand)

    st.markdown("---")
    if st.session_state.message:
        if "win" in st.session_state.message.lower() or "blackjack" in st.session_state.message.lower():
            st.success(st.session_state.message)
        elif "bust" in st.session_state.message.lower() or "dealer wins" in st.session_state.message.lower():
            st.error(st.session_state.message)
        else:
            st.info(st.session_state.message)

    st.metric("Chips remaining", f"💰 {st.session_state.chips}")

    if st.button("Play Again", type="primary", use_container_width=True):
        st.session_state.phase = "betting"
        st.rerun()

    if st.button("Reset Game", use_container_width=True):
        for key in ["deck", "player_hand", "dealer_hand", "chips", "bet",
                    "phase", "message", "wins", "losses"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
