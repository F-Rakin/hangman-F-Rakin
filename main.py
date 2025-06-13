# F-Rakin_text_based_hangman

# Import required modules
import customtkinter as ctk                    # CustomTkinter for modern GUI
import tkinter.messagebox as msgbox            # Message boxes for win/loss alerts
import requests                                 # To make API calls to Datamuse
import random                                   # To randomly choose category or word

# Constants for game settings
MAX_ATTEMPTS = 6                                # Total allowed wrong guesses
CATEGORIES = ['fruits', 'animals', 'colors', 'sports', 'foods']   # Categories for word selection

# App configuration setup
ctk.set_appearance_mode("dark")                 # Set dark mode for modern look
ctk.set_default_color_theme("blue")            # Set accent color theme

# Create the main application window
app = ctk.CTk()
app.title("Hangman")
app.geometry("600x500")                         # Set window size

# Initialize global variables for game state
selected_word = ""                              # Word chosen from the API
display_word = []                               # List to show current word progress with dashes
guessed_letters = set()                         # Set of letters already guessed
attempts = 0                                     # Count of incorrect guesses
correct_letters = set()                         # Set of correct letters in the selected word

# Function to make API call and fetch a word from Datamuse based on chosen category
def get_word_from_datamuse(category):
    url = f"https://api.datamuse.com/words?rel_trg={category}&max=100"
    response = requests.get(url)
    if response.status_code != 200:
        msgbox.showerror("API Error", f"Failed to fetch word. Status: {response.status_code}")
        return None
    words = [w['word'] for w in response.json() if w['word'].isalpha() and len(w['word']) > 2]  # Filter out symbols and short words
    return random.choice(words).upper() if words else None

# Start a new game and reset all game variables
def new_game():
    global selected_word, display_word, guessed_letters, attempts, correct_letters
    guessed_letters.clear()                    # Clear previous guesses
    attempts = 0                                # Reset attempts
    category = random.choice(CATEGORIES)        # Choose random category
    selected_word = get_word_from_datamuse(category)  # Get word from API
    if not selected_word:
        return
    correct_letters = set(selected_word)        # Break chosen word into set of letters
    display_word = ['_' for _ in selected_word] # Add dash for each letter in display word
    category_label.configure(text=f"Category: {category.title()}")
    update_display()                            # Show word and guessed letters
    for btn in letter_buttons:
        btn.configure(state="normal")           # Enable all letter buttons
    draw_hangman()                              # Reset drawing

# Handle when a letter is guessed by the player
def guess_letter(letter, btn):
    global attempts
    btn.configure(state="disabled")             # Disable the clicked button
    guessed_letters.add(letter)                 # Add to guessed letters
    if letter in correct_letters:               # If correct guess
        for i, ltr in enumerate(selected_word):
            if ltr == letter:
                display_word[i] = letter        # Replace dash with the guessed letter
    else:
        attempts += 1                           # Increase wrong attempt count
    update_display()
    draw_hangman()                              # Update drawing based on attempts
    check_game_status()                         # Check if player won or lost

# Update word display and guessed letter tracker
def update_display():
    word_display.configure(text=" ".join(display_word))
    guessed_display.configure(text="Guessed: " + ", ".join(sorted(guessed_letters)))

# Check if player has won or lost the game
def check_game_status():
    if set(display_word) == correct_letters:
        msgbox.showinfo("You Won!", f"Congratulations! The word was: {selected_word}")
        disable_letters()                        # End game and disable buttons
    elif attempts >= MAX_ATTEMPTS:
        msgbox.showinfo("Game Over", f"You lost! The word was: {selected_word}")
        disable_letters()

# Disable all letter buttons when game ends
def disable_letters():
    for btn in letter_buttons:
        btn.configure(state="disabled")

# Draw the hangman figure step-by-step
def draw_hangman():
    canvas.delete("all")                         # Clear previous drawing
    base_x, base_y = 40, 250
    # Scaffold structure
    canvas.create_line(base_x, base_y, base_x + 100, base_y, width=8)           # Base
    canvas.create_line(base_x + 50, base_y, base_x + 50, base_y - 200, width=8) # Vertical pole
    canvas.create_line(base_x + 50, base_y - 200, base_x + 110, base_y - 200, width=8) # Top bar
    canvas.create_line(base_x + 110, base_y - 200, base_x + 110, base_y - 170, width=8) # Rope

    # Draw hangman body parts based on attempts
    if attempts > 0:
        canvas.create_oval(100, 80, 120, 100, width=2, outline="red")         # Head
    if attempts > 1:
        canvas.create_line(110, 100, 110, 150, width=2, fill="red")           # Body
    if attempts > 2:
        canvas.create_line(110, 120, 90, 140, width=2, fill="red")            # Left Arm
    if attempts > 3:
        canvas.create_line(110, 120, 130, 140, width=2, fill="red")           # Right Arm
    if attempts > 4:
        canvas.create_line(110, 150, 90, 180, width=2, fill="red")            # Left Leg
    if attempts > 5:
        canvas.create_line(110, 150, 130, 180, width=2, fill="red")           # Right Leg

# ---------------------- GUI Layout ----------------------

# Create left frame to hold scaffold and word display
left_frame = ctk.CTkFrame(app, width=250)
left_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

# Create right frame to hold letter buttons
right_frame = ctk.CTkFrame(app)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Label to show chosen category
category_label = ctk.CTkLabel(left_frame, text="Category: ", font=("Arial", 14))
category_label.pack(pady=(0, 10))

# Canvas to draw the hangman
canvas = ctk.CTkCanvas(left_frame, width=200, height=250, bg="white")
canvas.pack()

# Display the word with dashes and revealed letters
word_display = ctk.CTkLabel(left_frame, text="_ _ _ _ _", font=("Courier", 20))
word_display.pack(pady=10)

# Display guessed letters
guessed_display = ctk.CTkLabel(left_frame, text="Guessed: ", font=("Arial", 12))
guessed_display.pack()

# Frame to hold letter buttons in a grid
letters_frame = ctk.CTkFrame(right_frame)
letters_frame.pack(pady=20)

letter_buttons = []
# Loop through all letters and create a button for each
for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    btn = ctk.CTkButton(letters_frame, text=letter, width=40, command=lambda l=letter, b=None: guess_letter(l, b))
    letter_buttons.append(btn)

# Properly assign command to each button
for i, btn in enumerate(letter_buttons):
    btn.configure(command=lambda b=btn, l=btn.cget("text"): guess_letter(l, b))
    btn.grid(row=i//6, column=i%6, padx=5, pady=5)

# Frame for bottom control buttons
bottom_frame = ctk.CTkFrame(app)
bottom_frame.pack(side="bottom", pady=10)

# Button to restart game
restart_btn = ctk.CTkButton(bottom_frame, text="Restart", command=new_game)
restart_btn.pack(side="left", padx=10)

# Button to quit the game
quit_btn = ctk.CTkButton(bottom_frame, text="Quit", command=app.destroy)
quit_btn.pack(side="left", padx=10)

# Start the first game
new_game()
app.mainloop()
