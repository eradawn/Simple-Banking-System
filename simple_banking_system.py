import random
import sys
import sqlite3
from sqlite3.dbapi2 import Cursor


class Login(object):
    def __init__(self):
        self.card_number = None
        self.PIN = None

    def menu_start(self):
        print("\n1. Create Account\n2. Log into account\n0. Exit")

    def second_menu(self):
        print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")

    def generate_number(self):
        self.card_number = "400000{}".format("%0.10d" % random.randint(0, 9999999999))
        card_number_list = list(self.card_number)
        num_list = []
        for i in card_number_list:
            i = int(i)
            num_list.append(i)
        del num_list[-1]
        num_list[::2] = [x*2 for x in num_list[::2]]
        num_list = [x - 9 if x > 9 else x for x in num_list]
        list_sum = sum(num_list)
        if list_sum % 10 != 0:
            sum_str = str(list_sum)
            sum_num2 = sum_str[-1]
            sum_num2 = int(sum_num2)
            x = 10 - sum_num2
            num_list.append(x)
        else:
            num_list.append(0)
        self.card_number = list(self.card_number)
        del self.card_number[-1]
        self.card_number.append(str(num_list[-1]))
        self.card_number = ''.join(self.card_number)

    def choices(self):
        conn = sqlite3.connect('card.s3db')
        cur: Cursor = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
        conn.commit()
        choice = int(input())
        while choice != 0:
            if choice == 1:
                self.generate_number()
                self.PIN = "%0.4d" % random.randint(0, 9999)
                cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (self.card_number, self.PIN))
                conn.commit()
                print("\nYour card has been created\nYour card number:\n{}\nYour card PIN:\n{}".format(self.card_number, self.PIN))
                self.menu_start()
                choice = int(input())
            elif choice == 2:
                log_in1 = str(input("Enter your card number: "))
                log_in2 = str(input("Enter your PIN: "))
                cur.execute("SELECT number, pin FROM card WHERE number = ? AND pin = ?", (log_in1, log_in2))
                data = cur.fetchall()
                conn.commit()
                if len(data) != 1:
                    print("\nWrong card number or PIN!")
                    self.menu_start()
                    choice = int(input())
                else:
                    print("\nYou have successfully logged in!")
                    cur.execute('SELECT balance FROM card WHERE number = ?', (log_in1,))
                    conn.commit()
                    balance = cur.fetchone()
                    balance = list(balance)
                    balance = balance[0]
                    self.second_menu()
                    choice2 = int(input())
                    while choice2 != 0:
                        if choice2 == 1:
                            print("\n" + str(balance))
                            self.second_menu()
                            choice2 = int(input())
                        elif choice2 == 5:
                            self.menu_start()
                            choice = int(input())
                            break
                        elif choice2 == 2:
                            print("\nEnter income:")
                            income = int(input())
                            balance += income
                            cur.execute("UPDATE card SET balance = ? WHERE number = ?", (balance, log_in1))
                            conn.commit()
                            print('Income was added!')
                            self.second_menu()
                            choice2 = int(input())
                        elif choice2 == 3:
                            receiver_input = str(input("\nTransfer\nEnter card number:\n"))
                            cur.execute("SELECT number FROM card WHERE number = ?", (receiver_input,))
                            receiver = cur.fetchone()
                            if receiver == None:
                                receiver_input_list = list(receiver_input)
                                receiver_num_list = []
                                for i in receiver_input_list:
                                    i = int(i)
                                    receiver_num_list.append(i)
                                last_digit = receiver_num_list[-1]
                                del receiver_num_list[-1]
                                receiver_num_list[::2] = [x*2 for x in receiver_num_list[::2]]
                                receiver_num_list = [x - 9 if x > 9 else x for x in receiver_num_list]
                                receiver_num_list.append(last_digit)
                                receiver_list_sum = sum(receiver_num_list)
                                if receiver_list_sum % 10 != 0:
                                    print("Probably you made a mistake in the card number. Please try again!")
                                    self.second_menu()
                                    choice2 = int(input())
                                else:
                                    print("Such a card does not exist.")
                                    self.second_menu()
                                    choice2 = int(input())
                            else:
                                if receiver_input == log_in1:
                                    print("You can't transfer money to the same account!")
                                    self.second_menu()
                                    choice2 = int(input())
                                else:
                                    transfer_amount = int(input("Enter how much money you want to transfer:\n"))
                                    if transfer_amount <= balance:
                                        balance -= transfer_amount
                                        cur.execute('SELECT balance FROM card WHERE number = ?', (receiver_input,))
                                        receiver_balance = cur.fetchone()
                                        receiver_balance = list(receiver_balance)
                                        receiver_balance = receiver_balance[0]
                                        receiver_balance += transfer_amount
                                        cur.execute("UPDATE card SET balance = ? WHERE number = ?", ((receiver_balance), receiver_input))
                                        conn.commit()
                                        cur.execute("UPDATE card SET balance = ? WHERE number = ?", ((balance), log_in1))
                                        conn.commit()
                                        print("Success!")
                                        self.second_menu()
                                        choice2 = int(input())
                                    else:
                                        print("Not enough money!")
                                        self.second_menu()
                                        choice2 = int(input())
                        elif choice2 == 4:
                            cur.execute('DELETE FROM card WHERE number = ?', (log_in1,))
                            conn.commit()
                            print("The account has been closed!")
                            self.menu_start()
                            choice = int(input())
                            break
                    if choice2 == 0:
                        print("\nBye!")
                        sys.exit()
        if choice == 0:
            print("\nBye!")
            sys.exit()


log1 = Login()
log1.menu_start()
log1.choices()
