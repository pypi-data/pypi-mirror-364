import random # Imports the random package

# Starting game text
print("Welcome to the luck room")
UserWallet = 1000 # Assigns the users money
CoinFace = ("heads", "tails") # Assigns coin faces
CardDeck = ("1 of hearts", "2 of hearts", "3 of heats", "4 of hearts", "5 of hearts", "6 of hearts", "7 of hearts", "8 of hearts", "9 of hearts", "10 of hearts", "jack of hearts", "queen of hearts", "king of hearts", "1 of diamonds", "2 of diamonds", "3 of diamonds", "4 of diamonds", "5 of diamonds", "6 of diamonds", "7 of diamonds", "8 of diamonds", "9 of diamonds", "10 of diamonds", "jack of diamonds", "queen of diamonds", "king of diamonds", "1 of clubs", "2 of clubs", "3 of clubs", "4 of clubs", "5 of clubs", "6 of clubs", "7 of clubs", "8 of clubs", "9 of clubs", "10 of clubs", "jack of clubs", "queen of clubs", "king of clubs", "1 of spades", "2 of spades", "3 of spades", "4 of spades", "5 of spades", "6 of spades", "7 of spades", "8 of spades", "9 of spades", "10 of spades", "jack of spades", "queen of spades", "king of spades")



# Dice Roll Function
def DiceRoll(): # Creates DiceRoll function
    print("\nYou have picked dice roll.")
    while True: # Betting Amount module
        global UserWallet 
        UserBet = input(f"\nPick how much you want to bet! You have ${UserWallet:.2f}.\n").strip() # Input so the user can set bet amount
        if UserBet.isdigit(): # Makes sure the input is a digit
            if float(UserBet) > UserWallet: # Makes sure they have the money 
                print("\nYou are betting more money that you have, try again.")
                continue
            else:
                UserWallet -= float(UserBet) # Takes away betting amount
                break
        else:
            print("\nYour bet amount was not a proper number.")

    print(f"\nYou have picked to bet ${float(UserBet):.2f}") # Announces bet
    while True: # Picking Number module
        UserPick = input("Pick a number between 1 and 6\n") # Input so the user can set dice number
        if UserPick.isdigit(): # Checks if digit
            if int(UserPick) in range(1, 7): # Checks if it is from 1-6
                DiceRollResult = random.randrange(1, 7) # Generates random number between 1 - 6
                break
            else:
                print("\nYou have picked a number outside 1 and 6.")

        else:
            print("\nValue invalid")

    # Outcome (win or lose)
    print("\nThe dice roll was: " + str(DiceRollResult)) # Announces dice roll
    if int(UserPick) == int(DiceRollResult): # Checks if user was correct
        UserBet = float(UserBet) * 6 # Times betting by 6
        UserWallet += float(UserBet) # Add betting time to wallet
        print("Congratulations, You have correctly picked the dice number!\n")
    else: 
        print("Bad luck, you guessed wrong!\n")

    print(f"You know have: $ {UserWallet:.2f}") # Anounces new walltet ammount
    
    if UserWallet == 0: # Check for money
        print("You have lost all your money and have been kicked out of the luck room")
        exit() # Ends code if the user has ran out of money
    else: 
        print("\nWould you like to play again?")
        while True: # Continue game module
            UserContinue = input("\nTo play again, type: 'again'\nTo select a new game, type: 'home'\n").strip().lower() # Input optin for again or home
            if UserContinue == "again":
                return "again" # returns again if picked again
            elif UserContinue == "home":
                return "home" # returns home if picked home
            else:
                print("\nThere is no option for: " + UserContinue) # retry if user picked something else



# Coin Flip Function
def CoinFlip():
    print("\nYou have chosen coin flip")
    while True: # Betting Amount module
        global UserWallet 
        UserBet = input(f"\nPick how much you want to bet! You have ${UserWallet:.2f}.\n")
        if UserBet.isdigit():
            if float(UserBet) > UserWallet:
                print("\nYou are betting more money that you have, try again.")
                continue
            else:
                UserWallet -= float(UserBet)
                break
        else:
            print("\nYour bet amount was not a proper number.")

    print(f"\nYou have placed a bet ${float(UserBet):.2f}")
    while True: # Coin Toss module
        UserPick = input("\nPick which face: 'heads' or 'tails'\n").strip().lower()
        if type(UserPick) == str:
            if UserPick == "heads" or UserPick == "tails" or UserPick == 1 or UserPick == 2:
                CounFlipResult = random.choice(CoinFace)
                break
            else:
                print("\nYou didn't choose a valid word.")

        else:
            print("\nValue invalid")

    # Outcome (win or lose)
    print("\nThe coin flip was: " + str(CounFlipResult))
    if UserPick == CounFlipResult:
        UserBet = float(UserBet) * 2
        UserWallet += float(UserBet)
        print("Congratulations, You have correctly picked the correct coin face!\n")
    else: 
        print("Bad luck, you guessed wrong!\n")

    print(f"You know have: ${UserWallet:.2f}")

    if UserWallet == 0: # Check for money (exit)
        print("You have lost all your money and have been kicked out of the luck room")
        exit()
    else: # Continue game modle
        print("\nWould you like to play again?")
        while True:
            UserContinue = input("\nTo play again, type: 'again'\nTo select a new game, type: 'home'\n").strip().lower()
            if UserContinue == "again":
                return "again"
            elif UserContinue == "home":
                return "home"
            else:
                print("\nThere is no option for: " + UserContinue)


