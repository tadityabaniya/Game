# =============================================================================
#  RAPID BRIDGE CONSTRUCTION — Single-file game application
#  Workflow order: Login → Chatbot → Map → Construction Sim → Performance Report
# =============================================================================

import pygame               # Pygame handles the Login screen and the Construction simulation window
import sys                  # sys.exit() is used to close the app cleanly if a dependency is missing
import customtkinter as ctk # CustomTkinter creates the modern dark-themed chatbot and dashboard windows
import re                   # re (regex) is used to extract numbers from player text input
import os                   # os.path lets us locate nepal_map.png relative to this script's folder
import math                 # math is imported for potential future geometry; not actively used right now
import matplotlib           # matplotlib generates the stacked bar charts in the performance report
matplotlib.use('Agg')       # 'Agg' tells matplotlib to draw to an image file instead of a pop-up window
import matplotlib.pyplot as plt  # plt is the main interface for creating and saving matplotlib figures
from PIL import Image, ImageTk   # Pillow (PIL) loads and resizes nepal_map.png for display in Tkinter


# =============================================================================
#  SECTION 1 — CONSTANTS, COLORS, STYLES
#  Keep initialisation metrics like colours and so on at first.
# =============================================================================

WIDTH, HEIGHT = 800, 600    # The pixel dimensions of every Pygame window in this app
FPS = 60                    # Target frames per second; keeps the animation smooth

DARK_GREY = (43, 43, 43)            # Background colour — mimics the look of asphalt
WHITE = (255, 255, 255)             # Used for borders, text, and active outlines
BLACK = (0, 0, 0)                   # Used for button text and idle-state dot colour
BLUE = (0, 120, 215)                # Signals "Construction Underway" on the map simulation
GREEN = (0, 255, 0)                 # Signals "Project Complete" on the map simulation
RED = (255, 0, 0)                   # Used for error states
YELLOW = (255, 215, 0)              # Construction Yellow — used for the game title text
LINE_COLOR = (127, 140, 141)        # Steel grey — drawn as the supply-route lines on the map
BUTTON_COLOR = (255, 215, 0)        # Default "Start the Game" button colour
BUTTON_HOVER_COLOR = (230, 194, 0)  # Slightly darker yellow when the mouse hovers over the button
INPUT_BOX_COLOR_INACTIVE = (100, 100, 100)  # Text box colour when the player has not clicked it
INPUT_BOX_COLOR_ACTIVE = (200, 200, 200)    # Text box colour when the player has clicked into it

class Style:
    BG_COLOR = "#2b2b2b"           # Asphalt — the main window background colour
    FRAME_BG_COLOR = "#3c3c3c"     # Concrete — slightly lighter background for panels and cards
    ACCENT_COLOR = "#FFD700"       # Construction Yellow — used for buttons and highlighted text
    HOVER_COLOR = "#E6C200"        # Darker yellow shown when the mouse hovers over an accent button
    TEXT_COLOR = "#e9e9ec"         # Primary text colour across all CTk labels
    SUBTEXT_COLOR = "#b3b3b3"      # Greyed-out colour for secondary labels like card titles
    CHAT_USER_BG = "#4a4a4a"       # Background colour of the player's chat bubbles
    CHAT_AI_BG = "#2a2a2a"         # Background colour of Mission Control's chat bubbles
    CHAT_FONT = ("Courier New", 14, "bold")   # Font used inside every chat bubble
    INPUT_FONT = ("Courier New", 13)          # Font used in the chat text-entry field
    BUTTON_FONT = ("Courier New", 14, "bold") # Font used on all CTk buttons


# =============================================================================
#  SECTION 2 — LOGIN PAGE
#  The first thing the player sees. Built entirely with Pygame.
# =============================================================================

class LoginPage:

    def __init__(self):
        pygame.init()                                           # Start all Pygame subsystems (display, fonts, events)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Create the main 800×600 Pygame window
        pygame.display.set_caption("Rapid Bridge Construction")# Set the title shown in the window's title bar
        self.clock = pygame.time.Clock()                       # Clock object used to cap the frame rate at FPS

        self.font_title = pygame.font.SysFont("Courier New", 48, bold=True)  # Large bold font for the game title
        self.font_normal = pygame.font.SysFont("Courier New", 24)            # Regular font for labels and prompts

        self.state = 'LOGIN'   # The login screen is always the first state when the app starts
        self.user_name = ""    # Stores the characters the player types into the name field
        self.input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 40) # Rectangle defining the text input area
        self.input_active = False                                              # Tracks whether the text box is focused
        self.button_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 30, 220, 50) # Rectangle defining the Start button

        self.bg_img = None     # Will hold the loaded background image surface (or None if loading fails)
        current_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory where this script lives
        bg_path = os.path.join(current_dir, "bg_fixed.jpg")      # Build the full path to the background image
        if os.path.exists(bg_path):                              # Only attempt to load if the file actually exists
            try:
                bg = pygame.image.load(bg_path).convert()        # Load the JPEG into a Pygame surface optimised for blitting
                self.bg_img = pygame.transform.scale(bg, (WIDTH, HEIGHT)) # Scale to fill the entire window
            except Exception as e:                               # Catch any image-loading errors (corrupt file, etc.)
                print("Failed to load background:", e)           # Print the error; the game will fall back to a solid grey background

    def run(self):
        while self.state != 'TRANSITION':  # Keep the login screen running until the player clicks Start
            self.handle_events()           # Process all pending mouse clicks and key presses
            self.draw()                    # Render the current frame (background, text box, button)
            self.clock.tick(FPS)           # Sleep just long enough to maintain 60 FPS
            
        pygame.quit()                      # Destroy the Pygame window once the player has transitioned out
        return self.user_name              # Return the player's name so the chatbot can greet them

    def handle_events(self):
        for event in pygame.event.get():       # Iterate over every event that occurred since the last frame
            if event.type == pygame.QUIT:      # The player clicked the window's close (X) button
                pygame.quit()                  # Release all Pygame resources
                sys.exit()                     # Terminate the entire Python process

            if self.state == 'LOGIN':          # Only process input events while on the login screen
                self.handle_login_events(event) # Delegate to the login-specific event handler

    def handle_login_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:              # The player clicked somewhere on the window
            if self.input_box.collidepoint(event.pos):        # Check if the click landed inside the text box
                self.input_active = not self.input_active     # Toggle the text box between focused and unfocused
            else:
                self.input_active = False                     # Clicking outside the box always deactivates it

            if self.button_rect.collidepoint(event.pos):      # Check if the click landed on the "Start the Game" button
                self.start_game()                             # Begin the transition to the chatbot phase

        elif event.type == pygame.KEYDOWN:                    # The player pressed a key on the keyboard
            if self.input_active:                             # Only capture keystrokes when the text box is focused
                if event.key == pygame.K_RETURN:              # Enter key acts the same as clicking the Start button
                    self.start_game()                         # Transition to the next phase
                elif event.key == pygame.K_BACKSPACE:         # Backspace removes the last typed character
                    self.user_name = self.user_name[:-1]      # Slice off the final character from the name string
                else:
                    self.user_name += event.unicode           # Append the typed character (letter, digit, etc.) to the name

    def start_game(self):
        if self.user_name.strip() == "":  # If the player left the name field blank
            self.user_name = "Guest"      # Assign a default name so downstream screens display something meaningful
        self.state = 'TRANSITION'         # Signal the run() loop to exit and hand control to the chatbot

    def draw(self):
        if self.state == 'LOGIN' and self.bg_img:                  # If a valid background image was loaded
            self.screen.blit(self.bg_img, (0, 0))                  # Paint it across the entire window starting at the top-left corner
        else:
            self.screen.fill(DARK_GREY)                            # Otherwise fill the window with a solid dark grey

        if self.state == 'LOGIN':                                  # Draw the login UI elements only while on the login screen
            self.draw_login()                                      # Call the helper that renders the title, text box, and button
            
        pygame.display.flip()                                      # Swap the back buffer to the screen so the player sees the newly drawn frame

    def draw_login(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Create a transparent surface the same size as the window
        overlay.fill((0, 0, 0, 170))                               # Fill it with semi-transparent black (alpha 170/255) to darken the background
        self.screen.blit(overlay, (0, 0))                          # Draw the dark overlay on top of the background image

        title_surface = self.font_title.render('Rapid Bridge Construction', True, YELLOW) # Render the game title in yellow
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4)) # Centre it horizontally, position at 1/4 of the window height
        self.screen.blit(title_surface, title_rect)                # Draw the title text onto the screen

        prompt_surface = self.font_normal.render("Enter your name:", True, WHITE) # Render the instruction label in white
        self.screen.blit(prompt_surface, (self.input_box.x, self.input_box.y - 35)) # Position it 35 pixels above the text box

        color = INPUT_BOX_COLOR_ACTIVE if self.input_active else INPUT_BOX_COLOR_INACTIVE # Pick the box colour based on focus state
        pygame.draw.rect(self.screen, color, self.input_box)        # Fill the text box with the chosen colour
        pygame.draw.rect(self.screen, WHITE, self.input_box, 2)     # Draw a 2-pixel white border around the text box

        text_surface = self.font_normal.render(self.user_name, True, BLACK) # Render the player's typed name in black
        self.screen.blit(text_surface, (self.input_box.x + 10, self.input_box.y + 8)) # Draw it inside the box with 10 px left padding

        mouse_pos = pygame.mouse.get_pos()                        # Get the current position of the mouse cursor
        if self.button_rect.collidepoint(mouse_pos):              # Check if the cursor is hovering over the Start button
            btn_color = BUTTON_HOVER_COLOR                        # Use the darker hover shade
        else:
            btn_color = BUTTON_COLOR                              # Use the default yellow
            
        pygame.draw.rect(self.screen, btn_color, self.button_rect)     # Fill the button rectangle with the chosen colour
        pygame.draw.rect(self.screen, WHITE, self.button_rect, 2)      # Draw a 2-pixel white border around the button

        btn_text = self.font_normal.render("Start the Game", True, BLACK) # Render the button label in black
        btn_text_rect = btn_text.get_rect(center=self.button_rect.center) # Centre the label inside the button rectangle
        self.screen.blit(btn_text, btn_text_rect)                         # Draw the button label onto the screen
        

