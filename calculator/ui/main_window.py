# calculator/ui/main_window.py
import re
from PySide6.QtCore import QTimer # type: ignore
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton, QScrollArea, QFrame # type: ignore
from PySide6.QtCore import Qt, QObject # type: ignore
from PySide6.QtGui import QKeyEvent, QGuiApplication # type: ignore
from logic.stat import StatisticsManager
from logic.statvar_menu import StatVarMenuManager
from .manual import ManualWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stat_manager = StatisticsManager()
        self.statvar_menu = StatVarMenuManager()
        
        self.key_buffer = ""
        self.cursor_position = 0
        self.insert_mode = False
        self._toggling_secondary = False
        self.is_in_menu = False  
        self.menu_type = None    
        self.menu_stack = []  # Stack to track nested menus
        self.menu_context = {}  # Store context for each menu
        self.angle_mode = "rad"
        self.output_format = "flo"
        self.decimal_places = None  # Default is None (F), meaning flexible decimal places
        self._original_sender = self.sender
        self.ans = "0"  # Initialize ans variable
        self.is_in_hyp = False  
        self.k_value = ""  # Store the K value entered by user
        self.k_mode_active = False  # Track if K mode is active
        self.mod_value = ""  # Store the MOD value entered by user
        self.mod_mode_active = False  # Track if MOD mode is active
        
        self.session_memory = []  # Store history of expressions
        self.history_index = -1   # Current position in history (-1 means not in history)
        
        # Memory storage variables
        self.memory_values = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}  # Storage for a, b, c, d, e values
        self.rand_value = 0  # Storage for random seed (r)
        
        # Input state tracking
        self.current_input = "0"
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.setWindowTitle("TI-30X IIS Calculator")
        self.setGeometry(100, 100, 400, 600)  # Set window size

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Display area (two-line display)
        self.display_input = QLabel("0")  # Current input
        self.display_result = QLabel("")  # Result display
        self.display_input.setAlignment(Qt.AlignRight)
        self.display_result.setAlignment(Qt.AlignRight)
        
        # Create a scroll area for the input display
        self.input_scroll_area = QScrollArea()
        self.input_scroll_area.setWidgetResizable(True)
        self.input_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.input_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_scroll_area.setFrameShape(QFrame.NoFrame)

        # Set the display input in the scroll area
        self.input_scroll_area.setWidget(self.display_input)

        # Style the labels
        self.display_input.setStyleSheet("font-size: 24px;")
        self.display_result.setStyleSheet("font-size: 20px; color: grey;")

        # Add display labels to layout
        main_layout.addWidget(self.input_scroll_area)
        main_layout.addWidget(self.display_result)

        # Set up grid layout for buttons
        self.grid_layout = QGridLayout()

        # State to track if "2ND" button is active
        self.secondary_state = False

        # Add buttons
        self.add_buttons(self.grid_layout)

        # Add button layout to the main layout
        main_layout.addLayout(self.grid_layout)
        
        # Add status bar at the bottom
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignCenter)
        self.status_bar.setStyleSheet("font-size: 10px; background-color: #f0f0f0; border-top: 1px solid #ccc; padding: 2px;")
        main_layout.addWidget(self.status_bar)
        
        # Update the status bar with initial settings
        self.update_status_bar()

        # Set the central widget of the window
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.load_state()  # Load saved state from file
        
        self.update_display_with_cursor()

    def add_buttons(self, grid_layout):
        self.buttons = [
            # row 1: 2nd/NULL, DRG/"SCI/ENG", DEL/INS
            ("2ND", "", 0, 1),
            ("DRG", "SCI/ENG", 0, 2),
            ("DEL", "INS", 0, 3),

            # row 2: log/10^x, prb/f<>d, ° ' \" /r<>p, ABS/NULL
            ("MOD", "", 1, 0),
            ("LOG", "10^x", 1, 1),
            ("PRB", "f<>d", 1, 2),
            ("° ' \"", "r<>p", 1, 3),
            ("ABS", "", 1, 4),

            # row 3: ln/e^x, "a b/c"/"a b/c <> d/e", data/stat, statvar/exit stat, clear/memclr
            ("LN", "e^x", 2, 0),
            ("A B/C", "A B/C <> D/E", 2, 1),
            ("DATA", "STAT", 2, 2),
            ("STATVAR", "EXIT STAT", 2, 3),
            ("CLEAR", "MEMCLR", 2, 4),

            # row 4: π/hyp, sin/sin^(-1), cos/cos^(-1), tan/tan^(-1), ÷/K
            ("π", "HYP", 3, 0),
            ("SIN", "SIN^(-1)", 3, 1),
            ("COS", "COS^(-1)", 3, 2),
            ("TAN", "TAN^(-1)", 3, 3),
            ("÷", "K", 3, 4),

            # row 5: ^/xroot, x^-1 (represents "ans^(-1))/EE, (/%, )/",", * (multiplication)/NULL
            ("^", "X√", 4, 0),
            ("X^-1", "EE", 4, 1),
            ("(", "%", 4, 2),
            (")", ",", 4, 3),
            ("*", "", 4, 4),

            # row 6: x^2/sqrt, 7/NULL, 8/NULL, 9/NULL, -(subtraction)/NULL
            ("X²", "√", 5, 0),
            ("7", "", 5, 1),
            ("8", "", 5, 2),
            ("9", "", 5, 3),
            ("-", "", 5, 4),

            # row 7: clrvar, 4/NULL, 5/NULL, 6/NULL, +/NULL
            ("CLRVAR", " ", 6, 0),
            ("4", "", 6, 1),
            ("5", "", 6, 2),
            ("6", "", 6, 3),
            ("+", "", 6, 4),

            # row 8: sto>/rcl, 1/NULL, 2/NULL, 3/NULL, =/NULL
            ("STO>", "RCL", 7, 0),
            ("1", "", 7, 1),
            ("2", "", 7, 2),
            ("3", "", 7, 3),
            ("=", "", 7, 4),

            # row 9: 0/reset, ./fix, (-)/ans
            ("MENU", "", 8, 0),
            ("0", "RESET", 8, 1),
            (".", "FIX", 8, 2),
            ("(-)", "ANS", 8, 3),
        ]

        # Add the buttons and secondary labels to the grid
        self.button_widgets = {}
        for (primary, secondary, row, col) in self.buttons:
            # Create the button for the primary function
            button = QPushButton(primary)
            button.setText(primary.upper())  # Ensure button text is uppercase
            button.setFocusPolicy(Qt.NoFocus)
            grid_layout.addWidget(button, row * 2 + 1, col)  # Place button in the grid

            # Display secondary text above the button (in smaller font)
            if secondary:  # Only show secondary if it is not empty
                label_secondary = QLabel(secondary)
                label_secondary.setAlignment(Qt.AlignCenter)
                label_secondary.setStyleSheet("font-size: 10px; color: gray;")
                # Add the secondary label above the button
                grid_layout.addWidget(label_secondary, row * 2, col)
            else:
                label_secondary = None

            # Store the button and label widgets
            self.button_widgets[(row, col)] = (button, label_secondary)
            
            # Connect the Menu button
            if primary == "MENU":
                button.clicked.connect(self.add_menu)

            # Connect the "2ND" button to toggle_secondary_state method
            if primary == "2ND":
                button.clicked.connect(self.toggle_secondary_state)

            # Connect number buttons to the input update method
            if primary in "123456789":
                button.clicked.connect(self.update_input)
                
            if primary in "+-*":
                button.clicked.connect(self.add_operator)
            
            if primary == "CLEAR":
                button.clicked.connect(self.clear_input)
                    
            # Connect the π button
            if primary == "π":
                button.clicked.connect(self.add_pi)
                
            # Connect the MOD button
            if primary == "MOD":
                button.clicked.connect(self.add_mod)
                    
            # Connect the LOG button to the add_log method
            if primary == "LOG":
                button.clicked.connect(self.add_log)
            
            # Connect LN
            if primary == "LN":
                button.clicked.connect(self.add_ln)
            
            # Connect 0
            if primary == "0":
                button.clicked.connect(self.add_zero)
                
            # Connect . button
            if primary == ".":
                button.clicked.connect(self.add_decimal)
                
            # Connect X^-1 button
            if primary == "X^-1":
                button.clicked.connect(self.add_inverse)
                
            # Connect X² button
            if primary == "X²":
                button.clicked.connect(self.add_square)
                
            # Connect ÷ button
            if primary == "÷":
                button.clicked.connect(self.add_divide)
                
            # Connect (-) button
            if primary == "(-)":
                button.clicked.connect(self.add_negate)
                
            # Connect ^ button
            if primary == "^":
                button.clicked.connect(self.add_power)
                
            # connect ( button
            if primary == "(":
                button.clicked.connect(self.add_open_parenthesis)
                
            # Connect ) button
            if primary == ")":
                button.clicked.connect(self.add_close_parenthesis)
                
            # Connect the prb button
            if primary == "PRB":
                button.clicked.connect(self.add_prb)
                
            # Connect the A B/C button
            if primary == "A B/C":
                button.clicked.connect(self.add_frac_conversion)
                
            # Connect the DRG button
            if primary == "DRG":
                button.clicked.connect(self.add_drg)
                
            # Connect the o'" button
            if primary == "° ' \"":
                button.clicked.connect(self.add_symbol_menu)
                
            # Connect the clrvar button
            if primary == "CLRVAR":
                button.clicked.connect(self.add_clrvar)
                
            # Connect the sto> button
            if primary == "STO>":
                button.clicked.connect(self.add_sto)
                
            # Conenct the Data button
            if primary == "DATA":
                button.clicked.connect(self.add_data)
                
            # Connect the statvar button
            if primary == "STATVAR":
                button.clicked.connect(self.add_statvar)
                
            # Connect buttons that need to add their text followed by "("
            if primary in ["SIN", "COS", "TAN"]:
                button.clicked.connect(self.add_with_parenthetical)
                
            # Connect delete button
            if primary == "DEL":
                button.clicked.connect(self.add_delete)
                
            # Connect the "ABS" button
            if primary == "ABS":
                button.clicked.connect(self.add_abs)
                
            # Connect the = button
            if primary == "=":
                button.clicked.connect(self.add_equals)

            # Set appropriate font size for buttons and labels
            button.setStyleSheet("font-size: 12px;")
            if label_secondary:
                label_secondary.setStyleSheet("font-size: 10px; color: gray;")
                
    def update_display_with_cursor(self):
        # Get the clean text without any formatting
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if not current_text:
            current_text = "0"
            self.cursor_position = 0
        
        # Special handling for menu cursor positions
        if self.is_in_menu and self.menu_type == "drg":
            # Ensure cursor is only at valid positions: 'd', 'r', 'g'
            valid_positions = [0, 6, 12]  # Positions of 'd', 'r', 'g'
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "sci_eng":
            # Ensure cursor is only at valid positions: 'f', 's', 'e'
            valid_positions = [0, 6, 12]  # Positions of 'f', 's', 'e'
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "fix":
            valid_positions = list(range(11))  # Positions 0-10 for F,0,1,2,3,4,5,6,7,8,9
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "sto" or self.menu_type == "rcl":
            # Ensure cursor is only at valid positions for memory letters: a, b, c, d, e, r
            valid_positions = [5, 7, 9, 11, 13, 15]  # Positions of letters in "STO: a b c d e r"
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "stat":
            # Ensure cursor is only at valid positions: '1', '2', 'c'
            valid_positions = [0, 6, 12]  # Positions of '1', '2', 'c'
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "reset_confirm":
            # Ensure cursor is only at valid positions: 'y', 'n'
            valid_positions = [16, 18]  # Positions of 'y', 'n'
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "symbol":
            # Ensure cursor is only at valid positions for symbols
            valid_positions = [0, 2, 4, 6, 8, 10]  # Positions of °, ', ", r, g, ►
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        elif self.menu_type == "r<>p":
            # Ensure cursor is only at valid positions
            valid_positions = [0, 5, 10, 15]  # Start of each option
            if self.cursor_position not in valid_positions:
                self.cursor_position = valid_positions[0]
        else:
            # Normal cursor position bounds checking
            if self.cursor_position >= len(current_text):
                self.cursor_position = len(current_text) - 1
            if self.cursor_position < 0:
                self.cursor_position = 0

        # Add underline to the character at cursor_position
        if current_text:
            new_text = (
                current_text[:self.cursor_position] +
                f"<u>{current_text[self.cursor_position]}</u>" +
                current_text[self.cursor_position + 1:]
            )
            self.display_input.setText(new_text)
        
        # After display update, ensure cursor is visible by scrolling the view
        QTimer.singleShot(0, self.ensure_cursor_visible)
        
        # Secondary state handling
        if self.secondary_state and not self._toggling_secondary:
            self._toggling_secondary = True  # Prevent recursion
            self.toggle_secondary_state()
            self._toggling_secondary = False

    def toggle_secondary_state(self):
        # When the 2ND button is pressed directly, we don't want to immediately toggle back
        self._toggling_secondary = True
        self.secondary_state = not self.secondary_state
        
        for (row, col), (button, label_secondary) in self.button_widgets.items():
            primary, secondary, _, _ = next((b for b in self.buttons if b[2] == row and b[3] == col), (None, None, None, None))
            if secondary:
                if self.secondary_state:
                    button.setText(secondary)
                    if label_secondary:
                        label_secondary.setText(primary)
                else:
                    button.setText(primary)
                    if label_secondary:
                        label_secondary.setText(secondary)
        
        # Invert the colors of the "2ND" button
        self.invert_2nd_button_color()
        self._toggling_secondary = False

    def invert_2nd_button_color(self):
        button_2nd, _ = self.button_widgets[(0, 1)]
        if self.secondary_state:
            button_2nd.setStyleSheet("background-color: black; color: white; font-size: 12px;")
        else:
            button_2nd.setStyleSheet("background-color: white; color: black; font-size: 12px;")
            
    def keyPressEvent(self, event: QKeyEvent):
        # Check for Ctrl+C to copy output text
        if event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            output_text = self.display_result.text()
            if output_text:
                # Copy to clipboard
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(output_text)                
            return
        
        # Handle special keys that should work in all modes
        if event.key() == Qt.Key_Space:
            # Toggle 2nd button functionality should always work
            self.invert_2nd_button_color()
            self.toggle_secondary_state()
            event.accept()  # Explicitly accept the event to prevent default handling
            return
            
        # Then check STATVAR menu handling
        if self.statvar_menu.active:
            # Check for Enter/Return FIRST (before left/right keys)
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                result_value = self.display_result.text()
                
                # Deactivate the menu
                self.statvar_menu.active = False
                self.statvar_menu.deactivate()
                
                # Copy the result to the input line
                self.display_input.setText(result_value)
                self.current_input = result_value
                
                # Position cursor at the end
                self.cursor_position = len(result_value) - 1
                self.update_display_with_cursor()
                return
                
            # Then check for left/right navigation
            if event.key() == Qt.Key_Left:
                menu_text, result = self.statvar_menu.navigate('left')
                self.display_input.setText(menu_text)
                self.cursor_position = self.statvar_menu.cursor_pos
                self.display_result.setText(str(result))
                self.update_display_with_cursor()
                return
                    
            if event.key() == Qt.Key_Right:
                menu_text, result = self.statvar_menu.navigate('right')
                self.display_input.setText(menu_text)
                self.cursor_position = self.statvar_menu.cursor_pos
                self.display_result.setText(str(result))
                self.update_display_with_cursor()
                return
        
        # Now process function key buffers BEFORE handling menu-specific inputs
        # This allows typing "sin", "log", etc. even in the K menu
        if Qt.Key_A <= event.key() <= Qt.Key_Z:
            self.key_buffer += event.text().lower()  # Store lowercase letter
            
            # Define function sequences
            function_sequences = {
                "sin": "sin(", "cos": "cos(", "tan": "tan(",  # Trig functions
                "asin": "sin^(-1)(", "acos": "cos^(-1)(", "atan": "tan^(-1)(",  # Inverse trig functions
                "hyp": "HYP(",  # Hyperbolic functions
                "npr": "nPr", "ncr": "nCr", "!": "!", # Combinatorial functions
                "log": "log(", "ln": "ln(",     # Logarithmic functions
                "sqrt": "√(", "xrt": "X√(",    # Root functions
                "pi": "π", "ans": "Ans",       # Constants
                "clear": "CLEAR", "memclr": "MEMCLR",  # Clear functions
                "fix": "FIX", "menu": "MENU", "abs": "ABS", # Other functions
                "deg": "deg", "rad": "rad", "grd": "grd", # Angle modes
                "ins": "INS",  # Insert mode
                "mod": "MOD"  # Modulus function
            }

            # Check if buffer matches a valid function
            for func in function_sequences:
                if self.key_buffer == func:
                    # Handle special functions that should execute even in K menu
                    special_functions = ["clear", "memclr", "fix", "menu"]
                    if func in special_functions:
                        # Execute the function directly, regardless of K menu
                        self.key_buffer = ""  # Reset buffer
                        if func == "clear":
                            self.clear_input()
                        elif func == "memclr":
                            self.memory_values = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
                            self.rand_value = 0
                            saved_input = self.current_input
                            self.display_input.setText("CLEARED")
                            QTimer.singleShot(1500, lambda: self.restore_input_after_clear(saved_input))
                        elif func == "fix":
                            self.add_fix()
                        elif func == "menu":
                            self.add_menu()
                        elif func == "ins":
                            self.insert_mode = not self.insert_mode
                        return
                    elif self.is_in_menu and self.menu_type == "k":
                        # In K menu - append the function to the K value
                        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
                        if "=" in current_text:
                            prefix, value_part = current_text.split("=", 1)
                            new_text = prefix + "=" + value_part + function_sequences[func]
                            self.display_input.setText(new_text)
                            self.current_input = new_text
                            self.cursor_position = len(new_text) - 1
                            self.update_display_with_cursor()
                    elif self.is_in_menu and self.menu_type == "mod":
                        current_text = self.display_input.text()
                        value_part = ""
                        
                        # Extract value part after the = sign
                        if "=" in current_text:
                            clean_text = current_text.replace("<u>", "").replace("</u>", "")
                            prefix, value_part = clean_text.split("=", 1)
                        
                        # Modified backspace behavior
                        if len(value_part) == 1:
                            # Only one character, delete it
                            value_part = ""
                        elif value_part:
                            # More than one character, delete last one
                            value_part = value_part[:-1]
                        
                        # Update the MOD value in real-time
                        self.update_mod_field(value_part)
                        return
                    else:
                        # Regular function insertion
                        self.insert_function(function_sequences[func])
                    
                    self.key_buffer = ""  # Reset buffer after match
                    return

            # If buffer is too long or invalid, reset it
            if not any(k.startswith(self.key_buffer) for k in function_sequences):
                self.key_buffer = ""
                # But don't return - continue processing the character normally
        
        # NOW handle K menu specific input for normal characters
        if self.is_in_menu and self.menu_type == "k":
            # For letters, rely ONLY on the key_buffer handling above
            # Only handle non-letter printable characters here
            if event.text().isprintable() and not (Qt.Key_A <= event.key() <= Qt.Key_Z):
                # Only process non-letter characters directly
                current_text = self.display_input.text()
                value_part = ""
                
                # Extract value part after the = sign
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                    
                # Add the new character
                value_part += event.text()
                
                # Update the K value in real-time
                self.update_k_field(value_part)
                return
            
            elif event.key() == Qt.Key_Backspace:
                current_text = self.display_input.text()
                value_part = ""
                
                # Extract value part after the = sign
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                
                # Modified backspace behavior
                if len(value_part) == 1:
                    # Only one character, delete it
                    value_part = ""
                elif value_part:
                    # More than one character, delete last one
                    value_part = value_part[:-1]
                
                # Update the K value in real-time
                self.update_k_field(value_part)
                return
        elif self.is_in_menu and self.menu_type == "mod":
            # Only accept numbers for modulo input
            if event.text().isdigit():
                # Get current text
                current_text = self.display_input.text()
                value_part = ""
                
                # Extract value part after the = sign
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                
                # Add the new digit
                value_part += event.text()
                
                # Update the MOD value in real-time
                self.update_mod_field(value_part)
                return
            
            # Handle backspace for modulus menu
            elif event.key() == Qt.Key_Backspace:
                current_text = self.display_input.text()
                value_part = ""
                
                # Extract value part after the = sign
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                
                # Modified backspace behavior
                if len(value_part) == 1:
                    # Only one character, delete it
                    value_part = ""
                elif value_part:
                    # More than one character, delete last one
                    value_part = value_part[:-1]
                
                # Update the MOD value in real-time
                self.update_mod_field(value_part)
                return
    
        # Check STATVAR menu first - before any other menu checks
        if self.statvar_menu.active:
            # Check for Enter/Return FIRST (before left/right keys)
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                result_value = self.display_result.text()
                
                # Deactivate the menu
                self.statvar_menu.active = False
                self.statvar_menu.deactivate()
                
                # Copy the result to the input line
                self.display_input.setText(result_value)
                self.current_input = result_value
                
                # Position cursor at the end
                self.cursor_position = len(result_value) - 1
                self.update_display_with_cursor()
                return
                
            # Then check for left/right navigation
            if event.key() == Qt.Key_Left:
                menu_text, result = self.statvar_menu.navigate('left')
                self.display_input.setText(menu_text)
                self.cursor_position = self.statvar_menu.cursor_pos
                self.display_result.setText(str(result))
                self.update_display_with_cursor()
                return
                    
            if event.key() == Qt.Key_Right:
                menu_text, result = self.statvar_menu.navigate('right')
                self.display_input.setText(menu_text)
                self.cursor_position = self.statvar_menu.cursor_pos
                self.display_result.setText(str(result))
                self.update_display_with_cursor()
                return
                
        # Then check for stat data entry mode
        if self.stat_manager.in_data_entry:
            if event.key() in [Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, 
                            Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9,
                            Qt.Key_Period, Qt.Key_Minus]:
                
                current_text = self.display_input.text()
                value_part = ""
                
                # Extract value part after the = sign
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                    
                # Add the new digit
                value_part += event.text()
                
                # Update the value in real-time
                self.update_stat_field(value_part)
                return
                
            elif event.key() == Qt.Key_Backspace:
                current_text = self.display_input.text()
                value_part = ""
                
                # Extract value part after the = sign
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                
                # Modified backspace behavior
                if len(value_part) == 1:
                    # Only one character, delete it
                    value_part = ""
                elif value_part:
                    # More than one character, delete last one
                    value_part = value_part[:-1]
                
                # Update the value in real-time
                self.update_stat_field(value_part)
                return
                
            if event.key() == Qt.Key_Up:
                success, prompt = self.stat_manager.navigate_up()
                if success:
                    self.display_input.setText(prompt)
                    self.current_input = prompt
                    self.cursor_position = len(prompt) - 1
                    self.update_display_with_cursor()
                return
            
            if event.key() == Qt.Key_Down:
                success, prompt = self.stat_manager.navigate_down()
                if success:
                    self.display_input.setText(prompt)
                    self.current_input = prompt
                    self.cursor_position = len(prompt) - 1
                    self.update_display_with_cursor()
                return
            
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # In data entry mode, Enter adds the current value
                current_text = self.display_input.text()
                
                # Extract value part after the = sign
                value_part = ""
                if "=" in current_text:
                    value_part = current_text.split("=")[1].strip()
                
                if value_part:
                    success, next_prompt = self.stat_manager.add_data_point(value_part)
                    if success:
                        self.display_input.setText(next_prompt)
                        self.current_input = next_prompt
                        self.cursor_position = len(next_prompt) - 1
                        self.update_display_with_cursor()
                return
        
        # Handle menu-specific navigation
        if self.is_in_menu and self.menu_type == "reset_confirm":
            if event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
                # Toggle between 'y' and 'n'
                if self.cursor_position == 16:  # At 'y'
                    self.cursor_position = 18  # Move to 'n'
                else:
                    self.cursor_position = 16  # Move to 'y'
                self.update_display_with_cursor()
                return
        if self.is_in_menu and self.menu_type == "drg":
            if event.key() == Qt.Key_Left:
                # Navigate between deg, rad, grd options (left)
                if self.cursor_position == 0:  # At 'd' in 'deg'
                    self.cursor_position = 12  # Move to 'g' in 'grd' 
                elif self.cursor_position == 6:  # At 'r' in 'rad'
                    self.cursor_position = 0   # Move to 'd' in 'deg'
                elif self.cursor_position == 12:  # At 'g' in 'grd'
                    self.cursor_position = 6   # Move to 'r' in 'rad'
                self.update_display_with_cursor()
                return
                
            if event.key() == Qt.Key_Right:
                # Navigate between deg, rad, grd options (right)
                if self.cursor_position == 0:  # At 'd' in 'deg'
                    self.cursor_position = 6   # Move to 'r' in 'rad'
                elif self.cursor_position == 6:  # At 'r' in 'rad'
                    self.cursor_position = 12  # Move to 'g' in 'grd'
                elif self.cursor_position == 12:  # At 'g' in 'grd'
                    self.cursor_position = 0   # Move to 'd' in 'deg'
                self.update_display_with_cursor()
                return
            
        if self.is_in_menu and self.menu_type == "sci_eng":
            if event.key() == Qt.Key_Left:
                # Navigate between flo, sci, eng options (left)
                if self.cursor_position == 0:  # At 'f' in 'flo'
                    self.cursor_position = 12  # Move to 'e' in 'eng' 
                elif self.cursor_position == 6:  # At 's' in 'sci'
                    self.cursor_position = 0   # Move to 'f' in 'flo'
                elif self.cursor_position == 12:  # At 'e' in 'eng'
                    self.cursor_position = 6   # Move to 's' in 'sci'
                self.update_display_with_cursor()
                return
                
            if event.key() == Qt.Key_Right:
                # Navigate between flo, sci, eng options (right)
                if self.cursor_position == 0:  # At 'f' in 'flo'
                    self.cursor_position = 6   # Move to 's' in 'sci'
                elif self.cursor_position == 6:  # At 's' in 'sci'
                    self.cursor_position = 12  # Move to 'e' in 'eng'
                elif self.cursor_position == 12:  # At 'e' in 'eng'
                    self.cursor_position = 0   # Move to 'f' in 'flo'
                self.update_display_with_cursor()
                return
            
        if self.is_in_menu and self.menu_type == "fix":
            if event.key() == Qt.Key_Left:
                # Navigate within fix options (left)
                self.cursor_position = (self.cursor_position - 1) % 11
                self.update_display_with_cursor()
                return
                
            if event.key() == Qt.Key_Right:
                # Navigate within fix options (right)
                self.cursor_position = (self.cursor_position + 1) % 11
                self.update_display_with_cursor()
                return
            
        if self.is_in_menu and (self.menu_type == "sto" or self.menu_type == "rcl"):
            if event.key() == Qt.Key_Left:
                # Navigate memory options (left)
                # Valid positions are at the letters: a(5), b(7), c(9), d(11), e(13), r(15)
                positions = [5, 7, 9, 11, 13, 15]
                current_index = positions.index(self.cursor_position) if self.cursor_position in positions else 0
                self.cursor_position = positions[(current_index - 1) % len(positions)]
                self.update_display_with_cursor()
                return
                
            if event.key() == Qt.Key_Right:
                # Navigate memory options (right)
                positions = [5, 7, 9, 11, 13, 15]
                current_index = positions.index(self.cursor_position) if self.cursor_position in positions else 0
                self.cursor_position = positions[(current_index + 1) % len(positions)]
                self.update_display_with_cursor()
                return
            
        if self.is_in_menu and self.menu_type == "stat":
            if event.key() == Qt.Key_Left:
                # Navigate between 1-var, 2-var, clrdata options (left)
                if self.cursor_position == 0:  # At '1' in '1-var'
                    self.cursor_position = 12  # Move to 'c' in 'clrdata'
                elif self.cursor_position == 6:  # At '2' in '2-var'
                    self.cursor_position = 0   # Move to '1' in '1-var'
                elif self.cursor_position == 12:  # At 'c' in 'clrdata'
                    self.cursor_position = 6   # Move to '2' in '2-var'
                self.update_display_with_cursor()
                return
                    
            if event.key() == Qt.Key_Right:
                # Navigate between 1-var, 2-var, clrdata options (right)
                if self.cursor_position == 0:  # At '1' in '1-var'
                    self.cursor_position = 6   # Move to '2' in '2-var'
                elif self.cursor_position == 6:  # At '2' in '2-var'
                    self.cursor_position = 12  # Move to 'c' in 'clrdata'
                elif self.cursor_position == 12:  # At 'c' in 'clrdata'
                    self.cursor_position = 0   # Move to '1' in '1-var'
                self.update_display_with_cursor()
                return
            
        if self.is_in_menu and self.menu_type == "prb":
            if event.key() == Qt.Key_Left:
                if self.cursor_position == 0:
                    self.cursor_position = 15
                elif self.cursor_position == 4:
                    self.cursor_position = 0
                elif self.cursor_position == 8:
                    self.cursor_position = 4
                elif self.cursor_position == 10:
                    self.cursor_position = 8
                elif self.cursor_position == 15:
                    self.cursor_position = 10
                self.update_display_with_cursor()
                return
            
            if event.key() == Qt.Key_Right:
                if self.cursor_position == 0:
                    self.cursor_position = 4
                elif self.cursor_position == 4:
                    self.cursor_position = 8
                elif self.cursor_position == 8:
                    self.cursor_position = 10
                elif self.cursor_position == 10:
                    self.cursor_position = 15
                elif self.cursor_position == 15:
                    self.cursor_position = 0
                self.update_display_with_cursor()
                return
        if self.is_in_menu and self.menu_type == "symbol":
            if event.key() == Qt.Key_Left:
                # Navigate between symbols (left)
                valid_positions = [0, 2, 4, 6, 8, 10]
                current_index = valid_positions.index(self.cursor_position) if self.cursor_position in valid_positions else 0
                self.cursor_position = valid_positions[(current_index - 1) % len(valid_positions)]
                self.update_display_with_cursor()
                return
                    
            if event.key() == Qt.Key_Right:
                # Navigate between symbols (right)
                valid_positions = [0, 2, 4, 6, 8, 10]
                current_index = valid_positions.index(self.cursor_position) if self.cursor_position in valid_positions else 0
                self.cursor_position = valid_positions[(current_index + 1) % len(valid_positions)]
                self.update_display_with_cursor()
                return
        if self.is_in_menu and self.menu_type == "r<>p":
            if event.key() == Qt.Key_Left:
                # Navigate between options (left)
                valid_positions = [0, 5, 10, 15]
                current_index = valid_positions.index(self.cursor_position) if self.cursor_position in valid_positions else 0
                self.cursor_position = valid_positions[(current_index - 1) % len(valid_positions)]
                self.update_display_with_cursor()
                return
                    
            if event.key() == Qt.Key_Right:
                # Navigate between options (right)
                valid_positions = [0, 5, 10, 15]
                current_index = valid_positions.index(self.cursor_position) if self.cursor_position in valid_positions else 0
                self.cursor_position = valid_positions[(current_index + 1) % len(valid_positions)]
                self.update_display_with_cursor()
                return
        
        if not self.is_in_menu and not self.stat_manager.in_data_entry:
            if event.key() == Qt.Key_Up:
                # Navigate backward in history
                if self.session_memory:
                    if self.history_index < len(self.session_memory) - 1:
                        self.history_index += 1
                    else:
                        self.history_index = len(self.session_memory) - 1
                    
                    # Display the historical expression
                    historical_expr = self.session_memory[len(self.session_memory) - 1 - self.history_index]
                    self.display_input.setText(historical_expr)
                    self.current_input = historical_expr
                    self.cursor_position = len(historical_expr) - 1
                    self.update_display_with_cursor()
                    return
                    
            elif event.key() == Qt.Key_Down:
                # Navigate forward in history
                if self.history_index > 0:
                    self.history_index -= 1
                    historical_expr = self.session_memory[len(self.session_memory) - 1 - self.history_index]
                    self.display_input.setText(historical_expr)
                    self.current_input = historical_expr
                    self.cursor_position = len(historical_expr) - 1
                    self.update_display_with_cursor()
                elif self.history_index == 0:
                    # Return to empty input
                    self.history_index = -1
                    self.display_input.setText("0")
                    self.current_input = "0"
                    self.cursor_position = 0
                    self.update_display_with_cursor()
                return
        
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.add_equals()
            self.cursor_position = len(self.display_input.text()) - 1
            self.update_display_with_cursor()
            return
        
        if event.key() == Qt.Key_Space:
            # Toggle 2nd button functionality
            self.invert_2nd_button_color()
            self.toggle_secondary_state()
            event.accept()  # Explicitly accept the event to prevent default handling
            return
        
        if event.key() == Qt.Key_Apostrophe:
            self.update_input_state("'")
            
        if event.key() == Qt.Key_QuoteDbl:
            self.update_input_state("\"")
            
        if event.key() == Qt.Key_Exclam:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            if current_text == "0":
                self.update_input_state("Ans!")
            else:
                self.update_input_state("!")
    
        key_to_text = {
            Qt.Key_0: "0", Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3",
            Qt.Key_4: "4", Qt.Key_5: "5", Qt.Key_6: "6", Qt.Key_7: "7",
            Qt.Key_8: "8", Qt.Key_9: "9", Qt.Key_Period: ".",
            Qt.Key_ParenLeft: "(", Qt.Key_ParenRight: ")",
            Qt.Key_Percent: "%", Qt.Key_Comma: ","
        }
        
        straight_operators = {
            Qt.Key_Plus: "+", Qt.Key_Minus: "-", Qt.Key_Asterisk: "*"
        }
        
        if event.key() == Qt.Key_Left:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            func, start, _ = self.is_in_function_token(current_text, self.cursor_position)
            
            if func and self.cursor_position > start:
                # If inside a function, jump to its start
                self.cursor_position = start
            else:
                # Normal left movement
                self.cursor_position = max(0, self.cursor_position - 1)
            self.update_display_with_cursor()
            return
            
        if event.key() == Qt.Key_Right:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            func, _, end = self.is_in_function_token(current_text, self.cursor_position) 
            
            if func and self.cursor_position < end - 1:
                # If inside a function, jump to its end
                self.cursor_position = end - 1
            else:
                # Normal right movement
                self.cursor_position = min(len(current_text) - 1, self.cursor_position + 1)
            self.update_display_with_cursor()
            return
        
        if event.key() in key_to_text:
            new_text = key_to_text[event.key()]            
            self.update_input_state(new_text, replace_zero=(new_text != "0"))
            
        if event.key() in straight_operators:
            key_value = event.key()  # Extract the key value first
            dummy_sender = QObject()
            dummy_sender.text = lambda key=key_value: straight_operators[key]
            
            self.add_operator(dummy_sender)
        
        if event.key() == Qt.Key_Slash:
            dummy_sender = QObject()
            dummy_sender.text = lambda: "÷"  
            
            self.add_operator(dummy_sender)
            
        if event.key() == Qt.Key_AsciiCircum:
            dummy_sender = QObject()
            dummy_sender.text = lambda: "^"
            
            self.add_carrot(dummy_sender)
            
        if event.key() == Qt.Key_Equal:
            self.add_equals()
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
            
        if event.key() == Qt.Key_Delete:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            func, start, end = self.is_in_function_token(current_text, self.cursor_position)
            
            # Special handling for stat data entry mode
            if self.stat_manager.in_data_entry:
                if self.is_protected_prefix_position(current_text, self.cursor_position):
                    # Don't allow deletion of the prefix
                    return
            
            if func:
                # Delete the entire function
                new_text = current_text[:start] + current_text[end:]
                if new_text == "":
                    new_text = "0"
                    
                self.display_input.setText(new_text)
                self.current_input = new_text
                self.cursor_position = min(start, len(new_text) - 1)
            else:
                if current_text != "0" and len(current_text) > 0 and not self.is_in_menu:  # Disable delete in menus
                    new_text = current_text[:self.cursor_position] + current_text[self.cursor_position + 1:]
                    if new_text == "":
                        new_text = "0"
                    
                    self.display_input.setText(new_text)
                    self.current_input = new_text
                    
                    self.cursor_position = min(self.cursor_position, len(new_text) - 1)
                    
                self.update_display_with_cursor()
                return
        
        if event.key() == Qt.Key_Backspace:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            
            # Special handling for stat data entry mode
            if self.stat_manager.in_data_entry:
                if self.is_protected_prefix_position(current_text, self.cursor_position):
                    # Don't allow deletion of the prefix
                    return
                    
                # Regular backspace behavior for values after the = sign
                value_part = ""
                if "=" in current_text:
                    clean_text = current_text.replace("<u>", "").replace("</u>", "")
                    prefix, value_part = clean_text.split("=", 1)
                    
                # Remove last character
                value_part = value_part[:-1] if value_part else ""
                
                # Update the value in real-time
                self.update_stat_field(value_part)
                return
            
            # Normal backspace behavior for non-stat modes
            if current_text != "0" and len(current_text) > 0:
                if len(current_text) == 1:
                    # If only one character left, replace with 0
                    new_text = "0"
                    self.cursor_position = 0
                elif self.cursor_position > 0:
                    # Otherwise delete character before cursor
                    new_text = current_text[:self.cursor_position - 1] + current_text[self.cursor_position:]
                    if new_text == "":
                        new_text = "0"
                    self.cursor_position = max(0, self.cursor_position - 1)
                else:
                    # Cursor at beginning, nothing to delete
                    return
                    
                self.display_input.setText(new_text)
                self.current_input = new_text
                
            self.update_display_with_cursor()
            return

    def update_input(self):
        if self.is_in_menu:
            return
            
        sender = self.sender()
        button_text = sender.text()
        
        self.update_input_state(button_text)
        
        self.current_input = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
    def clear_input(self):
        if self.is_in_menu and self.menu_type == "k":
            # Get current K menu content
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            
            if current_text == "K=" or len(current_text) <= 2:
                # No text after K=, exit the menu
                self.is_in_menu = False
                self.menu_type = None
                self.display_input.setText("")
                self.current_input = "0"  # Keep internal state as "0"
            else:
                # Clear text after K=
                self.display_input.setText("K=")
                self.cursor_position = 2  # Position after K=
            
            self.update_display_with_cursor()
            return
        
        if self.is_in_menu and self.menu_type == "mod":
            # Get current MOD menu content
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            
            if current_text == "MODULUS=" or len(current_text) <= 8:
                # No text after MOD=, exit the menu
                self.is_in_menu = False
                self.menu_type = None
                self.display_input.setText("")
                self.current_input = "0"
            else:
                # Clear text after MOD=
                self.display_input.setText("MODULUS=")
                self.cursor_position = 8
            
            self.update_display_with_cursor()
            return
    
        if self.is_in_menu:
            self.is_in_menu = False
            self.menu_type = None
            self.display_input.setText(self.current_input)
            self.cursor_position = 0
            self.update_display_with_cursor()
            return
        
        # Special handling for stat data entry mode
        if self.stat_manager.in_data_entry:
            current_text = self.display_input.text()
            if "=" in current_text:
                # Keep the prompt part but clear the value
                prefix = current_text.split("=")[0] + "="
                self.display_input.setText(prefix)
                self.current_input = prefix
                self.cursor_position = len(prefix) - 1
                
                self.update_display_with_cursor()
            return
        
        # Normal clear behavior for non-stat modes
        self.history_index = -1
        self.display_input.setText("0")
        self.display_result.setText("")
        self.cursor_position = 0
        
        if self.secondary_state:
            self.display_input.setText("0")
            self.display_result.setText("")
            self.cursor_position = 0
            self.ans = "0"
            self.memory_values = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
            self.rand_value = 0
            self.session_memory = []
            self.history_index = -1
        
        self.current_input = "0"
        self.update_display_with_cursor()
            
    def add_operator(self, custom_sender=None):
        if self.is_in_menu:
            return
        
        if self.display_result.text() != "":
            self.clear_input()
            
        sender = custom_sender or self.sender()
        button_text = sender.text()
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if current_text == "0":
            # Special case for operators - use "Ans" with operator
            new_text = "Ans" + button_text
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        else:
            # Use the helper for normal case
            self.update_input_state(button_text)
            
    def add_carrot(self, custom_sender=None):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
        
        sender = custom_sender or self.sender()
        button_text = sender.text()
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if current_text == "0":
            new_text = "Ans" + button_text
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        else:
            self.update_input_state(button_text)
            
    def insert_function(self, func_name: str):
        if self.display_result.text() != "":
            self.clear_input()
            
        if func_name == "CLEAR":
            self.clear_input()
            return
        
        if func_name == "FIX":
            self.add_fix()
            return
        
        if func_name == "MENU":
            self.add_menu()
            return
        
        if func_name == "ABS":
            self.add_abs()
            return
        
        if func_name == "INS":
            self.insert_mode = not self.insert_mode
            self.update_status_bar()
            return
        
        if func_name == "HYP":
            self.is_in_hyp = not self.is_in_hyp
            self.update_status_bar()
            return
        
        if func_name == "MOD":
            self.add_mod()
            return
            
        if func_name == "deg":
            self.angle_mode = "deg"
            self.update_status_bar()
            return
        
        if func_name == "rad":
            self.angle_mode = "rad"
            self.update_status_bar()
            return
        
        if func_name == "grd":
            self.angle_mode = "grd"
            self.update_status_bar()
            return            
        
        self.update_input_state(func_name, replace_zero=True)
            
    def insert_xrt(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.display_input.text().replace("<u>", "").replace("</u>", "") == "0":
            new_text = "AnsX√("
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
        else:
            self.update_input_state("X√(")
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
        self.update_display_with_cursor()

    def add_with_parenthetical(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        sender = self.sender()
        button_text = sender.text().lower() + "("
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        self.update_input_state(button_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_log(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = "10^("
        else:
            new_text = "log("
        
        self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_ln(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = "e^("
        else:
            new_text = "ln("
        
        self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()

    def add_zero(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            # Show confirmation prompt instead of immediate reset
            self.pre_menu_input = self.current_input
            new_text = "reset all data? y n"
            self.is_in_menu = True
            self.menu_type = "reset_confirm"
            
            self.display_input.setText(new_text)
            self.cursor_position = 15  # Position cursor at 'y'
            self.update_display_with_cursor()
        else:
            new_text = "0"
            replace_zero = (new_text != "0")
            self.update_input_state(new_text, replace_zero=replace_zero)
        
        if self.secondary_state:
            self.toggle_secondary_state()
        
    def add_fix(self):
        # Save the current input before entering menu mode
        self.pre_menu_input = self.current_input
        
        new_text = "F0123456789"
        self.is_in_menu = True
        self.menu_type = "fix"
        
        self.display_input.setText(new_text)
        self.cursor_position = 0  # Start cursor at F (default)
        self.update_display_with_cursor()
            
    def add_decimal(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            self.add_fix()
            return
        else:
            new_text = "."
        
        self.update_input_state(new_text, replace_zero=False)
        
        if self.secondary_state:
            self.toggle_secondary_state()
                
    def add_inverse(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "E"
        else:
            new_text = "^(-1)"
        
        if current_text == "0" and new_text == "^(-1)":
            new_text = "Ans^(-1)"
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        else:
            self.update_input_state(new_text, replace_zero=True)
            
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_square(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = "√("
        else:
            new_text = "^2"
        
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if current_text == "0" and new_text == "^2":
            new_text = "Ans^2"
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        else:
            self.update_input_state(new_text, replace_zero=True)
            
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_divide(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
                
        if self.secondary_state:
            if self.k_mode_active:
                # If already in K mode, exit K mode
                self.k_mode_active = False
                self.k_value = ""
                self.update_status_bar()
            else:
                new_text = "K="
                self.push_menu_state("k")  # Use push_menu_state
                self.display_input.setText(new_text)
                self.cursor_position = 2  # Position cursor after "K="
                self.update_display_with_cursor()
        else:
            # Regular divide functionality (unchanged)
            new_text = "÷"
            
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            if current_text == "0" and new_text == "÷":
                new_text = "Ans÷"
                self.display_input.setText(new_text)
                self.current_input = new_text
                self.cursor_position = len(new_text) - 1
                self.update_display_with_cursor()
            else:
                self.update_input_state(new_text)
                
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_mod(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.mod_mode_active:
            self.mod_mode_active = False
            self.mod_value = ""
            self.update_status_bar()
        else:
            new_text = "MODULUS="
            self.push_menu_state("mod")  # Use push_menu_state
            self.display_input.setText(new_text)
            self.cursor_position = 8  # Position cursor after "MODULUS="
            self.update_display_with_cursor()
            
    def add_negate(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = "Ans"
        else:
            new_text = "(-)"
        
        self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_power(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = "X√("
        else:
            new_text = "^"
        
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if current_text == "0":
            new_text = "Ans" + new_text
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        else:
            self.update_input_state(new_text)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_open_parenthesis(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = "%"
        else:
            new_text = "("
        
        self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_close_parenthesis(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            new_text = ","
        else:
            new_text = ")"
        
        self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_prb(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "►f↔d"  
        else:
            # Save current input before entering menu
            self.pre_menu_input = self.current_input
            
            # Use push_menu_state instead of directly setting menu variables
            new_text = "nPr nCr ! rand randi"
            self.push_menu_state("prb")
            
            self.display_input.setText(new_text)
            self.cursor_position = 0  # Position at 'n' in nPr
            self.update_display_with_cursor()
            return
        
        if current_text == "0" and new_text == "►f↔d":
            # Special case for f<>d with empty display - use Ans
            self.display_input.setText("Ans" + new_text)
            self.current_input = "Ans" + new_text
            self.cursor_position = len("Ans" + new_text) - 1
            self.update_display_with_cursor()
        else:
            # Use the helper for both PRB and normal f<>d cases
            self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_frac_conversion(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "►A B/C↔D/E"
        else:
            new_text = "┘"
        
        if current_text == "0" and new_text == "►A B/C↔D/E":
            # Special case for fraction format with empty display - use Ans
            self.display_input.setText("Ans" + new_text)
            self.current_input = "Ans" + new_text
            self.cursor_position = len("Ans" + new_text) - 1
            self.update_display_with_cursor()
        else:
            # Use the helper for both mixed fraction and normal conversion cases
            self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_drg(self):
        if self.display_result.text() != "":
            self.clear_input()
        if self.secondary_state:
            new_text = "flo | sci | eng"
            self.is_in_menu = True
            self.menu_type = "sci_eng"
        else:
            new_text = "deg | rad | grd"
            self.is_in_menu = True
            self.menu_type = "drg"
        
        self.display_input.setText(new_text)
        self.cursor_position = 0  # Start cursor at the beginning
        self.update_display_with_cursor()
        
    def add_symbol_menu(self):
        # Save the current input before entering menu mode
        self.pre_menu_input = self.current_input
        if self.display_result.text() != "":
            self.clear_input()
        
        if self.secondary_state:
            new_text = "R►Pr R►Pθ P►Rx P►Ry"
            self.push_menu_state("r<>p")  # Use push_menu_state
        else:
            new_text = "° ' \" r g ►DMS"
            self.push_menu_state("symbol")  # Use push_menu_state
        
        self.display_input.setText(new_text)
        self.cursor_position = 0  # Start cursor at the first symbol
        self.update_display_with_cursor()
        
    def add_clrvar(self):
        if self.secondary_state:
            return
        else:
            saved_input = self.current_input
            
            self.memory_values = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
            self.rand_value = 0
            
            self.display_input.setText("CLEARED")
            self.cursor_position = len("CLEARED") - 1
            self.update_display_with_cursor()
            
            QTimer.singleShot(1500, lambda: self.restore_input_after_clear(saved_input))

    def restore_input_after_clear(self, saved_input):
        self.display_input.setText(saved_input)
        self.current_input = saved_input
        self.cursor_position = len(saved_input) - 1
        self.update_display_with_cursor()
        
    def add_sto(self):
        self.pre_menu_input = self.current_input
        
        if self.secondary_state:
            new_text = "RCL: a b c d e r"
            # Use push_menu_state instead of directly setting menu variables
            self.push_menu_state("rcl")
        else:
            new_text = "STO: a b c d e r"
            # Use push_menu_state instead of directly setting menu variables
            self.push_menu_state("sto")
        
        self.display_input.setText(new_text)
        self.cursor_position = 5  # Position cursor at 'a'
        self.update_display_with_cursor()
        
    def add_data(self):
        if self.secondary_state:
            # Save the current input before entering menu mode
            self.pre_menu_input = self.current_input
            
            new_text = "1-var 2-var clrdata"
            self.is_in_menu = True
            self.menu_type = "stat"
            
            self.display_input.setText(new_text)
            self.cursor_position = 0  # Position cursor at '1' in 1-var
            self.update_display_with_cursor()
        else:
            # Only activate if we're in stat mode
            if not self.stat_manager.in_stat_mode:
                self.display_input.setText("STAT ERROR")
                self.cursor_position = len("STAT ERROR") - 1
                QTimer.singleShot(1500, lambda: self.display_input.setText("0"))
                self.update_display_with_cursor()
                return
                
            # Toggle data entry mode
            if self.stat_manager.in_data_entry:
                # Exit data entry mode but stay in stat mode
                self.stat_manager.in_data_entry = False
                self.display_input.setText("0")
                self.current_input = "0"
                self.cursor_position = 0
            else:
                # Start data entry
                success, prompt = self.stat_manager.start_data_entry()
                if success:
                    self.display_input.setText(prompt)
                    self.cursor_position = len(prompt) - 1
                    # Clear the result display for data entry
                    self.display_result.setText("")
            
            self.update_display_with_cursor()
        
    def add_statvar(self):
        if self.secondary_state:
            # Exit STAT mode
            if self.stat_manager.in_stat_mode:
                self.stat_manager.exit_stat_mode()
                self.update_status_bar()
                self.display_input.setText("0")
                self.current_input = "0"
                self.cursor_position = 0
                self.update_display_with_cursor()
            else: # Not in stat mode
                self.display_input.setText("STAT ERROR")
                self.cursor_position = len("STAT ERROR") - 1
                self.update_display_with_cursor()
        else:
            # Show statistical variables menu (if in stat mode)
            if self.stat_manager.in_stat_mode:
                self.is_in_menu = True
                if self.statvar_menu.active:
                    # Menu already active, just update display
                    menu_text, result = self.statvar_menu.navigate('right')
                else:
                    # Activate the menu
                    menu_text, result = self.statvar_menu.activate(
                        self.stat_manager.stat_mode, self.stat_manager)
                
                if menu_text:
                    self.display_input.setText(menu_text)
                    self.cursor_position = self.statvar_menu.cursor_pos
                    self.display_result.setText(str(result))
                    self.update_display_with_cursor()
            else: # Not in stat mode
                self.display_input.setText("STAT ERROR")
                self.cursor_position = len("STAT ERROR") - 1
                self.update_display_with_cursor()
        
    def add_pi(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        if self.secondary_state:
            self.is_in_hyp = not self.is_in_hyp
            self.update_status_bar()
            self.toggle_secondary_state()
            return
        else:
            new_text = "π"
            # Use the helper for normal π insertion
            self.update_input_state(new_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_delete(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if self.secondary_state and not self.is_in_menu:  # Prevent toggling insert mode in menus
            # Toggle insert mode
            self.insert_mode = not self.insert_mode

            self.update_status_bar()
            
            # Turn off 2nd mode when insert mode is toggled
            if self.secondary_state:
                self.secondary_state = False
                self.invert_2nd_button_color()
                self.toggle_secondary_state()  # Update all the button text
            
            self.update_display_with_cursor()
        else:
            # Always delete character at cursor position, regardless of insert mode
            if current_text != "0" and len(current_text) > 0 and not self.is_in_menu:  # Disable delete in menus
                # Delete the character at the cursor position
                new_text = current_text[:self.cursor_position] + current_text[self.cursor_position + 1:]
                if new_text == "":
                    new_text = "0"
                    
                # Update both display and internal input state
                self.display_input.setText(new_text)
                self.current_input = new_text  # Add this line to update input state tracking
                
                # Keep cursor at the same position (or adjust if needed)
                self.cursor_position = min(self.cursor_position, len(new_text) - 1)
                
            self.update_display_with_cursor()
            
    def add_abs(self):
        if self.is_in_menu:
            return
        if self.display_result.text() != "":
            self.clear_input()
            
        self.update_input_state("abs(")
        
        self.update_display_with_cursor()
            
    def insert_or_append_text(self, current_text, new_text):
        if self.insert_mode:
            # Insert at cursor position
            result = current_text[:self.cursor_position + 1] + new_text + current_text[self.cursor_position + 1:]
            # Move cursor to after the inserted text
            self.cursor_position += len(new_text)
            return result
        else:
            # Normal append mode
            return current_text + new_text
        
    def add_menu(self):
        manual_window = ManualWindow(self)
        manual_window.exec()
            
    def add_equals(self):
        # Handle STATVAR menu first (because it overrides other behavior)
        if self.statvar_menu.active:
            result_value = self.display_result.text()
            
            # Deactivate the menu
            self.statvar_menu.active = False
            self.statvar_menu.deactivate()
            
            # Copy the result to the input line
            self.display_input.setText(result_value)
            self.current_input = result_value
            
            # Position cursor at the end
            self.cursor_position = len(result_value) - 1
            self.update_display_with_cursor()
            return
        # Handle menu selection if in a menu
        if self.is_in_menu:
            if self.menu_type == "drg":
                # Get current selection based on cursor position
                if self.cursor_position == 0:  # First option (deg)
                    self.angle_mode = "deg"
                elif self.cursor_position == 6:  # Second option (rad)
                    self.angle_mode = "rad" 
                elif self.cursor_position == 12:  # Third option (grd)
                    self.angle_mode = "grd"
                    
                self.update_status_bar()
                    
                # Exit menu mode and return to calculator
                self.is_in_menu = False
                self.menu_type = None
                self.display_input.setText("0")
                self.cursor_position = 0
                self.update_display_with_cursor()
                return
            elif self.menu_type == "sci_eng":
                # Get current selection based on cursor position
                if self.cursor_position == 0:  # First option (flo)
                    self.output_format = "flo"
                elif self.cursor_position == 6:  # Second option (sci)
                    self.output_format = "sci" 
                elif self.cursor_position == 12:  # Third option (eng)
                    self.output_format = "eng"
                    
                self.update_status_bar()
                    
                # Exit menu mode and return to calculator
                self.is_in_menu = False
                self.menu_type = None
                self.display_input.setText("0")
                self.cursor_position = 0
                self.update_display_with_cursor()
                return
            elif self.menu_type == "fix":
                # Get current selection based on cursor position
                if self.cursor_position == 0:  # F - Flexible decimal places
                    self.decimal_places = None
                else:
                    # 0-9 correspond to positions 1-10
                    self.decimal_places = self.cursor_position - 1
                    
                self.update_status_bar()
                    
                # Exit menu mode and return to calculator with the preserved input
                self.is_in_menu = False
                self.menu_type = None
                
                # Restore the input that was active before entering the menu
                if hasattr(self, 'pre_menu_input'):
                    self.display_input.setText(self.pre_menu_input)
                    self.current_input = self.pre_menu_input
                else:
                    self.display_input.setText("0")
                    self.current_input = "0"
                    
                self.cursor_position = len(self.current_input) - 1
                self.update_display_with_cursor()
                return
            elif self.menu_type == "sto" or self.menu_type == "rcl":
                # Get the selected memory variable
                positions = [5, 7, 9, 11, 13, 15]
                memory_vars = ['a', 'b', 'c', 'd', 'e', 'r']
                selected_var = memory_vars[positions.index(self.cursor_position)] if self.cursor_position in positions else 'a'
                
                # Store the current menu type before clearing it
                current_menu_type = self.menu_type
                
                # Exit menu mode
                self.is_in_menu = False
                self.menu_type = None
                
                # Handle STO vs RCL differently
                if current_menu_type == "sto":
                    # Check the saved pre-menu input
                    if self.pre_menu_input == "0":
                        # If nothing was entered, use Ans
                        result = f"Ans►{selected_var}"
                    else:
                        # Otherwise append to what was there
                        result = f"{self.pre_menu_input}►{selected_var}"
                    
                    # Update both current_input and display
                    self.current_input = result
                    self.display_input.setText(result)
                else:  # RCL mode
                    # Just insert the memory value
                    if selected_var == 'r':
                        value = self.rand_value
                    else:
                        value = self.memory_values[selected_var]
                        
                    if self.pop_menu_state():
                        # We popped back to another menu
                        if self.menu_type == "k":
                            # In K menu - append the value to K=
                            k_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
                            new_text = k_text + str(value)
                            
                            # Update both display and current_input to keep them in sync
                            self.display_input.setText(new_text)
                            self.current_input = new_text
                            self.cursor_position = len(new_text) - 1
                        else:
                            # In some other menu - keep its behavior
                            self.current_input = str(value)
                            self.display_input.setText(str(value))
                    else:
                        # Not returning to another menu - regular RCL behavior
                        self.current_input = str(value)
                        self.display_input.setText(str(value))
                        self.cursor_position = len(str(value)) - 1
                
                self.cursor_position = len(self.display_input.text()) - 1
                self.update_display_with_cursor()
                return
            elif self.menu_type == "stat":
                if self.cursor_position == 0:  # 1-var statistics
                    self.stat_manager.enter_stat_mode('1-var')
                    self.update_status_bar()
                elif self.cursor_position == 6:  # 2-var statistics
                    self.stat_manager.enter_stat_mode('2-var')
                    self.update_status_bar()
                elif self.cursor_position == 12:  # Clear data
                    # Clear data but stay in stat mode
                    if self.stat_manager.in_stat_mode:
                        was_cleared = self.stat_manager.clear_all_data()
                        if was_cleared:
                            self.display_result.setText("Data cleared")
                            # Set a timer to clear this message after 1.5 seconds
                            QTimer.singleShot(1500, lambda: self.display_result.setText(""))
                
                # Exit menu mode and return to calculator
                self.is_in_menu = False
                self.menu_type = None
                self.display_input.setText(self.pre_menu_input)
                self.current_input = self.pre_menu_input
                self.cursor_position = len(self.current_input) - 1
                self.update_display_with_cursor()
                return
            elif self.menu_type == "reset_confirm":
                # Check if user selected 'y' (yes)
                if self.cursor_position == 16:  # 'y' position
                    # Reset everything
                    self.key_buffer = ""
                    self.cursor_position = 0
                    self.insert_mode = False
                    self._toggling_secondary = False
                    self.is_in_menu = False
                    self.menu_type = None
                    self.angle_mode = "rad"
                    self.output_format = "flo"
                    self.decimal_places = None
                    self.ans = "0"
                    self.is_in_hyp = False
                    self.memory_values = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
                    self.rand_value = 0
                    self.current_input = "0"
                    self.k_mode_active = False
                    self.k_value = ""
                    self.mod_mode_active = False
                    self.mod_value = ""
                    
                    # Clear stat data
                    self.stat_manager.clear_all_data()
                    self.stat_manager.in_stat_mode = False
                    self.stat_manager.stat_mode = None
                    self.stat_manager.in_data_entry = False
                    self.stat_manager.data_1var = []
                    self.stat_manager.data_2var = []
                    self.stat_manager.current_x_index = 1
                    self.stat_manager.current_freq = 1
                    self.stat_manager.viewing_freq = False
                    self.stat_manager.viewing_y = False
                    
                    # Update display to confirm reset
                    self.display_result.setText("RESET COMPLETE")
                    self.display_input.setText("")
                    self.update_display_with_cursor()
                    self.update_status_bar()
                    QTimer.singleShot(1500, lambda: self.display_result.setText(""))
                else:
                    self.is_in_menu = False
                    self.menu_type = None
                    self.display_input.setText(self.pre_menu_input)
                    self.current_input = self.pre_menu_input
                
                self.cursor_position = 0
                self.update_display_with_cursor()
                return
            elif self.menu_type == "prb":
                # Get the selected function based on cursor position
                if self.cursor_position == 0:  # nPr
                    input_text = self.current_input if self.current_input != "0" else "ans"
                    function_text = f"{input_text} nPr "
                elif self.cursor_position == 4:  # nCr
                    input_text = self.current_input if self.current_input != "0" else "ans"
                    function_text = f"{input_text} nCr "
                elif self.cursor_position == 8:  # !
                    input_text = self.current_input if self.current_input != "0" else "ans"
                    function_text = f"{input_text}!"
                elif self.cursor_position == 10:  # rand
                    function_text = "rand"
                elif self.cursor_position == 15:  # randi
                    function_text = "randi("
                
                # Check if we need to return to a previous menu
                if self.pop_menu_state():
                    # We popped back to another menu
                    if self.menu_type == "k":
                        # In K menu - append the function to K=
                        k_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
                        new_text = k_text + function_text
                        
                        # Update both display and current_input to keep them in sync
                        self.display_input.setText(new_text)
                        self.current_input = new_text
                    else:
                        # In some other menu - handle appropriately
                        self.current_input = function_text
                        self.display_input.setText(function_text)
                else:
                    # Not returning to another menu - regular behavior
                    self.is_in_menu = False
                    self.menu_type = None
                    self.display_input.setText(function_text)
                    self.current_input = function_text
                
                self.cursor_position = len(self.display_input.text()) - 1
                self.update_display_with_cursor()
                return
            elif self.menu_type == "symbol":
                # Get the selected symbol based on cursor position
                if self.cursor_position == 0:  # °
                    symbol = "°"
                elif self.cursor_position == 2:  # '
                    symbol = "'"
                elif self.cursor_position == 4:  # "
                    symbol = "\""
                elif self.cursor_position == 6:  # r
                    symbol = "r"
                elif self.cursor_position == 8:  # g
                    symbol = "g"
                elif self.cursor_position == 10:  # ►DMS
                    symbol = "►DMS"
                
                # Check if current input is 0
                if self.current_input == "0":
                    new_text = f"Ans{symbol}"  # No space between Ans and symbol
                else:
                    new_text = f"{self.current_input}{symbol}"  # Append symbol to existing input
                
                if self.pop_menu_state():
                    # If returning to K menu, append the symbol
                    if self.menu_type == "k":
                        k_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
                        self.display_input.setText(k_text + symbol)
                        self.cursor_position = len(k_text + symbol) - 1
                else:
                    # No previous menu, exit to calculator and update display
                    self.display_input.setText(new_text)
                    self.current_input = new_text
                    self.cursor_position = len(new_text) - 1
                
                self.update_display_with_cursor()
                return
            elif self.menu_type == "r<>p":
                # Get selected operation based on cursor position
                if self.cursor_position == 0:  # R►Pr
                    func = "R►Pr("
                elif self.cursor_position == 5:  # R►Pθ
                    func = "R►Pθ("
                elif self.cursor_position == 10:  # P►Rx
                    func = "P►Rx("
                elif self.cursor_position == 15:  # P►Ry
                    func = "P►Ry("
                
                # Apply to current input or Ans
                if self.current_input == "0":
                    new_text = f"{func}"
                else:
                    new_text = f"{self.pre_menu_input}{func}"
                
                # Exit menu mode
                self.is_in_menu = False
                self.menu_type = None
                
                # Update display
                self.display_input.setText(new_text)
                self.current_input = new_text
                self.cursor_position = len(new_text) - 1
                self.update_display_with_cursor()
                return
            elif self.menu_type == "k":
                # Get user entered K value (strip the "K=" prefix)
                k_input = self.display_input.text().replace("<u>", "").replace("</u>", "")
                k_input = k_input[2:]  # Remove "K=" prefix
                
                # Store the K value
                self.k_value = k_input
                
                # Activate K mode
                self.k_mode_active = True
                
                # Exit menu mode
                self.is_in_menu = False
                self.menu_type = None
                
                # Show confirmation and update status bar
                self.display_input.setText(f"K MODE: {k_input}")
                QTimer.singleShot(1500, lambda: self.display_input.setText("0"))
                self.current_input = "0"
                self.update_status_bar()
                return
            elif self.menu_type == "mod":
                # Get user entered MOD value (strip the "MODULUS=" prefix)
                mod_input = self.display_input.text().replace("<u>", "").replace("</u>", "")
                mod_input = mod_input[8:]
                
                # Store the MOD value
                self.mod_value = mod_input
                
                # Activate MOD mode
                self.mod_mode_active = True
                
                # Exit menu mode
                self.is_in_menu = False
                self.menu_type = None
                
                # Show confirmation and update status bar
                self.display_input.setText(f"MOD MODE: {mod_input}")
                QTimer.singleShot(1500, lambda: self.display_input.setText("0"))
                self.current_input = "0"
                self.update_status_bar()
                return
            # Handle other menu types here
            
        if "x'(" in self.current_input or "y'(" in self.current_input:
            # Extract function name and value
            if "x'(" in self.current_input:
                function_name = "x'"
                value_str = self.current_input.split("x'(")[1].rstrip(")")
            else:
                function_name = "y'"
                value_str = self.current_input.split("y'(")[1].rstrip(")")
            
            result = self.process_stat_function(function_name, value_str)
            self.display_result.setText(str(result))
            return
            
        # Standard calculator evaluation  
        import sys
        import os
        
        # Add the project root to sys.path if needed
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.append(project_root)
        
        # Now we can import the evaluator
        from logic.evaluator import evaluate_expression
        
        # Get the current input without HTML tags
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        # Get the current input without HTML tags
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")

        # Append K value if K mode is active
        if self.k_mode_active and self.k_value:
            current_text = current_text + self.k_value

        # Now evaluate with the modified input
        result_obj = evaluate_expression(current_text, 
                            angle_mode=self.angle_mode, 
                            output_format=self.output_format,
                            decimal_places=self.decimal_places,
                            ans=self.ans,
                            hyp=self.is_in_hyp,
                            rand_seed=self.rand_value,
                            modulus=self.mod_value)

        # Check if we need to store the result in memory
        if result_obj['store_to'] is not None:
            memory_location = result_obj['store_to']
            if memory_location == 'r':
                self.rand_value = result_obj['raw_value']
            else:
                self.memory_values[memory_location] = result_obj['raw_value']

        # Display the result value
        self.display_result.setText(str(result_obj['value']))

        # Update ans with the new result
        self.ans = result_obj['value']

        if current_text != "0" and not self.is_in_menu:
            # Don't add duplicate entries in a row
            if not self.session_memory or self.session_memory[-1] != current_text:
                self.session_memory.append(current_text)
            
            # Reset history navigation
            self.history_index = -1

        # Set cursor position to the end of the input field
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def update_status_bar(self):
        status_text = f"Mode: {self.angle_mode.upper()} | Format: {self.output_format.upper()}"
        
        # Add decimal places if set
        if self.decimal_places is not None:
            status_text += f" | FIX {self.decimal_places}"
        
        # Add insert mode indicator if active
        if self.insert_mode:
            status_text += " | INS"
        
        # Add STAT indicator if in stat mode
        if self.stat_manager.in_stat_mode:
            status_text += f" | STAT {self.stat_manager.stat_mode}"
        
        # Add hyp indicator if active
        if self.is_in_hyp:
            status_text += " | HYP"
            
        # Add K mode indicator if active
        if self.k_mode_active:
            status_text += f" | K={self.k_value}"
            
        # Add MOD mode indicator if active
        if self.mod_mode_active:
            status_text += f" | MOD={self.mod_value}"
        
        self.status_bar.setText(status_text)
        
    def update_input_state(self, new_text, replace_zero=True):
        if self.display_result.text() != "":
            self.clear_input()
        
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if current_text == "0" and replace_zero:
            result = new_text
        else:
            if self.insert_mode:
                # Insert at cursor position
                result = current_text[:self.cursor_position + 1] + new_text + current_text[self.cursor_position + 1:]
                # Move cursor after the inserted text
                self.cursor_position += len(new_text)
            else:
                # Replace mode: If cursor is not at the end, replace the character
                if self.cursor_position < len(current_text) - 1:
                    result = current_text[:self.cursor_position] + new_text + current_text[self.cursor_position + 1:]
                    # Move cursor after the replaced character
                    self.cursor_position += 1
                else:
                    # At the end, append
                    result = current_text + new_text
                    # Move cursor to the end
                    self.cursor_position = len(result) - 1
        
        # Update both states
        self.current_input = result
        self.display_input.setText(result)
        
        self.update_display_with_cursor()
                
    def update_stat_field(self, text_value):
        current_text = self.display_input.text()
        if "=" in current_text:
            prefix = current_text.split("=")[0] + "="
            
            # Update the display
            self.display_input.setText(prefix + text_value)
            self.current_input = prefix + text_value
            
            # Strip HTML tags from the value
            clean_value = text_value.replace("<u>", "").replace("</u>", "")
            self.stat_manager.current_value = clean_value
            success = self.stat_manager.update_current_value(clean_value)
            
            self.cursor_position = len(self.current_input) - 1
            self.update_display_with_cursor()
            
    def process_stat_function(self, function_name, value):
        if not value:
            return "Error: No input"
        
        try:
            value = float(value)
            
            if function_name == "x'":
                result = self.stat_manager.calculate_x_prime(value)
                return result
            elif function_name == "y'":
                result = self.stat_manager.calculate_y_prime(value)
                return result
        except:
            return "Error"
        
        return "Error: Unknown function"
    
    def is_protected_prefix_position(self, current_text, cursor_pos):
        # Check for MODULUS= prefix protection
        if self.is_in_menu and self.menu_type == "mod":
            # Protect the entire "MODULUS=" prefix (8 characters long)
            if cursor_pos < 8:
                return True
                
            # Protect the = sign
            if cursor_pos < len(current_text) and current_text[cursor_pos] == '=':
                return True
                
            # For backspace, check if previous character is part of the MODULUS= prefix
            if '=' in current_text:
                prefix = "MODULUS="
                if cursor_pos <= len(prefix):
                    return True
                    
        # Check for K= prefix protection
        if self.is_in_menu and self.menu_type == "k":
            # Protect the entire "K=" prefix
            if cursor_pos < 2:  # K= is 2 characters long
                return True
                
            # Protect the = sign
            if cursor_pos < len(current_text) and current_text[cursor_pos] == '=':
                return True
                
            # For backspace, check if previous character is part of K= prefix
            if '=' in current_text:
                prefix = "K="
                if cursor_pos <= len(prefix):
                    return True
        
        # Statistics prefix protection code
        if self.stat_manager.in_data_entry:
            # First check: cursor in range affecting prefix
            if cursor_pos <= 2:
                return True
                
            # Second check: protect the = sign
            if cursor_pos < len(current_text) and current_text[cursor_pos] == '=':
                return True
                
            # Third check: protect any letters in the prefix (for 'freq=' case)
            if cursor_pos < len(current_text) and current_text[cursor_pos].isalpha():
                return True
                
            # Fourth check: for backspace, check if the previous character is part of prefix
            if '=' in current_text:
                prefix = current_text.split('=')[0] + '='
                if cursor_pos <= len(prefix):
                    return True
                    
        return False
    
    def update_k_field(self, text_value):
        # Update the display
        self.display_input.setText("K=" + text_value)
        self.current_input = "K=" + text_value
        self.cursor_position = len(self.current_input) - 1
        self.update_display_with_cursor()
        
    def update_mod_field(self, text_value):
        # Update the display
        self.display_input.setText("MODULUS=" + text_value)
        self.current_input = "MODULUS=" + text_value
        self.cursor_position = len(self.current_input) - 1
        self.update_display_with_cursor()
        
    def ensure_cursor_visible(self):
        # Get the cursor's pixel position using font metrics
        metrics = self.display_input.fontMetrics()
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        # Calculate text width up to cursor position
        if self.cursor_position < len(current_text):
            cursor_text = current_text[:self.cursor_position]
            cursor_pixel_pos = metrics.horizontalAdvance(cursor_text)
        else:
            cursor_pixel_pos = metrics.horizontalAdvance(current_text)
        
        # Get scroll area properties
        scrollbar = self.input_scroll_area.horizontalScrollBar()
        viewport_width = self.input_scroll_area.viewport().width()
        current_scroll_pos = scrollbar.value()
        
        # Ensure cursor is visible - calculate required scroll position
        margin = 20  # Pixel margin from edge
        
        # If cursor is to the right of visible area
        if cursor_pixel_pos > current_scroll_pos + viewport_width - margin:
            scrollbar.setValue(cursor_pixel_pos - viewport_width + margin)
        
        # If cursor is to the left of visible area
        elif cursor_pixel_pos < current_scroll_pos + margin:
            scrollbar.setValue(max(0, cursor_pixel_pos - margin))
            
    def save_state(self):
        from logic.state_manager import save_calculator_state
        
        try:
            # Log state saving
            print("Saving calculator state...")
            
            # Call the state manager's save function, passing this instance
            success = save_calculator_state(self)
            
            if success:
                print("Calculator state saved successfully")
            else:
                print("Failed to save calculator state")
                
        except Exception as e:
            print(f"Error saving calculator state: {str(e)}")
            
    def load_state(self):
        from logic.state_manager import load_calculator_state
        
        try:
            # Log state loading
            print("Loading calculator state...")
            
            # Call the state manager's load function, passing this instance
            success = load_calculator_state(self)
            
            if success:
                print("Calculator state loaded successfully")
            else:
                print("No saved state found or failed to load")
                
        except Exception as e:
            print(f"Error loading calculator state: {str(e)}")
            
    def push_menu_state(self, new_menu_type):
        if self.is_in_menu:
            # Save current menu context
            context = {
                'menu_type': self.menu_type,
                'cursor_position': self.cursor_position,
                'display_text': self.display_input.text()
            }
            self.menu_stack.append(context)
        
        # Enter new menu
        self.is_in_menu = True
        self.menu_type = new_menu_type
        
    def pop_menu_state(self):
        if not self.menu_stack:
            # No previous menu, exit to calculator
            self.is_in_menu = False
            self.menu_type = None
            return False
        
        # Pop previous menu from stack
        prev_menu = self.menu_stack.pop()
        self.is_in_menu = True
        self.menu_type = prev_menu['menu_type']
        self.cursor_position = prev_menu['cursor_position']
        self.display_input.setText(prev_menu['display_text'])
        return True
    
    def is_in_function_token(self, text, position):
        function_tokens = ["nPr", "nCr", "Ans", "(-)", "sin(", "cos(", "tan(", 
                        "sin^(-1)(", "cos^(-1)(", "tan^(-1)(", "ln(", "log(", "e^(",
                        "►A B/C↔D/E", "►f↔d", "R►Pr(", "R►Pθ(", "P►Rx(", "P►Ry(", "►DMS"]
        
        # Special case for position at the end of the text
        if position >= len(text):
            return False, -1, -1
        
        # For each function, check if position falls within its range
        for i in range(len(text)):
            for func in function_tokens:
                if i + len(func) <= len(text) and text[i:i+len(func)] == func:
                    # If position is within this function token's range
                    if i <= position < i + len(func):
                        return func, i, i + len(func)
        
        return False, -1, -1