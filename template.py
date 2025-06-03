# F-Rakin_hangman_game

import requests
import random

def get_random_word(category):
    url = f"https://api.datamuse.com/words?topics={category}&max=1000"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch words from API.")
        return None

    words = response.json()
    # Filter out words with spaces or non-alphabetic characters
    valid_words = [word['word'] for word in words if word['word'].isalpha()]

    if not valid_words:
        print(f"No words found for category '{category}'.")
        return None

    return random.choice(valid_words).lower()

def hangman_game():
    categories = ['animal', 'food', 'color', 'sport', 'fruit']
    category = random.choice(categories)
    selected_word = get_random_word(category)

    if not selected_word:
        return

    guessed_letters = set()
    correct_letters = set(selected_word)
    display_word = ['_' for _ in selected_word]
    max_attempts = 6
    attempts = 0

    print(f"\nCategory: {category.capitalize()}")
    print("Guess the word:")
    print(" ".join(display_word))

    while attempts < max_attempts and set(display_word) != correct_letters:
        guess = input("Enter a letter: ").lower()

        if not guess.isalpha() or len(guess) != 1:
            print("Please enter a single alphabetical character.")
            continue

        if guess in guessed_letters:
            print("You already guessed that letter.")
            continue

        guessed_letters.add(guess)

        if guess in correct_letters:
            for i, letter in enumerate(selected_word):
                if letter == guess:
                    display_word[i] = guess
            print("Correct!")
        else:
            attempts += 1
            print(f"Wrong. {max_attempts - attempts} attempts remaining.")

        print("Word: " + " ".join(display_word))
        print("Guessed letters: " + ", ".join(sorted(guessed_letters)))

    if set(display_word) == correct_letters:
        print(f"\n🎉 You won! The word was: {selected_word}")
    else:
        print(f"\n💀 Game over. The word was: {selected_word}")

# Run the game
if __name__ == "__main__":
    hangman_game()