# =============================================================================
#  SECTION 3 — CHATBOT (MISSION CONTROLLER)
#  Runs immediately after the login screen closes.
# =============================================================================

class MissionController:

    def __init__(self, player_name="Engineer"):
        self.player_name = player_name  # Name carried over from the login screen for personalised messages
        self.state = "GREETING"         # The conversation always starts at the GREETING stage
        self.chitwan_pct = 0.0          # Percentage of materials to source from Chitawan (0–100)
        self.dang_pct = 0.0             # Percentage of materials to source from Dang (0–100)
        self.kanchanpur_pct = 0.0       # Percentage of materials to source from Kanchanpur (0–100)
        self.game_over = False          # Flag set to True when the mission ends (success or abort)

    def process_input(self, user_text):
        if self.game_over:                                              # If the mission already ended, ignore further input
            return "Mission Control communication link has been terminated." # Inform the player the channel is closed

        user_text = user_text.strip()  # Remove leading/trailing whitespace from the player's message

        if self.state == "GREETING":                                    # First interaction — introduce the scenario
            self.state = "THE_INCIDENT"                                 # Advance to the incident phase
            return (f"A 20m bridge connecting Mahendra Highway at Chitawan has been damaged by flood. " # Describe the emergency
                    f"So, new bridge must be built with optimum efficiency where performance of construction is evaluated using a weighted efficiency model, where 65% importance is given to time and 35% to cost.. "
                    f"Are you willing to take the challenge, {self.player_name}?")

        elif self.state == "THE_INCIDENT":                              # Player is responding to the challenge question
            if self._analyze_intent(user_text):                         # Check if the response is affirmative
                self.state = "MATH_CHALLENGE"                           # Move to the resource allocation phase
                return (
                    "Excellent.You will require 40 tonnes of steel.\n" # Brief the player on material requirements
                    "Construction takes 24 hours if materials are available. Strategically allocate the material percentages from all three locations. Remember that the percentage of material sourced directly dictates the percentage of construction work completed. Your goal is to optimize the distribution to attain maximum efficiency.\n\n"
                    "Locations:\n"
                    "- Chitawan (Local): $1000/ton\n"
                    "- Dang (8hrs away): $980/ton\n"
                    "- Kanchanpur (16hrs away): $960/ton\n\n"
                    "Please use the Map interface & Sliders on the right to set the material procurement percentages. Submissions must equal 100%."
                )
            else:
                self.game_over = True                                   # Player declined — end the mission
                return "Mission aborted. We will look for another commander. Out."

        elif self.state == "MATH_CHALLENGE":                            # Player is on the slider allocation screen
            return "Awaiting slider input... Use the panel on the right to submit your allocation."

        return "Awaiting orders..."                                     # Fallback response for any unhandled state

    def _analyze_intent(self, text):
        text_lower = text.lower()                                       # Convert to lowercase for case-insensitive matching
        positives = ["yes", "sure", "yep", "okay", "ready", "absolutely", "yeah", "willing", "affirmative", "copy"] # Accepted affirmative keywords
        return any(word in text_lower for word in positives)            # Return True if any positive keyword is found in the text


class ChatUI(ctk.CTkFrame):

    def __init__(self, master, process_callback, initial_msg, **kwargs):
        super().__init__(master, fg_color=Style.FRAME_BG_COLOR, corner_radius=15, **kwargs) # Initialise the frame with dark concrete background and rounded corners
        self.process_callback = process_callback                        # Store the callback function that routes messages to MissionController

        self.grid_rowconfigure(0, weight=1)                             # Allow the chat history row to expand vertically
        self.grid_columnconfigure(0, weight=1)                          # Allow the input column to expand horizontally

        self.chat_history = ctk.CTkScrollableFrame(self, fg_color=Style.BG_COLOR, corner_radius=10) # Scrollable container for chat bubbles
        self.chat_history.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="nsew") # Fill the top area of the frame

        self.input_entry = ctk.CTkEntry(self, placeholder_text="Enter transmission...", font=Style.INPUT_FONT, # Text entry field for player messages
                                        height=40, fg_color=Style.BG_COLOR, border_color=Style.ACCENT_COLOR) # Styled with accent-coloured border
        self.input_entry.grid(row=1, column=0, padx=(15, 5), pady=(5, 15), sticky="ew") # Place below the chat history, stretch horizontally
        self.input_entry.bind("<Return>", self._on_send)                # Bind the Enter key to send the message

        self.send_button = ctk.CTkButton(self, text="Transmit", font=Style.BUTTON_FONT, fg_color=Style.ACCENT_COLOR, text_color="black", # Yellow "Transmit" button
                                         hover_color=Style.HOVER_COLOR, command=self._on_send, width=100) # Darkens on hover; calls _on_send when clicked
        self.send_button.grid(row=1, column=1, padx=(5, 15), pady=(5, 15), sticky="e") # Align to the right of the input entry

        self.add_message("Mission Control", initial_msg, is_user=False) # Display the first AI greeting message in the chat

    def _on_send(self, event=None):
        user_text = self.input_entry.get().strip()  # Read and trim the text from the input field
        if not user_text: return                    # Do nothing if the message is empty

        self.input_entry.delete(0, 'end')           # Clear the input field after reading the text

        self.add_message("You", user_text, is_user=True)  # Display the player's message as a right-aligned bubble
        self.update_idletasks()                            # Force Tkinter to redraw immediately so the bubble appears before processing

        ai_response = self.process_callback(user_text)     # Send the text to MissionController and receive the AI response
        self.add_message("Mission Control", ai_response, is_user=False)  # Display the AI response as a left-aligned bubble

        if "Out." in ai_response or "Over and out" in ai_response: # Detect mission-ending phrases in the response
            self.disable_input()                       # Lock the input field and button to prevent further messages
            self.master.after(3000, self.master.quit)  # Schedule the window to close after a 3-second delay

    def add_message(self, sender, text, is_user=True):
        bg = Style.CHAT_USER_BG if is_user else Style.CHAT_AI_BG  # Choose bubble background: dark grey for player, darker for AI

        msg_container = ctk.CTkFrame(self.chat_history, fg_color="transparent")  # Transparent wrapper to control left/right alignment
        msg_container.pack(fill="x", pady=5, padx=10)                            # Stack vertically with spacing between bubbles

        bubble = ctk.CTkFrame(msg_container, fg_color=bg, corner_radius=10)  # The coloured bubble that holds the message text
        bubble.pack(side="right" if is_user else "left")                      # Player bubbles align right, AI bubbles align left

        ctk.CTkLabel(bubble, text=sender, font=("Arial", 11, "bold"), text_color=Style.SUBTEXT_COLOR).pack(anchor="w", padx=10, pady=(5, 0)) # Sender name label at the top of the bubble
        ctk.CTkLabel(bubble, text=text, font=Style.CHAT_FONT, text_color=Style.TEXT_COLOR, justify="left", wraplength=300).pack(padx=10, pady=(0, 10)) # Message body with word wrapping at 300 px

        self.chat_history.update_idletasks()                  # Recalculate scroll area dimensions after adding the new bubble
        self.chat_history._parent_canvas.yview_moveto(1.0)   # Auto-scroll to the bottom so the latest message is always visible

    def disable_input(self):
        self.input_entry.configure(state="disabled")  # Grey out the text entry field so the player cannot type
        self.send_button.configure(state="disabled")  # Grey out the Transmit button so the player cannot click it


