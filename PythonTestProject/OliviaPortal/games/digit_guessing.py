# Import required module
import random 

# Returns list of digits 
# of a number

def get_digits(num):
    return [int(i) for i in str(num)]
    

# Returns True if number has 
# no duplicate digits 
# otherwise False      
def no_duplicates(num):
    num_li = get_digits(num)
    if len(num_li) == len(set(num_li)):
        return True
    else:
        return False


# Generates a 4 digit number 
# with no repeated digits    
def generate_num():
    while True:
        num = random.randint(1000,9999)
        if no_duplicates(num):
            return num


# Returns common digits with exact 
# matches (bulls) and the common 
# digits in wrong position (cows)
def num_of_bulls_cows(num,guess):
    bull_cow = [0,0]
    num_li = get_digits(num)
    guess_li = get_digits(guess)
    
    for i,j in zip(num_li,guess_li):
        
        # common digit present
        if j in num_li:
        
            # common digit exact match
            if j == i:
                bull_cow[0] += 1
            
            # common digit match but in wrong position
            else:
                bull_cow[1] += 1
                
    return bull_cow

def play() -> None:
# Secret Code
    num = generate_num()
    while True:
        try:
            tries = int(input("Enter number of tries: "))
            break
        except ValueError:
            print("Please enter a valid number.")

    # Play game until correct guess
    # or till no tries left
    while tries > 0:
        try:
             guess = int(input("Enter your guess: "))
        except ValueError:
            print("Please enter a valid 4-digit number.")
            continue

        if not no_duplicates(guess):
            print("Number should not have repeated digits. Try again.")
            continue
        if guess < 1000 or guess > 9999:
            print("Enter 4 digit number only. Try again.")
            continue

        bull_cow = num_of_bulls_cows(num,guess)
        print(f"{bull_cow[0]} bulls, {bull_cow[1]} cows")
        tries -=1

        if bull_cow[0] == 4:
            print("You guessed right!")
            break
    else:
        print(f"You ran out of tries. Number was {num}")