# Wheel sping function
def WheelSpin():
    print("\nYou have chosen wheel spin")
    while True: # Betting Amount module
        global UserWallet 
        UserBet = input(f"\nPick how much you want to bet! You have ${UserWallet:.2f}.\n")
        if UserBet.isdigit():
            if float(UserBet) > UserWallet:
                print("\nYou are betting more money that you have, try again.")
                continue
            else:
                UserWallet -= float(UserBet)
                break
        else:
            print("\nYour bet amount was not a proper number.")

    print(f"\nYou have picked to bet ${float(UserBet):.2f}")
    while True: # Picking Number module
        UserPick = input("Pick a number between 1 and 100\n") 
        if UserPick.isdigit(): 
            if int(UserPick) in range(1, 100):
                WheelSpinResult = random.randrange(1, 101) 
                break
            else:
                print("\nYou have picked a number outside 1 and 100.")

        else:
            print("\nValue invalid")

# Outcome (win or lose)
    print("\nThe number was: " + str(WheelSpinResult))
    if int(UserPick) == int(WheelSpinResult):
        UserBet = float(UserBet) * 100
        UserWallet += float(UserBet)
        print("Congratulations, You have correctly picked the correct number!\n")
    else: 
        print("Bad luck, you guessed wrong!\n")

    print(f"You know have: ${UserWallet:.2f}")

    if UserWallet == 0: # Check for money (exit)
        print("You have lost all your money and have been kicked out of the luck room")
        exit()
    else: # Continue game modle
        print("\nWould you like to play again?")
        while True:
            UserContinue = input("\nTo play again, type: 'again'\nTo select a new game, type: 'home'\n").strip().lower()
            if UserContinue == "again":
                return "again"
            elif UserContinue == "home":
                return "home"
            else:
                print("\nThere is no option for: " + UserContinue)



# Card Pick Functiom
def CardPick():
    print("\nYou have chosen card pick")
    while True: # Betting Amount module
        global UserWallet 
        UserBet = input(f"\nPick how much you want to bet! You have ${UserWallet:.2f}.\n")
        if UserBet.isdigit():
            if float(UserBet) > UserWallet:
                print("\nYou are betting more money that you have, try again.")
                continue
            else:
                UserWallet -= float(UserBet)
                break
        else:
            print("\nYour bet amount was not a proper number.")

    print(f"\nYou have picked to bet ${float(UserBet):.2f}")
    while True: # Picking Card module
        UserPick = input("Pick a playing card\nSuits:hearts, spades, diamonds, clubs\nValue:1, 2, 3, 4, 5, 6, 7, 8, 9, 10, jack, queen, king\n(example: 3 of spades)\n")
        if UserPick in CardDeck:
            CardDeckResult = random.choice(CardDeck) 
            break
        else:
            print("\nYou have picked a invalid value.")

# Outcome (win or lose)
    print("\nThe number was: " + str(CardDeckResult))
    if UserPick == CardDeckResult:
        UserBet = float(UserBet) * 52
        UserWallet += float(UserBet)
        print("Congratulations, You have correctly picked the correct card!\n")
    else: 
        print("Bad luck, you guessed wrong!\n")

    print(f"You know have: ${UserWallet:.2f}")

    if UserWallet == 0: # Check for money (exit)
        print("You have lost all your money and have been kicked out of the luck room")
        exit()
    else: # Continue game modle
        print("\nWould you like to play again?")
        while True:
            UserContinue = input("\nTo play again, type: 'again'\nTo select a new game, type: 'home'\n").strip().lower()
            if UserContinue == "again":
                return "again"
            elif UserContinue == "home":
                return "home"
            else:
                print("\nThere is no option for: " + UserContinue)



# Game Pick Function
def GamePick():
        global MenuOption
        MenuOption = input("\nChoose what you would like to do:\n1) Dice roll (1/6 - 6x)\n2) Coin flip (1/2 - 2x)\n3) Wheel spin (1/100 100x)\n4) Card pick (1/52 52x)\n5) Wallet (View money)\n6) Quit (Leave the luck room)\n").strip().lower()


def main():
    while True: # Main loop
        GamePick() # Uses game function
        if MenuOption == "dice roll" or MenuOption == "1": # Checks if user picks either dice roll or 1
            while True: # Loops
                result = DiceRoll() # Uses dice roll function and output as result variable 
                if result == "again": # Checks if varaible is again
                    continue # runs loop again
                elif result == "home": 
                    break # Stops this loop and goes back to the other loop
                elif result == "quit":
                    exit() # ends code 


        elif MenuOption == "coin flip" or MenuOption == "2":
            while True:
                result = CoinFlip()
                if result == "again":
                    continue
                elif result == "home":
                    break


        elif MenuOption == "wheel spin" or MenuOption == "3":
            while True:
                result = WheelSpin()
                if result == "again":
                    continue
                elif result == "home":
                    break

        elif MenuOption == "card pick" or MenuOption == "4":
            while True:
                result = CardPick()
                if result == "again":
                    continue
                elif result == "home":
                    break
        
        elif MenuOption == "wallet" or MenuOption == "5":
            print(f"\nYou have ${UserWallet:.2f}")

        elif MenuOption == "quit" or MenuOption == "6":
            print("You have decided to leave the luck room, sadly, you got mugged. Luckily you made it out alive!")
            exit()

        elif MenuOption in ("duckyboi_xd", "duckydk_xd", "duckydk-xd", "duckydk"):
            print("The creator of this game appreciates you playing!")
        else:
            print("\nInvalid option")

if __name__ == "__main__":
    main() # Runs main function