class RapidBridgeApp(ctk.CTk):

    def __init__(self, player_name="Commander"):
        super().__init__()                                    # Initialise the root CustomTkinter window
        self.title("Rapid Bridge Construction Tracker")       # Set the window title bar text
        self.geometry("1100x750")                             # Set the default window size to 1100 px wide × 750 px tall
        self.configure(fg_color=Style.BG_COLOR)               # Apply the dark asphalt background colour

        self.controller = MissionController(player_name=player_name)  # Create the chatbot logic controller with the player's name

        self.grid_columnconfigure(0, weight=4)  # Left column (chat panel) gets 40% of available width
        self.grid_columnconfigure(1, weight=6)  # Right column (map + sliders) gets 60% of available width
        self.grid_rowconfigure(0, weight=1)     # Single row expands to fill the full window height

        self.chat_screen = ChatUI(self,                                   # Create the chat panel as a child of this window
                                  process_callback=self.handle_chat_input,  # Route player messages through handle_chat_input
                                  initial_msg=f"Greetings. This is Mission Control. Do you copy?") # First message shown to the player
        self.chat_screen.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20) # Place the chat panel in the left column

        self.setup_right_panel()  # Build the right-side panel containing the map, sliders, and submit button

    def handle_chat_input(self, text):
        resp = self.controller.process_input(text)           # Forward the player's text to MissionController and get the response
        if self.controller.state == "MATH_CHALLENGE":        # If the controller just entered the allocation phase
            self.slide_chitwan.configure(state="normal")     # Enable the Chitawan slider (was disabled until now)
            self.slide_dang.configure(state="normal")        # Enable the Dang slider
            self.slide_kanch.configure(state="normal")       # Enable the Kanchanpur slider
        return resp                                          # Return the AI response string to the ChatUI for display

    def setup_right_panel(self):
        self.right_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG_COLOR, corner_radius=15) # Container for the entire right-side UI
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20) # Place it in the right column, fill available space

        self.right_frame.grid_rowconfigure(0, weight=1)  # Map row expands vertically to fill available space
        self.right_frame.grid_rowconfigure(1, weight=0)  # Sliders row stays at its natural height (no expansion)
        self.right_frame.grid_columnconfigure(0, weight=1) # Single column stretches to fill the panel width

        self.map_panel = ctk.CTkFrame(self.right_frame, fg_color="transparent") # Transparent wrapper frame for the map canvas
        self.map_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) # Fill the top portion of the right panel

        self.map_canvas = ctk.CTkCanvas(self.map_panel, bg=Style.FRAME_BG_COLOR, highlightthickness=0) # Tkinter canvas widget for drawing the Nepal map and location markers

        self.map_canvas.pack(expand=True, fill="both")  # Let the canvas expand to fill the entire map panel

        self.map_img_tk = None                                              # Will hold the PhotoImage reference (must persist to avoid garbage collection)
        current_dir = os.path.dirname(os.path.abspath(__file__))            # Get the directory containing this script
        map_path = os.path.join(current_dir, "nepal_map.png")              # Build the full path to the Nepal map image
        if os.path.exists(map_path):                                        # Only attempt loading if the file exists on disk
            try:
                pil_img = Image.open(map_path)                              # Open the PNG file as a PIL Image object
                pil_img = pil_img.resize((600, 375), Image.Resampling.LANCZOS) # Resize to 600×375 using high-quality Lanczos filter
                self.map_img_tk = ImageTk.PhotoImage(pil_img)              # Convert PIL Image to a Tkinter-compatible PhotoImage
            except Exception as e:
                print("Failed to load map:", e)  # Log the error; the map will render without a background image

        self.map_canvas.bind("<Configure>", self.draw_map)  # Redraw the map whenever the canvas is resized

        self.sliders_frame = ctk.CTkFrame(self.right_frame, fg_color=Style.BG_COLOR, corner_radius=10) # Container frame for the three allocation sliders
        self.sliders_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20) # Place below the map, stretch horizontally
        self.sliders_frame.grid_columnconfigure(1, weight=1)  # Let the slider column (column 1) stretch to fill available width
        slider_font = ("Courier New", 14, "bold") # Monospaced bold font shared by all slider labels

        self._updating_sliders = False # Guard flag to prevent recursive slider updates during programmatic value changes
        self.chitwan_val = ctk.DoubleVar(value=0) # Tkinter variable tracking the Chitawan slider's current percentage (0–100)
        self.dang_val = ctk.DoubleVar(value=0) # Tkinter variable tracking the Dang slider's current percentage (0–100)
        self.kanchanpur_val = ctk.DoubleVar(value=0) # Tkinter variable tracking the Kanchanpur slider's current percentage (0–100)

        self.lbl_chitwan = ctk.CTkLabel(self.sliders_frame, text="Chitawan: 0.0% - 0.0 Tons", font=slider_font, text_color="white") # Label showing Chitawan's current allocation percentage and tonnage
        self.lbl_chitwan.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5)) # Left-align in the first row of the sliders frame
        self.slide_chitwan = ctk.CTkSlider(self.sliders_frame, from_=0, to=100, variable=self.chitwan_val, command=self.update_c, state="disabled", progress_color="white", button_color="white", button_hover_color="white") # White-themed slider for Chitawan; disabled until the chatbot reaches MATH_CHALLENGE
        self.slide_chitwan.grid(row=0, column=1, sticky="we", padx=10, pady=(15, 5)) # Stretch horizontally beside the label

        self.lbl_dang = ctk.CTkLabel(self.sliders_frame, text="Dang: 0.0% - 0.0 Tons", font=slider_font, text_color=Style.TEXT_COLOR) # Label showing Dang's current allocation percentage and tonnage
        self.lbl_dang.grid(row=1, column=0, sticky="w", padx=10, pady=5) # Left-align in the second row
        self.slide_dang = ctk.CTkSlider(self.sliders_frame, from_=0, to=100, variable=self.dang_val, command=self.update_d, state="disabled", button_color="#0078D7", button_hover_color="#005A9E") # Blue-themed slider for Dang; disabled until needed
        self.slide_dang.grid(row=1, column=1, sticky="we", padx=10, pady=5) # Stretch horizontally beside the Dang label

        self.lbl_kanch = ctk.CTkLabel(self.sliders_frame, text="Kanchanpur: 0.0% - 0.0 Tons", font=slider_font, text_color=Style.TEXT_COLOR) # Label showing Kanchanpur's current allocation percentage and tonnage
        self.lbl_kanch.grid(row=2, column=0, sticky="w", padx=10, pady=5) # Left-align in the third row
        self.slide_kanch = ctk.CTkSlider(self.sliders_frame, from_=0, to=100, variable=self.kanchanpur_val, command=self.update_k, state="disabled", button_color="#0078D7", button_hover_color="#005A9E") # Blue-themed slider for Kanchanpur; disabled until needed
        self.slide_kanch.grid(row=2, column=1, sticky="we", padx=10, pady=5) # Stretch horizontally beside the Kanchanpur label

        self.bottom_bar = ctk.CTkFrame(self.sliders_frame, fg_color="transparent") # Transparent bar at the bottom of the sliders for the total label and submit button
        self.bottom_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(15, 15)) # Span both columns beneath the sliders
        self.bottom_bar.grid_columnconfigure(0, weight=1) # Push the total label left and the submit button right

        self.lbl_total = ctk.CTkLabel(self.bottom_bar, text="Total: 0.0%", font=("Courier New", 16, "bold"), text_color="red") # Shows the running total of all three sliders; red until it reaches 100%
        self.lbl_total.grid(row=0, column=0, sticky="w") # Left-align the total percentage label

        self.btn_submit = ctk.CTkButton(self.bottom_bar, text="Lock and Transmit", font=Style.BUTTON_FONT, fg_color=Style.ACCENT_COLOR, hover_color=Style.HOVER_COLOR, text_color="black", state="disabled", command=self.submit_allocation) # Submit button — disabled until the total equals exactly 100%
        self.btn_submit.grid(row=0, column=1, sticky="e") # Right-align the submit button

    def draw_map(self, event=None):
        self.map_canvas.delete("all")             # Clear all previously drawn items from the canvas
        w_canvas = self.map_canvas.winfo_width()  # Get the current pixel width of the canvas widget
        h_canvas = self.map_canvas.winfo_height() # Get the current pixel height of the canvas widget

        x_offset = 0 # Horizontal offset used to centre the map image on the canvas
        y_offset = 0 # Vertical offset used to centre the map image on the canvas
        scale_x = 1.0 # Horizontal scale factor mapping original 800 px coordinates to the displayed image width
        scale_y = 1.0 # Vertical scale factor mapping original 500 px coordinates to the displayed image height

        if self.map_img_tk:
            img_w = self.map_img_tk.width()                  # Get the width of the loaded map image in pixels
            img_h = self.map_img_tk.height()                 # Get the height of the loaded map image in pixels
            x_offset = (w_canvas - img_w) // 2              # Calculate horizontal centring offset
            y_offset = (h_canvas - img_h) // 2              # Calculate vertical centring offset
            self.map_canvas.image = self.map_img_tk          # Keep a reference to prevent garbage collection of the PhotoImage
            self.map_canvas.create_image(x_offset, y_offset, anchor="nw", image=self.map_img_tk)  # Draw the map image anchored at its top-left corner
            scale_x = img_w / 800.0   # Scale factor: how many display pixels per original coordinate pixel (horizontal)
            scale_y = img_h / 500.0   # Scale factor: how many display pixels per original coordinate pixel (vertical)

        else:
            x_offset = w_canvas // 2 - 300 # Fallback horizontal offset when no image is loaded (centres a 600 px wide area)
            y_offset = h_canvas // 2 - 187 # Fallback vertical offset (centres a 375 px tall area)
            scale_x = 600.0 / 800.0 # Fallback horizontal scale (600 px display / 800 px original)
            scale_y = 375.0 / 500.0 # Fallback vertical scale (375 px display / 500 px original)

        c_chitawan = (x_offset + 424.5 * scale_x, y_offset + 327.0 * scale_y)    # Pixel position of Chitawan on the displayed map
        c_dang = (x_offset + 261.8 * scale_x, y_offset + 292.5 * scale_y)        # Pixel position of Dang on the displayed map
        c_kanchanpur = (x_offset + 93.9 * scale_x, y_offset + 210.5 * scale_y)   # Pixel position of Kanchanpur on the displayed map

        r = 6  # Radius in pixels for the location marker dots

        self.map_canvas.create_oval(c_chitawan[0]-r, c_chitawan[1]-r, c_chitawan[0]+r, c_chitawan[1]+r, fill="red", outline="white") # Draw a red dot at Chitawan (the target/bridge site)
        self.map_canvas.create_oval(c_dang[0]-r, c_dang[1]-r, c_dang[0]+r, c_dang[1]+r, fill="#FF8C00", outline="white") # Draw an orange dot at Dang (supply location)
        self.map_canvas.create_oval(c_kanchanpur[0]-r, c_kanchanpur[1]-r, c_kanchanpur[0]+r, c_kanchanpur[1]+r, fill="#FF8C00", outline="white") # Draw an orange dot at Kanchanpur (supply location)

        legend_x = w_canvas - 230   # X position for the legend box, offset from the right edge of the canvas
        legend_y = 20               # Y position for the legend box, near the top of the canvas

        self.map_canvas.create_oval(legend_x, legend_y, legend_x+12, legend_y+12, fill="red", outline="white") # Legend dot for Chitawan (red)
        self.map_canvas.create_text(legend_x+25, legend_y+6, text="Chitawan (Target)", fill="white", font=("Courier", 14, "bold"), anchor="w") # Legend label for Chitawan

        self.map_canvas.create_oval(legend_x, legend_y+30, legend_x+12, legend_y+42, fill="#FF8C00", outline="white") # Legend dot for Dang (orange)
        self.map_canvas.create_text(legend_x+25, legend_y+36, text="Dang (Supply)", fill="white", font=("Courier", 14, "bold"), anchor="w") # Legend label for Dang

        self.map_canvas.create_oval(legend_x, legend_y+60, legend_x+12, legend_y+72, fill="#FF8C00", outline="white") # Legend dot for Kanchanpur (orange)
        self.map_canvas.create_text(legend_x+25, legend_y+66, text="Kanchanpur (Supply)", fill="white", font=("Courier", 14, "bold"), anchor="w") # Legend label for Kanchanpur

    def update_c(self, val): self.balance_sliders("C", float(val)) # Called when the Chitawan slider moves; triggers rebalancing
    def update_d(self, val): self.balance_sliders("D", float(val)) # Called when the Dang slider moves; triggers rebalancing
    def update_k(self, val): self.balance_sliders("K", float(val)) # Called when the Kanchanpur slider moves; triggers rebalancing

    def balance_sliders(self, source, new_val):
        if hasattr(self, '_updating_sliders') and self._updating_sliders: # If we're already inside a programmatic update, do nothing to avoid recursion
            return  # Exit early to prevent infinite callback loops

        self._updating_sliders = True  # Set the guard flag so nested slider callbacks are ignored

        if not hasattr(self, 'slider_history'): # On the very first slider interaction, create the history list
            self.slider_history = []           # Tracks the order in which the player has touched each slider

        if source in self.slider_history: # If this slider was already in the history, remove it so we can re-add it at the end
            self.slider_history.remove(source) # Remove the old entry
        self.slider_history.append(source)     # Append the current slider as the most recently touched

        c = self.chitwan_val.get() # Read the current value of the Chitawan slider (0–100)

        d = self.dang_val.get() # Read the current value of the Dang slider (0–100)

        k = self.kanchanpur_val.get() # Read the current value of the Kanchanpur slider (0–100)

        vals = {"C": c, "D": d, "K": k}  # Pack all three slider values into a dictionary for easy manipulation
        vals[source] = new_val            # Overwrite the value of the slider the player just moved
        
        if len(self.slider_history) >= 2: # Only auto-balance once the player has touched at least two sliders
            diff = 100.0 - vals[source]  # The remaining percentage that the other two sliders must share

            others_to_adjust = [s for s in self.slider_history if s != source]  # Sliders the player has previously touched (excluding current)

            untouched = [s for s in ["C", "D", "K"] if s not in self.slider_history]  # Any slider the player has never touched

            order_to_adjust = untouched + others_to_adjust # Adjust untouched sliders first, then previously touched ones

            val1 = vals[order_to_adjust[0]]  # Current value of the first slider to adjust
            val2 = vals[order_to_adjust[1]]  # Current value of the second slider to adjust

            val1_target = diff - val2        # Target value for the first slider so that all three sum to 100%

            if val1_target < 0:              # If the target is negative, the second slider alone exceeds the remainder
                val1_new = 0.0 # First slider gets clamped to zero
                val2_new = diff # Second slider takes the entire remainder

            elif val1_target > diff:         # If the target exceeds the total remainder (shouldn't normally happen)
                val1_new = diff # First slider takes the entire remainder

                val2_new = 0.0 # Second slider gets clamped to zero

            else:
                val1_new = val1_target       # Normal case: first slider gets the calculated target value

                val2_new = val2 # Second slider keeps its current value unchanged

            vals[order_to_adjust[0]] = val1_new  # Apply the computed value to the first adjusted slider
            vals[order_to_adjust[1]] = val2_new # Apply the computed value to the second adjusted slider

        c = max(0.0, min(100.0, vals["C"])) # Clamp Chitawan value between 0 and 100
        d = max(0.0, min(100.0, vals["D"])) # Clamp Dang value between 0 and 100
        k = max(0.0, min(100.0, vals["K"])) # Clamp Kanchanpur value between 0 and 100

        self.chitwan_val.set(c) # Update the Chitawan DoubleVar so the slider position reflects the new value
        self.dang_val.set(d) # Update the Dang DoubleVar
        self.kanchanpur_val.set(k) # Update the Kanchanpur DoubleVar
        
        self.slide_chitwan.set(c) # Move the Chitawan slider thumb to the new position
        self.slide_dang.set(d) # Move the Dang slider thumb to the new position
        self.slide_kanch.set(k) # Move the Kanchanpur slider thumb to the new position
        
        self.lbl_chitwan.configure(text=f"Chitawan: {c:.1f}% - {(c/100*40):.1f} Tons") # Update label: percentage and corresponding tonnage (out of 40 total tonnes)
        self.lbl_dang.configure(text=f"Dang: {d:.1f}% - {(d/100*40):.1f} Tons") # Update the Dang label with percentage and tonnage
        self.lbl_kanch.configure(text=f"Kanchanpur: {k:.1f}% - {(k/100*40):.1f} Tons") # Update the Kanchanpur label with percentage and tonnage
        
        total = c + d + k  # Sum the three slider values to check if they add up to 100%
        color = "#4CAF50" if abs(total - 100.0) < 0.1 else "#FF4444"  # Green if total ≈ 100%, red otherwise
        self.lbl_total.configure(text=f"Total Amount: {total:.1f}%", text_color=color) # Update the total label with the sum and appropriate colour
        
        if abs(total - 100.0) < 0.1:                      # If the allocation is valid (sums to 100% within tolerance)
            self.btn_submit.configure(state="normal")      # Enable the "Lock and Transmit" button
        else:
            self.btn_submit.configure(state="disabled")    # Keep the submit button disabled until the total reaches 100%
            
        self._updating_sliders = False  # Clear the guard flag so future slider callbacks will be processed

    def submit_allocation(self):
        c = self.chitwan_val.get()   # Read the final Chitawan percentage from the slider
        d = self.dang_val.get()      # Read the final Dang percentage from the slider
        k = self.kanchanpur_val.get()# Read the final Kanchanpur percentage from the slider
        
        self.controller.chitwan_pct = float(c) # Store the Chitawan percentage in the MissionController for later use
        self.controller.dang_pct = float(d) # Store the Dang percentage in the MissionController
        self.controller.kanchanpur_pct = float(k) # Store the Kanchanpur percentage in the MissionController
        self.controller.state = "DONE"       # Set the controller state to DONE — the chatbot phase is complete
        self.controller.game_over = True     # Mark the mission as over so no further chat input is processed
        
        self.chat_screen.add_message("You", f"[Transmission Protocol] Allocating Materials:\n- Chitawan: {c:.1f}%\n- Dang: {d:.1f}%\n- Kanchanpur: {k:.1f}%", is_user=True) # Display the player's allocation as a formatted chat message
        self.chat_screen.add_message("Mission Control", f"Data accepted! Total allocation: {c+d+k:.1f}%. Commencing construction layer... Over and out.", is_user=False) # Display Mission Control's confirmation and sign-off
        
        self.chat_screen.disable_input() # Disable the chat input so the player can no longer type messages
        self.slide_chitwan.configure(state="disabled") # Lock the Chitawan slider to prevent further changes
        self.slide_dang.configure(state="disabled") # Lock the Dang slider
        self.slide_kanch.configure(state="disabled") # Lock the Kanchanpur slider
        self.btn_submit.configure(state="disabled") # Disable the submit button since the allocation is finalised

        self.after(3000, self.quit)  # Close the chatbot window after a 3-second delay before launching the simulation


