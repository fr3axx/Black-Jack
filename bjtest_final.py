import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    def __str__(self):
        return f"{self.rank['rank']} de {self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        suits = ["picas", "tréboles", "corazones", "diamantes"]
        ranks = [
                {"rank": "A", "value": 11},
                {"rank": "2", "value": 2},
                {"rank": "3", "value": 3},
                {"rank": "4", "value": 4},
                {"rank": "5", "value": 5},
                {"rank": "6", "value": 6},
                {"rank": "7", "value": 7},
                {"rank": "8", "value": 8},
                {"rank": "9", "value": 9},
                {"rank": "10", "value": 10},
                {"rank": "J", "value": 10},
                {"rank": "Q", "value": 10},
                {"rank": "K", "value": 10},
            ]
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        
    def shuffle(self):
        if len(self.cards) > 1:
            random.shuffle(self.cards)
    
    def deal(self, number):
        cards_dealt = []
        for x in range(number):
            if len(self.cards) > 0:
                card = self.cards.pop()
                cards_dealt.append(card)
        return cards_dealt

class Hand:
    def __init__(self, dealer=False):
        self.cards = []
        self.value = 0
        self.dealer = dealer

    def add_card(self, card_list):
        self.cards.extend(card_list)

    def calculate_value(self):
        self.value = 0
        has_ace = False
        ace_count = 0

        for card in self.cards:
            card_value = int(card.rank["value"])
            self.value += card_value
            if card.rank["rank"] == "A":
                has_ace = True
                ace_count += 1

        # Manejar múltiples ases
        while has_ace and self.value > 21 and ace_count > 0:
            self.value -= 10
            ace_count -= 1

    def get_value(self):
        self.calculate_value()
        return self.value

    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def display(self, show_all_dealer_cards=False):
        print(f'''{"Mano del dealer" if self.dealer else "Tu mano"}:''')
        for index, card in enumerate(self.cards):
            if index == 0 and self.dealer \
            and not show_all_dealer_cards and not self.is_blackjack():
                print("oculto")
            else:
                print(card)

        if not self.dealer:
            print("Valor:", self.get_value())
        print()

class GameStats:
    def __init__(self):
        self.total_games = 0
        self.player_wins = 0
        self.dealer_wins = 0
        self.ties = 0
        self.player_blackjacks = 0
        self.dealer_blackjacks = 0
        self.total_winnings = 0

