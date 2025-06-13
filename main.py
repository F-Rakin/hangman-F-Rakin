# F-Rakin_text_based_hangman

# Import necessary modules for the game
import requests
import random

def get_word_from_datamuse(category: str) -> str:
    """
    Does an API call to Datamuse usign a specific category to get a random associated word
    """
    url = f"https://api.datamuse.com/words?rel_trg={category}&max=100"
    response = requests.get(url)

    # If the API call returns an error display message
    if response.status_code != 200:
        print(f"❌ Error: Status code {response.status_code}")
        return None

    # Format response into JSON 
    words = response.json()

    # Filter to keep only alphabetic words (remove phrases or hyphenated terms)
    # Make List of valid words
    valid_words = [word['word'] for word in words if word['word'].isalpha()]        # Use isalpha function to check for alphabets

    # If no valid word is returned from the category in API call
    if not valid_words:
        print(f"⚠️ No usable words found for category '{category}'.")
        return None

    # Return a randomly chose word from the list
    return random.choice(valid_words).upper()

def hangman_game() -> str:
    """
    This function takes user input and displays progress for the game
    """

    # Randomly choose a category from the possible options
    categories = ['fruits', 'animals', 'colors', 'sports', 'foods']
    category = random.choice(categories)

    # Call function to get a word from the API
    selected_word = get_word_from_datamuse(category)

    # Display error message if a word could not be found
    if not selected_word:
        print("❌ Could not fetch a word. Try again.")
        return

    # Use a set instead of list to not allow duplicate inputs
    guessed_letters = set()

    # Seperate all letters in the chosen word as seperate objects in the set
    correct_letters = set(selected_word)

    # Display a dash for every letter in the chosen word
    display_word = ['_' for _ in selected_word]

    # Available attempts
    max_attempts = 6
    attempts = 0

    # Create a simple UI
    print(f"\n📚 Category: {category.capitalize()}")
    print("🎮 Let's play Hangman!")
    print("Word: " + " ".join(display_word))

    # Loop for guessing letters
    while attempts < max_attempts and set(display_word) != correct_letters:     # Attempts are remaining and all correct letters are not guessed
        guess = input("🔤 Enter a letter: ").upper()

        # If a non-alphabet or more than 1 letter is inputted
        if not guess.isalpha() or len(guess) != 1:

            # Display error message
            print("⚠️ Please enter a single alphabetical character.")
            continue

        # If user has already guessed the letter before
        if guess in guessed_letters:
            print("ℹ️ You already guessed that letter.")
            continue

        # Add guess to guessed_letters set
        guessed_letters.add(guess)

        # If guessed letter is in the chosen word
        if guess in correct_letters:

            # Loop through letters in chosen word
            for i, letter in enumerate(selected_word):

                # Replace dash as the letter if the guess is correct
                if letter == guess:
                    display_word[i] = guess
            print("✅ Correct!")

        # If wrong letter is guessed, add 1 to attempts
        else:
            attempts += 1
            print(f"❌ Wrong. {max_attempts - attempts} attempts remaining.")

        # Display current progress
        print("\nWord: " + " ".join(display_word))
        print("Guessed letters: " + ", ".join(sorted(guessed_letters)))

    # If all letters are guessed display final message
    if set(display_word) == correct_letters:
        print(f"\n🎉 You won! The word was: {selected_word}")

    # If all attempts are over
    else:
        print(f"\n💀 Game over. The word was: {selected_word}")

# Run the game
if __name__ == "__main__":
    hangman_game()

