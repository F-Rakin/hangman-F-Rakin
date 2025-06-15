# F-Rakin_text_based_hangman

# ---------------- IMPORTS ----------------
import customtkinter as ctk                    # CustomTkinter for modern GUI
import tkinter.messagebox as msgbox            # Message boxes for win/loss alerts
import requests                                 # To make API calls to Datamuse
import random                                   # To randomly choose category or word
import time                                     # For animation delays
import winsound                                 # For sound effects (Windows only)
import threading                                # For non-blocking timer updates

# ---------------- CONSTANTS ----------------
MAX_ATTEMPTS = 6                                # Total allowed wrong guesses
MAX_HINTS = 3                                   # Maximum number of hint
CATEGORIES = ['fruits', 'animals', 'colors', 'sports', 'foods']   # List of word categories

# ---------------- APP CONFIG ----------------
ctk.set_appearance_mode("dark")                 # Set dark mode for modern look
ctk.set_default_color_theme("blue")             # Set blue accent color

app = ctk.CTk()                                 # Create the main application window
app.title("Py-Hangman")                         # Set window title
app.geometry("700x550")                         # Set fixed window size

# ---------------- GAME STATE VARIABLES ----------------
selected_word = ""                               # Stores the word to guess
display_word = []                                # Displays correctly guessed letters
guessed_letters = set()                         # Tracks letters already guessed
attempts = 0                                     # Counter for incorrect guesses
correct_letters = set()                         # Set of correct letters in the word
hint_count = 0                                   # Counter for hints used
start_time = None                                # Track start time of game
timer_running = False                            # Track whether the timer is running

# ---------------- TIMER FUNCTION ----------------
def update_timer():
    """Continuously updates the timer label in the GUI."""
    global timer_running
    while timer_running:
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        timer_label.configure(text=f"Time: {mins:02d}:{secs:02d}")
        time.sleep(1)


# ---------------- WORD FETCH FUNCTION ----------------
def get_word_from_datamuse(category):
    """
    Fetches a word from the Datamuse API related to the given category.
    """
    url = f"https://api.datamuse.com/words?rel_trg={category}&max=100"  # API endpoint
    response = requests.get(url)                # Send GET request
    if response.status_code != 200:             # Check for successful response
        msgbox.showerror("API Error", f"Failed to fetch word. Status: {response.status_code}")
        return None
    words = [w['word'] for w in response.json() if w['word'].isalpha() and len(w['word']) > 2]  # Filter valid words
    return random.choice(words).upper() if words else None  # Return a random word


# ---------------- START NEW GAME ----------------
def new_game():
    """
    Starts a new game by resetting variables and getting a new word
    """
    global selected_word, display_word, guessed_letters, attempts, correct_letters, start_time, timer_running
    guessed_letters.clear()                     # Reset guessed letters
    attempts = 0                                 # Reset attempts
    hint_count = 0
    category = random.choice(CATEGORIES)         # Pick a random category
    selected_word = get_word_from_datamuse(category)  # Get a word using API

    if not selected_word:
        return
    correct_letters = set(selected_word)         # Store correct letters
    display_word = ['_' for _ in selected_word]  # Fill display with blanks
    category_label.configure(text=f"Category: {category.title()}")  # Update category label
    update_display()                             # Refresh display

    for btn in letter_buttons:
        btn.configure(state="normal")
    hint_btn.configure(state="normal", text=f"Hint ({MAX_HINTS - hint_count} left)")

    draw_hangman()                               # Draw initial state of hangman

    # Start timer
    start_time = time.time()
    timer_running = True
    threading.Thread(target=update_timer, daemon=True).start()


# ---------------- HANDLE GUESSED LETTER ----------------
def guess_letter(letter, btn):
    """
    Handles logic when a letter is guessed, updating state and checking game outcome
    """
    global attempts
    btn.configure(state="disabled")             # Disable clicked button
    guessed_letters.add(letter)                  # Track guessed letter
    if letter in correct_letters:                # If letter is correct
        flash_screen("green")

        for i, ltr in enumerate(selected_word):
            if ltr == letter:
                display_word[i] = letter         # Reveal letter in display

    else:
        flash_screen("red")
        attempts += 1                            # Increment wrong attempt
    update_display()                             # Update word and guessed letters
    draw_hangman()                               # Draw next hangman stage
    check_game_status()                          # Check win/lose condition


# ---------------- HINT FUNCTION ----------------
def use_hint():
    """Reveals one hidden letter from the selected word."""
    global hint_count
    if hint_count >= MAX_HINTS:
        return  # No more hints available

    # Identify indices of unrevealed letters
    remaining_indices = [i for i, l in enumerate(display_word) if l == '_']
    if not remaining_indices:
        return  # All letters already revealed

    # Randomly choose a hidden letter to reveal
    reveal_index = random.choice(remaining_indices)
    reveal_letter = selected_word[reveal_index]
    display_word[reveal_index] = reveal_letter  # Reveal it in the display
    guessed_letters.add(reveal_letter)         # Add to guessed list
    hint_count += 1                            # Increment hint usage

    update_display()       # Refresh GUI display
    draw_hangman()        # Redraw hangman if needed
    check_game_status()   # Check if this causes a win

    # Update hint button text or disable it
    if hint_count >= MAX_HINTS:
        hint_btn.configure(state="disabled", text="No Hints Left")
    else:
        hint_btn.configure(text=f"Hint ({MAX_HINTS - hint_count} left)")