# =============================================================================
#  SECTION 4 — CORE SIMULATION (Construction Layer)
#  Animates the material deliveries and real-time bridge construction on the map.
# =============================================================================

class ConstructionLayer:

    def __init__(self, screen, font_normal, pct_Chitawan, pct_dang, pct_kanchanpur):
        self.screen = screen                # Reference to the Pygame display surface for drawing
        self.font_normal = font_normal      # 24 pt Courier New font used for the simulation timer display
        self.font_legend = pygame.font.SysFont("Courier New", 16)          # Smaller font for legend text in the simulation view
        self.font_labels = pygame.font.SysFont("Courier New", 18, bold=True) # Bold font for location labels on the map

        self.pct_Chitawan = pct_Chitawan # Fraction (0.0–1.0) of materials sourced from Chitawan
        self.pct_dang = pct_dang # Fraction (0.0–1.0) of materials sourced from Dang
        self.pct_kanchanpur = pct_kanchanpur # Fraction (0.0–1.0) of materials sourced from Kanchanpur

        self.dur_Chitawan = 24.0 * pct_Chitawan     # Hours of construction work contributed by Chitawan materials
        self.dur_dang = 24.0 * pct_dang             # Hours of construction work contributed by Dang materials
        self.dur_kanchanpur = 24.0 * pct_kanchanpur # Hours of construction work contributed by Kanchanpur materials
        
        end_C = self.dur_Chitawan  # Chitawan construction ends after its duration (starts at time 0)

        if self.dur_dang > 0:
            start_D = max(end_C, 8.0)       # Dang materials can't arrive before 8 hours (travel time from Dang)
            end_D = start_D + self.dur_dang  # Dang construction ends after its materials are fully used
        else:
            end_D = end_C  # If no materials from Dang, the timeline continues from where Chitawan ended

        if self.dur_kanchanpur > 0:
            start_K = max(end_D, 16.0)              # Kanchanpur materials can't arrive before 16 hours (travel time)
            end_K = start_K + self.dur_kanchanpur   # Kanchanpur construction ends after its materials are fully used
        else:
            end_K = end_D  # If no materials from Kanchanpur, the timeline continues from where Dang ended

        self.total_time = max(end_K, 24.0) # Total simulation duration; at least 24 hours (the base construction time)
        
        self.timer = 0.0       # Tracks elapsed simulation time in hours (incremented each frame)
        self.completed = False # Set to True when the timer reaches total_time, signalling construction is finished

        self.coords = {
            "Chitawan": (424.5, 327.0),     # Map pixel coordinates for Chitawan (bridge site / target)
            "Dang": (261.8, 292.5),         # Map pixel coordinates for Dang (supply location)
            "Kanchanpur": (93.9, 210.5)     # Map pixel coordinates for Kanchanpur (supply location)
        }

        self.map_img = None # Will hold the Pygame surface for the Nepal map background
        map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nepal_map.png") # Full path to the map image file
        if os.path.exists(map_path):
            self.map_img = pygame.image.load(map_path)  # Load the Nepal map image as a Pygame surface

        self.last_printed_pct = -1  # Tracks the last printed completion percentage to avoid duplicate console output

    def update(self, dt):
        if self.timer < self.total_time:
            self.timer += dt / 1000.0          # Convert milliseconds to seconds and advance the simulation clock
            if self.timer >= self.total_time:  # Check if the simulation has reached or exceeded the total duration
                self.timer = self.total_time # Clamp the timer to exactly the total time
                self.completed = True          # Mark the construction as finished
                
        pct_complete = min(100, int((self.timer / self.total_time) * 100))  # Calculate the integer completion percentage (0–100)
        if pct_complete != self.last_printed_pct:  # Only print when the percentage changes to avoid console spam
            if self.timer <= self.dur_Chitawan:
                current_loc = "Chitawan"  # Materials are currently arriving from Chitawan
            elif 8 <= self.timer <= max(self.dur_Chitawan, 8.0) + self.dur_dang:
                current_loc = "Dang"      # Materials are currently arriving from Dang
            elif 16 <= self.timer <= self.total_time:
                current_loc = "Kanchanpur" # Materials are currently arriving from Kanchanpur
            else:
                current_loc = "Waiting"   # Between deliveries — construction is stalled waiting for materials

            if current_loc != "Waiting":
                print(f"Material from {current_loc} arriving... Construction {pct_complete}% complete.") # Log active construction progress
            else:
                print(f"Stalled... Construction {pct_complete}% complete.") # Log that construction is idle

            self.last_printed_pct = pct_complete  # Remember this percentage so we don't re-print it next frame

    def get_chitawan_color(self):
        t = self.timer  # Current simulation time in hours

        if t <= self.dur_Chitawan:
            return BLUE   # Chitawan materials are being used — construction is underway (blue)

        if t < 8.0:
            return BLACK  # Between Chitawan completion and Dang arrival — construction is idle (black)

        max_ch_8 = max(self.dur_Chitawan, 8.0)   # The earliest time Dang materials can start being used
        exhaust_dang = max_ch_8 + self.dur_dang  # The time when all Dang materials have been used

        if max_ch_8 <= t <= exhaust_dang:
            return BLUE   # Dang materials are being used — construction is underway (blue)

        if t < 16.0:
            return BLACK  # Between Dang completion and Kanchanpur arrival — construction is idle (black)

        if 16.0 <= t < self.total_time:
            return BLUE   # Kanchanpur materials are being used — construction is underway (blue)

        if t >= self.total_time:
            return GREEN  # All materials used, construction is complete (green)

        return BLACK  # Default fallback — construction is idle (black)

    def lerp(self, p1, p2, t):
        t = max(0.0, min(1.0, t))                          # Clamp the interpolation factor t to the range [0.0, 1.0]
        return (p1[0] + (p2[0] - p1[0]) * t,              # Linearly interpolate the x-coordinate between p1 and p2
                p1[1] + (p2[1] - p1[1]) * t)              # Linearly interpolate the y-coordinate between p1 and p2

    def draw(self):
        y_offset = 50  # Vertical offset to push the map down, leaving space for the timer text at the top

        if self.map_img:
            self.screen.blit(self.map_img, (0, y_offset))  # Draw the Nepal map background starting 50 px from the top

        c_chitawan = (int(self.coords["Chitawan"][0]), int(self.coords["Chitawan"][1] + y_offset)) # Pixel position of Chitawan with vertical offset applied
        c_dang = (int(self.coords["Dang"][0]), int(self.coords["Dang"][1] + y_offset)) # Pixel position of Dang with vertical offset applied
        c_kanchanpur = (int(self.coords["Kanchanpur"][0]), int(self.coords["Kanchanpur"][1] + y_offset)) # Pixel position of Kanchanpur with vertical offset applied

        pygame.draw.line(self.screen, LINE_COLOR, c_kanchanpur, c_chitawan, 2)  # Draw a supply route line from Kanchanpur to Chitawan
        pygame.draw.line(self.screen, LINE_COLOR, c_dang, c_chitawan, 2)        # Draw a supply route line from Dang to Chitawan

        pygame.draw.circle(self.screen, (100, 100, 100), c_kanchanpur, 6) # Draw a grey dot at Kanchanpur's position (supply node)
        pygame.draw.circle(self.screen, (100, 100, 100), c_dang, 6) # Draw a grey dot at Dang's position (supply node)
        
        current_chitawan_col = self.get_chitawan_color() # Get the current colour for Chitawan based on construction phase (black/blue/green)
        pygame.draw.circle(self.screen, current_chitawan_col, c_chitawan, 12)       # Draw a larger dot at Chitawan showing the construction status
        if current_chitawan_col != BLACK:
            pygame.draw.circle(self.screen, WHITE, c_chitawan, 12, 2)              # Add a white outline ring when construction is active or complete

        if self.pct_kanchanpur > 0:
            cursor_k = self.lerp(c_kanchanpur, c_chitawan, self.timer / 16.0)  # Interpolate a moving dot along the Kanchanpur→Chitawan route based on elapsed time
            if self.timer <= 16.0:  # Only show the moving dot while the Kanchanpur delivery is in transit (first 16 hours)
                pygame.draw.circle(self.screen, (255, 140, 0), (int(cursor_k[0]), int(cursor_k[1])), 8) # Draw an orange moving dot representing the material shipment

        if self.pct_dang > 0:
            cursor_d = self.lerp(c_dang, c_chitawan, self.timer / 8.0)  # Interpolate a moving dot along the Dang→Chitawan route (8-hour journey)
            if self.timer <= 8.0:  # Only show the moving dot while the Dang delivery is in transit (first 8 hours)
                pygame.draw.circle(self.screen, (255, 140, 0), (int(cursor_d[0]), int(cursor_d[1])), 8) # Draw an orange moving dot representing the material shipment

        timer_text = self.font_normal.render(f"Simulation Time: {self.timer:.1f}s / {self.total_time:.1f}s", True, WHITE) # Render the elapsed/total time text in white
        self.screen.blit(timer_text, (20, 20)) # Draw the timer text in the top-left corner of the window

        legend_x = WIDTH - 220  # X position for the simulation legend, near the right edge of the window
        legend_y = 20 # Y position for the simulation legend, near the top of the window

        pygame.draw.circle(self.screen, BLACK, (legend_x, legend_y), 6) # Legend dot: black = construction delay/idle
        pygame.draw.circle(self.screen, WHITE, (legend_x, legend_y), 6, 1)  # White outline on the black legend dot for visibility
        lbl_delay = self.font_legend.render("Construction Delay", True, WHITE) # Render the "Construction Delay" legend text
        self.screen.blit(lbl_delay, (legend_x + 15, legend_y - 8)) # Position the text to the right of the legend dot

        pygame.draw.circle(self.screen, BLUE, (legend_x, legend_y + 25), 6) # Legend dot: blue = construction underway
        lbl_underway = self.font_legend.render("Construction Underway", True, WHITE) # Render the "Construction Underway" legend text
        self.screen.blit(lbl_underway, (legend_x + 15, legend_y + 17)) # Position the text to the right of the blue dot

        pygame.draw.circle(self.screen, GREEN, (legend_x, legend_y + 50), 6) # Legend dot: green = project complete
        lbl_completed = self.font_legend.render("Project Delivery", True, WHITE) # Render the "Project Delivery" legend text
        self.screen.blit(lbl_completed, (legend_x + 15, legend_y + 42)) # Position the text to the right of the green dot


