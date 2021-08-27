from random import randrange
import sqlite3


class Account:
    def __init__(self):
        self.card_number = luhn("400000" + str(randrange(100000000, 1000000000)))
        self.pin = str(randrange(1000, 10000))
        self.balance = 0

    def get_card_info(self):
        return "Your card number:\n{}\nYour card PIN:\n{}".format(self.card_number, self.pin)

    def get_balance(self):
        return f"Balance: {self.balance}"


def luhn(number):
    list_numbers = [int(n) for n in number]
    odd_numbers = list_numbers[0::2]
    odd_numbers = [2 * n - 9 if n > 4 else 2 * n for n in odd_numbers]
    even_numbers = list_numbers[1::2]

    return number + str((10 - (sum(odd_numbers) + sum(even_numbers)) % 10) % 10)


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS card (
               id INTEGER,
               number TEXT,
               pin TEXT,
               balance INTEGER DEFAULT 0);
''')
conn.commit()

while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    opt = int(input())
    print()

    if opt == 1:
        cur.execute("SELECT COUNT(*) FROM card;")
        account_id = cur.fetchone()[0]
        new_account = Account()

        cur.execute("INSERT INTO card VALUES (?, ?, ?, ?);",
                    [account_id, new_account.card_number, new_account.pin, new_account.balance])
        conn.commit()
        print("Your card has been created")
        print(new_account.get_card_info())
    elif opt == 2:
        card_number = input("Enter your card number:")
        pin = input("Enter your PIN:")

        cur.execute("SELECT number, pin, balance FROM card WHERE number = ? AND pin = ?;",
                    [card_number, pin])
        account = cur.fetchone()
        if account is None:
            print("\nWrong card number or PIN!\n")
        else:
            print("\nYou have successfully logged in!")
            while True:
                print()
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")

                opt = int(input())

                if opt == 1:
                    print("\nBalance:", account[2])

                elif opt == 2:
                    income = int(input("Enter income: "))
                    income += account[2]
                    cur.execute('''UPDATE card
                                   SET balance = ?
                                   WHERE number = ?;''', [income, account[0]])
                    conn.commit()

                    cur.execute("SELECT number, pin, balance FROM card WHERE number = ? AND pin = ?;",
                                [account[0], pin])
                    account = cur.fetchone()
                    print("Income was added!")

                elif opt == 3:
                    print("Transfer")
                    card_number = input("Enter your card number:")
                    cur.execute("SELECT COUNT(*) FROM card WHERE number = ?;", [card_number])
                    is_exist = cur.fetchone()[0]

                    if card_number != luhn(card_number[:15]):
                        print("Probably you made a mistake in the card number. Please try again!")
                        continue
                    elif is_exist == 0:
                        print("Such a card does not exist.")
                        continue
                    elif card_number == account[0]:
                        print("You can't transfer money to the same account!")
                        continue

                    money = int(input("Enter how much money you want to transfer:"))
                    if account[2] < money:
                        print("Not enough money!")
                        continue

                    cur.execute("SELECT balance FROM card WHERE number = ?;", [card_number])

                    balance = cur.fetchone()[0]
                    balance += money

                    cur.execute('''UPDATE card
                                   SET balance = ?
                                   WHERE number = ?;''', [balance, card_number])
                    conn.commit()

                    balance = account[2] - money
                    cur.execute('''UPDATE card
                                   SET balance = ?
                                   WHERE number = ?;''', [balance, account[0]])
                    conn.commit()

                    print("Success!")

                elif opt == 4:
                    cur.execute("DELETE FROM card WHERE number = ?;", [account[0]])
                    conn.commit()
                    print("\nThe account has been closed!\n")
                    break

                elif opt == 5:
                    print("\nYou have successfully logged out!\n")
                    break

                else:
                    conn.close()
                    print("Bye!")
                    exit(0)

    else:
        print("Bye!")
        break
conn.close()