# ---------------- UPDATE DISPLAY ----------------
def update_display():
    """
    Updates the word and guessed letters display on the GUI
    """
    word_display.configure(text=" ".join(display_word))           # Show word progress
    guessed_display.configure(text="Guessed: " + ", ".join(sorted(guessed_letters)))  # Show guessed letters


# ---------------- CHECK GAME STATUS ----------------
def check_game_status():
    """
    Checks whether the player has won or lost the game and handles the result
    """
    if set(display_word) == correct_letters:     # If word guessed fully
        jump_effect()                            # Play jump animation
        winsound.MessageBeep(winsound.MB_ICONASTERISK)  # Win sound
        msgbox.showinfo("🎉 You Won! 🎉", f"Congratulations! 🎊 The word was: {selected_word} 😄")
        timer_running = False
        new_game()                               # Start new game

    elif attempts >= MAX_ATTEMPTS:               # If out of attempts
        winsound.MessageBeep(winsound.MB_ICONHAND)  # Loss sound
        msgbox.showinfo("💀 Game Over", f"You lost! The word was: {selected_word} 😢")
        timer_running = False
        new_game()


# ---------------- JUMP EFFECT FOR 'PY' ----------------
def jump_effect():
    """
    Jumping animation for every guess
    """
    for _ in range(3):
        canvas.move("py", 0, -10)                 # Move up
        canvas.update()
        canvas.after(100)                         # Delay
        canvas.move("py", 0, 10)                  # Move down
        canvas.update()
        canvas.after(100)                         # Delay


# ---------------- SCREEN FLASH EFFECT ----------------
def flash_screen(color):
    """
    Flashes the screen background color briefly to indicate correct (green) or wrong (red) guess
    """
    original_color = "#242424"  # Default dark mode color in CTk
    main_frame.configure(fg_color=color)
    app.update()
    time.sleep(0.15)
    main_frame.configure(fg_color=original_color)
    app.update()


# ---------------- DRAW HANGMAN ----------------
def draw_hangman():
    """
    Draw "Py" the hangman character
    """
    canvas.delete("all")                          # Clear canvas
    base_x, base_y = 40, 250
    canvas.create_line(base_x, base_y, base_x + 100, base_y, width=8)              # Base
    canvas.create_line(base_x + 50, base_y, base_x + 50, base_y - 200, width=8)    # Pole
    canvas.create_line(base_x + 50, base_y - 200, base_x + 110, base_y - 200, width=8)  # Top bar
    canvas.create_line(base_x + 110, base_y - 200, base_x + 110, base_y - 170, width=8) # Rope
    if attempts > 0:
        canvas.create_oval(140, 80, 160, 100, width=2, outline="green", tags="py")    # Head
        canvas.create_text(150, 90, text="Py", font=("Arial", 8), fill="blue", tags="py")  # Name
    if attempts > 1:
        canvas.create_line(150, 100, 150, 150, width=2, fill="green", tags="py")      # Body
    if attempts > 2:
        canvas.create_line(150, 120, 130, 140, width=2, fill="green", tags="py")      # Left arm
    if attempts > 3:
        canvas.create_line(150, 120, 170, 140, width=2, fill="green", tags="py")      # Right arm
    if attempts > 4:
        canvas.create_line(150, 150, 130, 180, width=2, fill="green", tags="py")      # Left leg
    if attempts > 5:
        canvas.create_line(150, 150, 170, 180, width=2, fill="green", tags="py")      # Right leg

# ---------------- GUI LAYOUT ----------------

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)

left_frame = ctk.CTkFrame(main_frame, width=350)      # Frame for left side (drawing and labels)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

right_frame = ctk.CTkFrame(main_frame)                 # Frame for letter buttons
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

category_label = ctk.CTkLabel(left_frame, text="Category: ", font=("Arial", 18))
category_label.pack(pady=(0, 10))                # Label for category

canvas = ctk.CTkCanvas(left_frame, width=250, height=300, bg="white")
canvas.pack()                                    # Drawing canvas

word_display = ctk.CTkLabel(left_frame, text="_ _ _ _ _", font=("Courier", 20))
word_display.pack(pady=10)                       # Display guessed word

guessed_display = ctk.CTkLabel(left_frame, text="Guessed: ", font=("Arial", 14))
guessed_display.pack()                           # Display guessed letters

letters_frame = ctk.CTkFrame(right_frame)        # Frame to hold alphabet buttons
letters_frame.pack(pady=20)

letter_buttons = []
for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    btn = ctk.CTkButton(letters_frame, text=letter, width=40, command=lambda l=letter, b=None: guess_letter(l, b))
    letter_buttons.append(btn)                   # Store button in list

for i, btn in enumerate(letter_buttons):
    btn.configure(command=lambda b=btn, l=btn.cget("text"): guess_letter(l, b))
    btn.grid(row=i//6, column=i%6, padx=5, pady=5)  # Arrange in grid

hint_btn = ctk.CTkButton(left_frame, text=f"Hint ({MAX_HINTS} left)", command=use_hint)
hint_btn.pack(side= "bottom", pady=20)                         # Hint button

timer_label = ctk.CTkLabel(left_frame, text="Time: 00:00", font=("Arial", 18))
timer_label.pack(pady=20)                       # On-Screen Timer 

restart_btn = ctk.CTkButton(right_frame, text="Restart", command=new_game)
restart_btn.pack(side="left", padx=10)           # Restart button

quit_btn = ctk.CTkButton(right_frame, text="Quit", command=app.destroy)
quit_btn.pack(side="right", padx=10)             # Quit button

new_game()                                        # Start the first game
app.mainloop()                                    # Run the application