# =============================================================================
#  SECTION 5 — PERFORMANCE EVALUATOR
#  Scores the player and displays stacked bar charts comparing their choices.
# =============================================================================

def generate_performance_charts(pct_chitawan, pct_dang, pct_kanchanpur):
    pct_c = pct_chitawan / 100.0 # Convert Chitawan percentage (0–100) to a fraction (0.0–1.0)
    pct_d = pct_dang / 100.0 # Convert Dang percentage to a fraction
    pct_k = pct_kanchanpur / 100.0 # Convert Kanchanpur percentage to a fraction

    cost_c = pct_c * 40 * 1000   # Player's cost from Chitawan: fraction × 40 tonnes × $1000/ton
    cost_d = pct_d * 40 * 980    # Player's cost from Dang: fraction × 40 tonnes × $980/ton
    cost_k = pct_k * 40 * 960    # Player's cost from Kanchanpur: fraction × 40 tonnes × $960/ton

    ideal_cost_c = 0.33 * 40 * 1000    # Ideal cost from Chitawan (33% allocation at $1000/ton)
    ideal_cost_d = 0.33 * 40 * 980     # Ideal cost from Dang (33% allocation at $980/ton)
    ideal_cost_k = 0.34 * 40 * 960     # Ideal cost from Kanchanpur (34% allocation at $960/ton)

    dur_c = 24.0 * pct_c   # Construction hours contributed by Chitawan materials
    dur_d = 24.0 * pct_d   # Construction hours contributed by Dang materials
    dur_k = 24.0 * pct_k   # Construction hours contributed by Kanchanpur materials

    end_c = dur_c # Chitawan construction phase ends at this hour mark
    if dur_d > 0:
        start_d = max(end_c, 8.0)   # Dang phase can't start before hour 8 (travel time from Dang)
        end_d = start_d + dur_d # Dang phase ends after its construction hours are consumed
    else:
        start_d = end_c # No Dang materials — start time equals Chitawan end time (no gap)
        end_d = end_c # No Dang materials — end time equals Chitawan end time

    if dur_k > 0:
        start_k = max(end_d, 16.0)  # Kanchanpur phase can't start before hour 16 (travel time)
        end_k = start_k + dur_k # Kanchanpur phase ends after its construction hours are consumed
    else:
        start_k = end_d # No Kanchanpur materials — start time equals Dang end time
        end_k = end_d # No Kanchanpur materials — end time equals Dang end time

    idle1_start = end_c                        # First idle period begins when Chitawan materials run out
    idle1_dur = max(0, start_d - end_c)        # Duration of the first idle gap (waiting for Dang materials)

    idle2_start = end_d                        # Second idle period begins when Dang materials run out
    idle2_dur = max(0, start_k - end_d)        # Duration of the second idle gap (waiting for Kanchanpur materials)

    ideal_dur_c = 8.0   # Ideal timeline: 8 hours of work from each of the three locations
    ideal_dur_d = 8.0   # Ideal timeline: 8 hours of work from Dang (no idle gaps)
    ideal_dur_k = 8.0   # Ideal timeline: 8 hours of work from Kanchanpur (total = 24 hours)

    bg_color = Style.BG_COLOR   # Chart background colour, matching the app's dark theme
    text_color = "white" # Text colour for axis labels, titles, and tick marks
    col_c = "#FFD700"    # Bar colour for Chitawan segments (construction yellow)
    col_d = "#FF6E00"    # Bar colour for Dang segments (orange)
    col_k = "#0078D7"    # Bar colour for Kanchanpur segments (blue)
    col_idle = "white"   # Bar colour for idle/stalled periods (white)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), facecolor=bg_color)  # Create a figure with two side-by-side sub-plots

    ax1.set_facecolor(bg_color) # Set the cost chart's background to match the dark theme
    ax1.set_title("Total Cost Analysis (USD)", color=text_color) # Title for the left chart
    ax1.set_ylabel("Total Cost (USD)", color=text_color) # Y-axis label for the cost chart
    ax1.set_ylim(0, 55000)  # Fix the y-axis range to $0–$55,000 for consistent visual comparison

    ax1.bar(["Player Performance"], [cost_c], color=col_c, edgecolor='black', label="Chitawan") # Player's Chitawan cost bar (bottom segment)
    ax1.bar(["Player Performance"], [cost_d], bottom=[cost_c], color=col_d, edgecolor='black', label="Dang") # Player's Dang cost bar stacked on top of Chitawan
    ax1.bar(["Player Performance"], [cost_k], bottom=[cost_c + cost_d], color=col_k, edgecolor='black', label="Kanchanpur") # Player's Kanchanpur cost bar stacked on top
    
    ax1.bar(["Ideal Condition"], [ideal_cost_c], color=col_c, edgecolor='black') # Ideal Chitawan cost bar (bottom segment of the "Ideal" column)
    ax1.bar(["Ideal Condition"], [ideal_cost_d], bottom=[ideal_cost_c], color=col_d, edgecolor='black') # Ideal Dang cost bar stacked on top
    ax1.bar(["Ideal Condition"], [ideal_cost_k], bottom=[ideal_cost_c + ideal_cost_d], color=col_k, edgecolor='black') # Ideal Kanchanpur cost bar stacked on top

    ax1.tick_params(colors=text_color)          # Set tick mark and tick label colours to white
    ax1.spines['bottom'].set_color(text_color)  # Set the bottom axis line to white
    ax1.spines['left'].set_color(text_color)    # Set the left axis line to white
    ax1.spines['top'].set_visible(False)         # Hide the top axis line for a cleaner look
    ax1.spines['right'].set_visible(False) # Hide the right axis line for a cleaner look
    ax1.legend(loc='upper right')               # Place the legend in the upper-right corner

    ax2.set_facecolor(bg_color) # Set the timeline chart's background to match the dark theme
    ax2.set_title("Construction Timeline Efficiency", color=text_color) # Title for the right chart
    ax2.set_ylabel("Time (Hours)", color=text_color) # Y-axis label for the timeline chart
    ax2.set_ylim(0, 55)  # Fix the y-axis range to 0–55 hours for consistent visual comparison

    ax2.bar(["Player Performance"], [dur_c], color=col_c, edgecolor='black')                             # Player's Chitawan construction time (bottom segment)

    if idle1_dur > 0:       # If there's an idle gap between Chitawan and Dang deliveries
        ax2.bar(["Player Performance"], [idle1_dur], bottom=[idle1_start], color=col_idle, edgecolor='black', label="Idle/Stalled") # Draw the first idle period as a white bar

    if dur_d > 0:           # If the player allocated any materials from Dang
        ax2.bar(["Player Performance"], [dur_d], bottom=[start_d], color=col_d, edgecolor='black') # Draw Dang construction time stacked on the timeline

    if idle2_dur > 0:
        lbl = "Idle/Stalled" if idle1_dur == 0 else ""  # Only label the first idle bar to avoid duplicate legend entries
        ax2.bar(["Player Performance"], [idle2_dur], bottom=[idle2_start], color=col_idle, edgecolor='black', label=lbl) # Draw the second idle period

    if dur_k > 0:           # If the player allocated any materials from Kanchanpur
        ax2.bar(["Player Performance"], [dur_k], bottom=[start_k], color=col_k, edgecolor='black') # Draw Kanchanpur construction time stacked on the timeline

    ax2.bar(["Ideal Condition"], [ideal_dur_c], color=col_c, edgecolor='black') # Ideal Chitawan timeline segment (8 hours)
    ax2.bar(["Ideal Condition"], [ideal_dur_d], bottom=[ideal_dur_c], color=col_d, edgecolor='black') # Ideal Dang timeline segment stacked at 8–16 hours
    ax2.bar(["Ideal Condition"], [ideal_dur_k], bottom=[ideal_dur_c + ideal_dur_d], color=col_k, edgecolor='black') # Ideal Kanchanpur timeline segment stacked at 16–24 hours

    ax2.tick_params(colors=text_color) # Set tick colours to white for the timeline chart
    ax2.spines['bottom'].set_color(text_color) # White bottom axis line
    ax2.spines['left'].set_color(text_color) # White left axis line
    ax2.spines['top'].set_visible(False) # Hide the top axis line
    ax2.spines['right'].set_visible(False) # Hide the right axis line

    handles, labels = ax2.get_legend_handles_labels() # Retrieve current legend entries from the timeline chart
    from matplotlib.patches import Patch # Import Patch to create a custom legend entry
    if "Idle/Stalled" not in labels: # If no idle bars were drawn, we still want the legend entry for completeness
        handles.append(Patch(facecolor=col_idle, edgecolor='black', label='Idle/Stalled')) # Add a manual "Idle/Stalled" legend patch
    ax2.legend(handles=handles, loc='upper right') # Display the legend in the upper-right corner of the timeline chart

    plt.tight_layout()                          # Automatically adjust sub-plot spacing to prevent overlapping labels
    plt.savefig("performance_report.png", dpi=100)  # Save the figure as a PNG image at 100 DPI in the current directory
    plt.close(fig)                              # Close the figure to free memory


