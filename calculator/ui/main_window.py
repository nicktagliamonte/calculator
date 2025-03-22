# calculator/ui/main_window.py
from PySide6.QtCore import QTimer # type: ignore
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton # type: ignore
from PySide6.QtCore import Qt, QObject # type: ignore
from PySide6.QtGui import QKeyEvent # type: ignore
from logic.stat import StatisticsManager
from logic.statvar_menu import StatVarMenuManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stat_manager = StatisticsManager()
        self.statvar_menu = StatVarMenuManager()
        
        self.key_buffer = ""
        self.cursor_position = 0
        self.insert_mode = False
        self._toggling_secondary = False
        self.is_in_menu = False  # Track if we're in a menu
        self.menu_type = None    # Type of menu we're in
        self.angle_mode = "rad"
        self.output_format = "flo"
        self.decimal_places = None  # Default is None (F), meaning flexible decimal places
        self._original_sender = self.sender
        self.ans = "0"  # Initialize ans variable
        
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
        self.display_result = QLabel("0")  # Result display
        self.display_input.setAlignment(Qt.AlignRight)
        self.display_result.setAlignment(Qt.AlignRight)

        # Style the labels
        self.display_input.setStyleSheet("font-size: 24px;")
        self.display_result.setStyleSheet("font-size: 20px; color: grey;")

        # Add display labels to layout
        main_layout.addWidget(self.display_input)
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
        
        self.update_display_with_cursor()

    def add_buttons(self, grid_layout):
        self.buttons = [
            # row 1: 2nd/NULL, DRG/"SCI/ENG", DEL/INS
            ("2ND", "", 0, 1),
            ("DRG", "SCI/ENG", 0, 2),
            ("DEL", "INS", 0, 3),

            # row 2: log/10^x, prb/f<>d, ° ' \" /r<>p
            ("LOG", "10^x", 1, 1),
            ("PRB", "f<>d", 1, 2),
            ("° ' \"", "r<>p", 1, 3),

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
            
        # If we're in secondary state, turn it off AFTER the operation is complete
        # (except when we're toggling due to the 2ND button itself)
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
                    
                # Remove last character
                value_part = value_part[:-1] if value_part else ""
                
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
        # Handle menu-specific navigation first
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
        # OTHER MENUS TO BE ADDED HERE
        
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
        
        function_sequences = {
            "sin": "sin(", "cos": "cos(", "tan": "tan(",  # Trig functions
            "log": "log(", "ln": "ln(",     # Logarithmic functions
            "sqrt": "√(", "xrt": "X√(",    # Root functions
            "pi": "π", "ans": "Ans",       # Constants
            "clear": "CLEAR", "memclr": "MEMCLR",  # Clear functions
            "fix": "FIX" # Other functions
        }
        
        if event.key() == Qt.Key_Left:
            self.cursor_position = max(0, self.cursor_position - 1)
            self.update_display_with_cursor()
            return
            
        if event.key() == Qt.Key_Right:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            self.cursor_position = min(len(current_text) - 1, self.cursor_position + 1)
            self.update_display_with_cursor()
            return

        # Capture letters for function sequences
        if Qt.Key_A <= event.key() <= Qt.Key_Z:
            self.key_buffer += event.text().lower()  # Store lowercase letter

            # Check if buffer matches a valid function
            for func in function_sequences:
                if self.key_buffer == func:
                    # Use the existing insert_function method
                    self.insert_function(function_sequences[func])
                    self.key_buffer = ""  # Reset buffer after match
                    break

            # If buffer is too long or invalid, reset
            if not any(k.startswith(self.key_buffer) for k in function_sequences):
                self.key_buffer = ""
        
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
            
        if event.key() == Qt.Key_K:
            self.display_input.setText("K=")
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
            
        if event.key() == Qt.Key_Equal:
            self.add_equals()
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
            
        if event.key() == Qt.Key_Delete:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            
            # Special handling for stat data entry mode
            if self.stat_manager.in_data_entry:
                if self.is_protected_prefix_position(current_text, self.cursor_position):
                    # Don't allow deletion of the prefix
                    return
            
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
            if current_text != "0" and len(current_text) > 0 and self.cursor_position > 0:
                new_text = current_text[:self.cursor_position - 1] + current_text[self.cursor_position:]
                if new_text == "":
                    new_text = "0"
                self.display_input.setText(new_text)
                self.current_input = new_text
                
                self.cursor_position = max(0, self.cursor_position - 1)
                
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
        self.display_input.setText("0")
        self.display_result.setText("0")
        self.cursor_position = 0
        
        if self.secondary_state:
            self.display_input.setText("0")
            self.display_result.setText("0")
            self.cursor_position = 0
            self.ans = "0"
            self.memory_values = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
            self.rand_value = 0
        
        self.current_input = "0"
        self.update_display_with_cursor()
            
    def add_operator(self, custom_sender=None):
        if self.is_in_menu:
            return
            
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
        if func_name == "CLEAR":
            self.clear_input()
            return
        
        if func_name == "FIX":
            self.add_fix()
            return
        
        self.update_input_state(func_name, replace_zero=True)
            
    def insert_xrt(self):
        if self.is_in_menu:
            return
            
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
            
        sender = self.sender()
        button_text = sender.text().lower() + "("
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        self.update_input_state(button_text, replace_zero=True)
        
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_log(self):
        if self.is_in_menu:
            return
            
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
            
        if self.secondary_state:
            new_text = "RESET"
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
            
        if self.secondary_state:
            new_text = "K="
        else:
            new_text = "÷"
        
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if new_text == "K=":
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        elif current_text == "0" and new_text == "÷":
            new_text = "Ans÷"
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
        else:
            self.update_input_state(new_text)
            
        if self.secondary_state:
            self.toggle_secondary_state()
            
    def add_negate(self):
        if self.is_in_menu:
            return
            
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
            
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "►f↔d"  
        else:
            new_text = "PRB"
        
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
        if self.secondary_state:
            new_text = "r<>p"
        else:
            new_text = "° ' \""
        
        self.display_input.setText(new_text)
        self.cursor_position = len(new_text) - 1
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
        """Helper method to restore input after memory clear"""
        self.display_input.setText(saved_input)
        self.current_input = saved_input
        self.cursor_position = len(saved_input) - 1
        self.update_display_with_cursor()
        
    def add_sto(self):
        self.pre_menu_input = self.current_input
        
        if self.secondary_state:
            new_text = "RCL: a b c d e r"
            self.is_in_menu = True
            self.menu_type = "rcl"
        else:
            new_text = "STO: a b c d e r"
            self.is_in_menu = True
            self.menu_type = "sto"
        
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
            # Exit STAT mode (existing code)
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
            
        if self.secondary_state:
            new_text = "HYP"
            # HYP completely replaces the display
            self.display_input.setText(new_text)
            self.current_input = new_text
            self.cursor_position = len(new_text) - 1
            self.update_display_with_cursor()
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
            
            self.cursor_position = len(self.display_input.text()) - 1
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
                    
                    self.current_input = str(value)
                    self.display_input.setText(str(value))
                
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
                        # Maybe show a brief confirmation
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
        
        result_obj = evaluate_expression(current_text, 
                            angle_mode=self.angle_mode, 
                            output_format=self.output_format,
                            decimal_places=self.decimal_places,
                            ans=self.ans)  # Pass ans to evaluator

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
        
        self.status_bar.setText(status_text)
        
    def update_input_state(self, new_text, replace_zero=True):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if current_text == "0" and replace_zero:
            result = new_text
        else:
            if self.insert_mode:
                # Insert at cursor position
                result = current_text[:self.cursor_position + 1] + new_text + current_text[self.cursor_position + 1:]
            else:
                # Normal append mode
                result = current_text + new_text
        
        # Update both states
        self.current_input = result
        self.display_input.setText(result)
        
        # Update cursor position
        self.cursor_position = len(result) - 1 if not self.insert_mode else self.cursor_position + len(new_text)
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
    
    # Add this function to MainWindow class
    def is_protected_prefix_position(self, current_text, cursor_pos):
        if not self.stat_manager.in_data_entry:
            return False
            
        # First check: cursor in range [0,2] (would affect any prefix)
        if cursor_pos <= 2:
            return True
            
        # Second check: protect the = sign
        if cursor_pos < len(current_text) and current_text[cursor_pos] == '=':
            return True
            
        # Third check: protect any letters in the prefix (for 'freq=' case)
        if cursor_pos < len(current_text) and current_text[cursor_pos].isalpha():
            return True
            
        # Fourth check: for backspace, check if the previous character is part of prefix
        # For 'freq=', protect position right after 'q'
        if '=' in current_text:
            prefix = current_text.split('=')[0] + '='
            if cursor_pos <= len(prefix):
                return True
                
        return False