class Game:
    def __init__(self):
        self.stats = GameStats()
        self.player_balance = 0

    def get_initial_balance(self):
        while True:
            try:
                balance = float(input("¿Cuánto dinero quieres tener para jugar? $"))
                if balance > 0:
                    self.player_balance = balance
                    return
                else:
                    print("Por favor, ingresa un monto positivo.")
            except ValueError:
                print("Por favor, ingresa un número válido.")

    def get_bet(self):
        while True:
            try:
                print(f"\nSaldo actual: ${self.player_balance:.2f}")
                bet = float(input("¿Cuánto quieres apostar en esta mano? $"))
                
                if bet <= 0:
                    print("La apuesta debe ser mayor que cero.")
                    continue
                
                if bet > self.player_balance:
                    print("No tienes suficiente saldo para esa apuesta.")
                    
                    # New section to handle insufficient balance
                    print("\n¡Te has quedado sin dinero! Has perdido todo tu saldo.")
                    while True:
                        continue_option = input("¿Quieres añadir más dinero (añadir) o salir del juego (salir)? ").lower()
                        
                        if continue_option in ['añadir', 'a']:
                            # Restart with new initial balance
                            self.get_initial_balance()
                            # Recursively call get_bet to retry betting
                            return self.get_bet()
                        elif continue_option in ['salir', 's']:
                            print("¡Gracias por jugar! Vuelve cuando tengas más suerte.")
                            exit()
                
                return bet
            except ValueError:
                print("Por favor, ingresa un número válido.")

    def calculate_win_probability(self, player_hand, dealer_hand):
        """
        Calcula la probabilidad estimada de ganar basada en las manos actuales
        """
        # Probabilidad básica de ganar
        if player_hand.get_value() > 21:
            return 0  # Seguro pierde si se pasa
        
        if dealer_hand.get_value() > 21:
            return 100  # Seguro gana si dealer se pasa
        
        # Probabilidad basada en valores de las manos
        if player_hand.is_blackjack():
            return 90  # Alta probabilidad con Blackjack
        
        if dealer_hand.is_blackjack():
            return 10  # Baja probabilidad contra Blackjack del dealer
        
        # Cálculo de probabilidad basado en diferencia de valores
        player_value = player_hand.get_value()
        dealer_visible = dealer_hand.cards[1].rank["value"]  # Carta visible del dealer
        
        # Probabilidades simples basadas en comparación de valores
        if player_value > 21:
            return 0
        elif player_value > dealer_visible:
            return 60  # Probabilidad moderada de ganar
        elif player_value < dealer_visible:
            return 40  # Probabilidad moderada de perder
        else:
            return 50  # Empate probable

    def check_winner(self, player_hand, dealer_hand, current_bet=0, game_over=False):
        # Update the game result tracking
        if not game_over:
            if player_hand.get_value() > 21:
                print("Te pasaste. ¡El dealer gana! 😭")
                self.player_balance -= current_bet
                self.stats.total_winnings -= current_bet
                self.stats.dealer_wins += 1
                return True
            elif dealer_hand.get_value() > 21:
                print("El dealer se pasó. ¡Tú ganas! 😀")
                self.player_balance += current_bet
                self.stats.total_winnings += current_bet
                self.stats.player_wins += 1
                return True
            elif dealer_hand.is_blackjack() and player_hand.is_blackjack():
                print("¡Ambos jugadores tienen blackjack! ¡Empate! 😑")
                self.stats.ties += 1
                return True
            elif player_hand.is_blackjack():
                # Blackjack typically pays 1.5x
                winnings = current_bet * 1.5
                print("Tienes blackjack. ¡Tú ganas! 😀")
                self.player_balance += winnings
                self.stats.total_winnings += winnings
                self.stats.player_wins += 1
                self.stats.player_blackjacks += 1
                return True
            elif dealer_hand.is_blackjack():
                print("El dealer tiene blackjack. ¡El dealer gana! 😭")
                self.player_balance -= current_bet
                self.stats.total_winnings -= current_bet
                self.stats.dealer_wins += 1
                self.stats.dealer_blackjacks += 1
                return True
        else:
            self.stats.total_games += 1
            if player_hand.get_value() > dealer_hand.get_value():
                print("¡Tú ganas! 😀")
                self.player_balance += current_bet
                self.stats.total_winnings += current_bet
                self.stats.player_wins += 1
            elif player_hand.get_value() < dealer_hand.get_value():
                print("El dealer gana. 😭")
                self.player_balance -= current_bet
                self.stats.total_winnings -= current_bet
                self.stats.dealer_wins += 1
            else:
                print("¡Empate! 😑")
                self.stats.ties += 1
            return True
        return False

    def print_stats(self):
        print("\n--- ESTADÍSTICAS DEL JUEGO ---")
        print(f"Juegos totales: {self.stats.total_games}")
        print(f"Victorias del jugador: {self.stats.player_wins}")
        print(f"Victorias del dealer: {self.stats.dealer_wins}")
        print(f"Empates: {self.stats.ties}")
        print(f"Blackjacks del jugador: {self.stats.player_blackjacks}")
        print(f"Blackjacks del dealer: {self.stats.dealer_blackjacks}")
        print(f"Ganancias totales: ${self.stats.total_winnings:.2f}")
        print(f"Saldo final: ${self.player_balance:.2f}")

    def play(self):
        # Get initial balance before starting
        self.get_initial_balance()

        playing = True

        while playing:
            # Get number of games to play
            game_number = 0
            games_to_play = 0

            while games_to_play <= 0:
                try:
                    games_to_play = int(input("¿Cuántos juegos quieres jugar? "))
                except:
                    print("Debes ingresar un número.")

            while game_number < games_to_play:
                # Check balance before each game
                if self.player_balance <= 0:
                    print("\n¡Te has quedado sin dinero! Has perdido todo tu saldo.")
                    while True:
                        continue_option = input("¿Quieres añadir más dinero (añadir) o salir del juego (salir)? ").lower()
                        
                        if continue_option in ['añadir', 'a']:
                            # Restart with new initial balance
                            self.get_initial_balance()
                            break
                        elif continue_option in ['salir', 's']:
                            print("¡Gracias por jugar! Vuelve cuando tengas más suerte.")
                            return

                # Get bet for this hand
                current_bet = self.get_bet()

                game_number += 1

                deck = Deck()
                deck.shuffle()

                player_hand = Hand()
                dealer_hand = Hand(dealer=True)

                for i in range(2):
                    player_hand.add_card(deck.deal(1))
                    dealer_hand.add_card(deck.deal(1))

                print()
                print("*" * 30)
                print(f"Juego {game_number} de {games_to_play}")
                print(f"Apuesta actual: ${current_bet:.2f}")
                print("*" * 30)
                player_hand.display()
                dealer_hand.display()

                # Mostrar probabilidad inicial de ganar
                initial_win_prob = self.calculate_win_probability(player_hand, dealer_hand)
                print(f"💡 Probabilidad inicial de ganar: {initial_win_prob}%")

                if self.check_winner(player_hand, dealer_hand, current_bet):
                    continue

                choice = ""
                while player_hand.get_value() < 21 and choice not in ["q", "quedarse"]:
                    choice = input("Por favor elige 'Pedir' o 'Quedarse': ").lower()
                    print()
                    while choice not in ["p", "q", "pedir", "quedarse"]:
                        choice = input("Por favor ingresa 'Pedir' o 'quedarse' (o P/Q) ").lower()
                        print()
                    if choice in ["pedir", "p"]:
                        player_hand.add_card(deck.deal(1))
                        player_hand.display()
                        
                        # Mostrar probabilidad después de pedir carta
                        win_prob = self.calculate_win_probability(player_hand, dealer_hand)
                        print(f"💡 Probabilidad actual de ganar: {win_prob}%")
                
                if self.check_winner(player_hand, dealer_hand, current_bet):
                    continue

                player_hand_value = player_hand.get_value()
                dealer_hand_value = dealer_hand.get_value()

                while dealer_hand_value < 17:
                    dealer_hand.add_card(deck.deal(1))
                    dealer_hand_value = dealer_hand.get_value()

                dealer_hand.display(show_all_dealer_cards=True)

                if self.check_winner(player_hand, dealer_hand, current_bet):
                    continue

                print("Resultados finales")
                print("Tu mano:", player_hand_value)
                print("Mano del dealer:", dealer_hand_value)

                self.check_winner(player_hand, dealer_hand, current_bet, True)

            # Mostrar estadísticas al final de los juegos
            self.print_stats()

            # If player ran out of money during games
            if self.player_balance <= 0:
                print("\n¡Te has quedado sin dinero! Has perdido todo tu saldo.")
                while True:
                    continue_option = input("¿Quieres añadir más dinero (añadir) o salir del juego (salir)? ").lower()
                    
                    if continue_option in ['añadir', 'a']:
                        # Restart with new initial balance
                        self.get_initial_balance()
                        break
                    elif continue_option in ['salir', 's']:
                        playing = False
                        print("¡Gracias por jugar!")
                        break
            else:
                # Normal play again prompt if player still has money
                play_again = input("\n¿Quieres jugar otra vez? (sí/no): ").lower()
                if play_again in ['no', 'n']:
                    playing = False
                    print("¡Gracias por jugar!")

def main():
    g = Game()
    g.play()

if __name__ == "__main__":
    main()