class PerformanceEvaluator(ctk.CTkToplevel):

    def __init__(self, master, chitwan_pct, dang_pct, kanchanpur_pct, t_actual):
        super().__init__(master)                      # Create a new top-level CTk window as a child of the main app
        self.title("Performance Evaluator")           # Set the window title to "Performance Evaluator"
        self.geometry("850x780")                      # Set the window size to 850×780 pixels
        self.configure(fg_color=Style.BG_COLOR)      # Apply the dark asphalt background colour

        c_chitwan = (chitwan_pct / 100.0) * 40 * 1000     # Calculate the player's Chitawan cost: percentage × 40 tonnes × $1000/ton
        c_dang = (dang_pct / 100.0) * 40 * 980            # Calculate the player's Dang cost: percentage × 40 tonnes × $980/ton
        c_kanchanpur = (kanchanpur_pct / 100.0) * 40 * 960# Calculate the player's Kanchanpur cost: percentage × 40 tonnes × $960/ton
        c_actual = c_chitwan + c_dang + c_kanchanpur       # Sum all three location costs to get total project cost

        s_t = (40 - t_actual) / (40 - 24) # Time efficiency score: higher is better; 1.0 when t_actual = 24h, 0.0 when t_actual = 40h

        s_c = (40000 - c_actual) / (40000 - 38400) # Cost efficiency score: higher is better; 1.0 when cost = $38,400 (cheapest), 0.0 when cost = $40,000 (most expensive)

        E = (0.65 * s_t) + (0.35 * s_c) # Weighted composite efficiency: 65% time weight + 35% cost weight

        scaled_score = (E / 0.825) * 100 # Normalise the efficiency to a 0–100 scale (0.825 is the theoretical max E when ideal allocation is used)
        scaled_score = max(0, min(100.0, scaled_score))  # Clamp the score between 0 and 100 to handle edge cases

        title_lbl = ctk.CTkLabel(self, text="PERFORMANCE EVALUATOR", font=("Courier New", 32, "bold"), text_color=Style.ACCENT_COLOR) # Large yellow title at the top of the dashboard
        title_lbl.pack(pady=(20, 10))  # Add vertical padding above and below the title

        metrics_frame = ctk.CTkFrame(self, fg_color="transparent") # Transparent container for the three metric cards
        metrics_frame.pack(fill="x", padx=30, pady=10) # Fill horizontally with padding on each side
        metrics_frame.grid_columnconfigure(0, weight=1)   # First card column takes equal width
        metrics_frame.grid_columnconfigure(1, weight=1) # Second card column takes equal width
        metrics_frame.grid_columnconfigure(2, weight=1) # Third card column takes equal width

        self._create_card(metrics_frame, "Total Time", f"{t_actual:.1f} Hours", 0)     # Metric card 1: displays the actual construction time in hours
        self._create_card(metrics_frame, "Total Cost", f"${c_actual:,.0f}", 1)          # Metric card 2: displays the total project cost formatted with commas
        self._create_card(metrics_frame, "Final Efficiency", f"{scaled_score:.1f}%", 2) # Metric card 3: displays the normalised efficiency score as a percentage
        
        generate_performance_charts(chitwan_pct, dang_pct, kanchanpur_pct) # Generate the stacked bar charts and save them as performance_report.png
        try:
            pil_img = Image.open("performance_report.png")  # Open the generated chart image
            chart_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(800, 320)) # Wrap it as a CTkImage with explicit display size
            chart_lbl = ctk.CTkLabel(self, text="", image=chart_img)  # Create an image label (no text, image only)
            chart_lbl.pack(pady=(10, 10)) # Display the chart image with vertical padding
        except Exception as e:
            print("Failed to load chart image:", e)  # Log the error if the chart image can't be loaded
            
        if scaled_score >= 90:
            feedback_text = "Elite Engineer - Optimal Resource Management" # Top-tier feedback message
            color = "#4CAF50"   # Green colour for excellent performance
        elif scaled_score >= 75:
            feedback_text = "Competent Builder - Good Efficiency" # Mid-tier feedback message
            color = "#FFC107"   # Amber colour for good performance
        else:
            feedback_text = "In-Training - High Time and Cost Waste Detected" # Low-tier feedback message
            color = "#F44336"   # Red colour for poor performance
            
        feedback_lbl = ctk.CTkLabel(self, text=feedback_text, font=("Courier New", 22, "bold"), text_color=color) # Display the performance feedback label in the appropriate colour
        feedback_lbl.pack(pady=(40, 20))  # Add padding above and below the feedback text
        
        btn = ctk.CTkButton(self, text="Finish Simulation", font=Style.BUTTON_FONT, fg_color=Style.ACCENT_COLOR, hover_color=Style.HOVER_COLOR, command=self.quit) # Button to close the entire application
        btn.pack(pady=10) # Add vertical padding around the finish button

    def _create_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, fg_color=Style.FRAME_BG_COLOR, corner_radius=15, height=120) # Create a dark card with rounded corners, fixed 120 px height
        card.grid(row=0, column=col, padx=10, sticky="nsew")  # Place the card in the specified column
        card.grid_propagate(False)   # Prevent the card from shrinking to fit its contents (preserve the 120 px height)
        card.pack_propagate(False)   # Also prevent pack geometry manager from resizing the card
        
        lbl_title = ctk.CTkLabel(card, text=title, font=("Courier New", 16), text_color=Style.SUBTEXT_COLOR) # Subtitle label (e.g., "Total Time") in grey
        lbl_title.pack(pady=(25, 5))  # Position with top and bottom padding inside the card
        
        lbl_val = ctk.CTkLabel(card, text=value, font=("Courier New", 26, "bold"), text_color=Style.TEXT_COLOR) # Value label (e.g., "24.0 Hours") in large bold white text
        lbl_val.pack(pady=(0, 15))    # Position below the title with bottom padding
        

