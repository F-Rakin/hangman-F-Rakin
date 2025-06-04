# F-Rakin_text_based_hangman

# Import necessary modules for the game
import requests
import random

def get_word_from_datamuse(category: str) -> str:
    """
    Does an API call to Datamuse usign a specific category to get a random word associated
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
    valid_words = [word['word'] for word in words if word['word'].isalpha()]

    if not valid_words:
        print(f"⚠️ No usable words found for category '{category}'.")
        return None

    return random.choice(valid_words).lower()

def hangman_game():
    categories = ['fruits', 'animals', 'colors', 'sports', 'foods']
    category = random.choice(categories)
    selected_word = get_word_from_datamuse(category)

    if not selected_word:
        print("❌ Could not fetch a word. Try again.")
        return

    guessed_letters = set()
    correct_letters = set(selected_word)
    display_word = ['_' for _ in selected_word]
    max_attempts = 6
    attempts = 0

    print(f"\n📚 Category: {category.capitalize()}")
    print("🎮 Let's play Hangman!")
    print("Word: " + " ".join(display_word))

    while attempts < max_attempts and set(display_word) != correct_letters:
        guess = input("🔤 Enter a letter: ").lower()

        if not guess.isalpha() or len(guess) != 1:
            print("⚠️ Please enter a single alphabetical character.")
            continue

        if guess in guessed_letters:
            print("ℹ️ You already guessed that letter.")
            continue

        guessed_letters.add(guess)

        if guess in correct_letters:
            for i, letter in enumerate(selected_word):
                if letter == guess:
                    display_word[i] = guess
            print("✅ Correct!")
        else:
            attempts += 1
            print(f"❌ Wrong. {max_attempts - attempts} attempts remaining.")

        print("\nWord: " + " ".join(display_word))
        print("Guessed letters: " + ", ".join(sorted(guessed_letters)))

    if set(display_word) == correct_letters:
        print(f"\n🎉 You won! The word was: {selected_word}")
    else:
        print(f"\n💀 Game over. The word was: {selected_word}")

# Run the game
if __name__ == "__main__":
    hangman_game()