# =============================================================================
#  SECTION 6 — MAIN ORCHESTRATOR
#  Coordinates the linear transition between the distinct application phases.
# =============================================================================

def main():
    login_page = LoginPage() # Create a new LoginPage instance (initialises Pygame and shows the login window)
    user_name = login_page.run() # Run the login screen event loop; returns the player's name once they click Start

    app = RapidBridgeApp(player_name=user_name) # Create the chatbot + map window, passing in the player's name
    app.mainloop()   # Start the CTk event loop — blocks until the window is closed or quit() is called
    app.withdraw()   # Hide the chatbot window (don't destroy it yet; it's still the master for PerformanceEvaluator)

    if app.controller.game_over: # Only proceed to the simulation if the player completed the chatbot (didn't abort)
        total_pct = app.controller.chitwan_pct + app.controller.dang_pct + app.controller.kanchanpur_pct # Sum the three allocations
        if total_pct > 0:  # Guard: only run the simulation if the player actually submitted a valid allocation
            def run_simulation(pct_c, pct_d, pct_k): # Inner function that runs the Pygame construction simulation
                 pygame.init() # Re-initialise Pygame (it was quit after the login screen)
                 screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Create a new 800×600 Pygame window for the simulation
                 pygame.display.set_caption("Rapid Bridge Construction - Map Simulation") # Set the simulation window title
                 clock = pygame.time.Clock() # Create a clock to control the simulation frame rate
                 font_normal = pygame.font.SysFont("Courier New", 24) # 24 pt font for the simulation timer display
                 layer = ConstructionLayer(screen, font_normal, pct_c, pct_d, pct_k) # Create the construction simulation with the player's allocation fractions
                 running = True # Flag to control the simulation loop
                 end_timer = 0 # Accumulates milliseconds after construction completes (3-second delay before closing)
                 while running: # Main simulation loop
                     dt = clock.tick(FPS) # Advance the clock and get elapsed milliseconds since the last frame
                     for event in pygame.event.get(): # Process all pending Pygame events
                         if event.type == pygame.QUIT: # The player clicked the window's close button
                             running = False # Exit the simulation loop
                     layer.update(dt) # Advance the simulation timer and update construction progress
                     if layer.completed: # If construction has finished
                         end_timer += dt # Accumulate time since completion
                         if end_timer >= 3000: # After 3 seconds of showing the final state
                             running = False # Exit the simulation loop
                     screen.fill(DARK_GREY) # Clear the screen with the dark grey background
                     layer.draw() # Draw the map, route lines, location dots, moving cursors, and legend
                     pygame.display.flip() # Swap the back buffer to the screen
                 pygame.quit() # Destroy the Pygame window and release all Pygame resources
                 return layer.total_time # Return the total simulation time for the performance evaluator

            t_actual = run_simulation(app.controller.chitwan_pct / 100.0, app.controller.dang_pct / 100.0, app.controller.kanchanpur_pct / 100.0) # Run the simulation with the player's percentages converted to fractions

            eval_app = PerformanceEvaluator(app, chitwan_pct=app.controller.chitwan_pct, dang_pct=app.controller.dang_pct, kanchanpur_pct=app.controller.kanchanpur_pct, t_actual=t_actual) # Create the performance dashboard, passing all allocation data and actual time
            eval_app.protocol("WM_DELETE_WINDOW", app.quit) # Wire the dashboard's close button to quit the entire CTk app
            app.mainloop()       # Re-enter the CTk event loop to keep the performance dashboard visible until closed
            eval_app.destroy()   # Destroy the performance dashboard window after the event loop ends

    app.destroy()  # Destroy the main CTk window and release all remaining Tkinter resources

# =============================================================================
#  ENTRY POINT — this block only runs when the script is executed directly
# =============================================================================
if __name__ == "__main__":
    try:
        import pygame   # Verify that Pygame is installed before attempting to start the game
    except ImportError:
        print("Pygame library is required to run this script. Install it using 'pip install pygame'.") # Inform the user how to install the missing dependency
        sys.exit(1)     # Exit with error code 1 since the required dependency is missing
    
    main() # Launch the full game workflow: Login → Chatbot → Simulation → Performance Report


