# calculator/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton # type: ignore
from PySide6.QtCore import Qt, QObject # type: ignore
from PySide6.QtGui import QKeyEvent # type: ignore

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.key_buffer = ""
        self.cursor_position = 0
        
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

        # Set up grid layout for buttons (substep 2)
        self.grid_layout = QGridLayout()

        # State to track if "2ND" button is active
        self.secondary_state = False

        # Add buttons
        self.add_buttons(self.grid_layout)

        # Add button layout to the main layout
        main_layout.addLayout(self.grid_layout)

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

            # row 7: memvar/clrvar, 4/NULL, 5/NULL, 6/NULL, +/NULL
            ("MEMVAR", "CLRVAR", 6, 0),
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
                
            # Connect the memvar button
            if primary == "MEMVAR":
                button.clicked.connect(self.add_memvar)
                
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

    def toggle_secondary_state(self):
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

    def invert_2nd_button_color(self):
        button_2nd, _ = self.button_widgets[(0, 1)]
        if self.secondary_state:
            button_2nd.setStyleSheet("background-color: black; color: white; font-size: 12px;")
        else:
            button_2nd.setStyleSheet("background-color: white; color: black; font-size: 12px;")
            
    def keyPressEvent(self, event: QKeyEvent):
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
            "sqrt": "√(", "xrt": "X√",    # Root functions
            "pi": "π", "ans": "Ans",       # Constants
            "clear": "CLEAR", "memclr": "MEMCLR"  # Clear functions
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
                    current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
                    if current_text == "0":
                        self.display_input.setText(function_sequences[func])
                    else:
                        self.display_input.setText(current_text + function_sequences[func])
                    self.cursor_position = len(self.display_input.text()) - 1
                    self.update_display_with_cursor()
                    self.key_buffer = ""  # Reset buffer after match
                    break

            # If buffer is too long or invalid, reset
            if not any(k.startswith(self.key_buffer) for k in function_sequences):
                self.key_buffer = ""
        
        if event.key() in key_to_text:
            current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
            if current_text == "0":
                self.display_input.setText(key_to_text[event.key()])
            else:
                self.display_input.setText(current_text + key_to_text[event.key()])
            self.cursor_position = len(self.display_input.text()) - 1
            self.update_display_with_cursor()
            
        if event.key() in straight_operators:
            dummy_sender = QObject()
            dummy_sender.text = lambda: straight_operators[event.key()]
            self.sender = lambda: dummy_sender
            self.add_operator()
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
        
        if event.key() == Qt.Key_Slash:
            dummy_sender = QObject()
            dummy_sender.text = lambda: "÷"
            self.sender = lambda: dummy_sender
            self.add_operator()
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
            
        if event.key() == Qt.Key_AsciiCircum:
            dummy_sender = QObject()
            dummy_sender.text = lambda: "^"
            self.sender = lambda: dummy_sender
            self.add_carrot()
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
            
        if event.key() == Qt.Key_K:
            self.display_input.setText("K=")
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()
            
        if event.key() == Qt.Key_Equal:
            self.add_equals()
            self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
            self.update_display_with_cursor()

    def update_input(self):
        sender = self.sender()
        button_text = sender.text()
        current_text = self.display_input.text()
        print(current_text)

        # Remove <u> tags from current_text
        current_text = current_text.replace("<u>", "").replace("</u>", "")

        if current_text == "0":
            self.display_input.setText(button_text)
        else:
            self.display_input.setText(current_text + button_text)

        self.cursor_position = len(self.display_input.text()) - 1  # Move cursor to the end
        self.update_display_with_cursor()
        
    def clear_input(self):
        self.display_input.setText("0")
        if self.secondary_state:
            self.display_input.setText("MEMCLR")
            
    def add_operator(self):
        sender = self.sender()
        button_text = sender.text()
        current_text = self.display_input.text()
        if current_text == "0":
            self.display_input.setText("Ans" + button_text)
        else:
            self.display_input.setText(current_text + button_text)
            
    def add_carrot(self):
        sender = self.sender()
        button_text = sender.text()
        current_text = self.display_input.text()
        if current_text == "0":
            self.display_input.setText("Ans" + button_text)
        else:
            self.display_input.setText(current_text + button_text)
            
    def insert_function(self, func_name: str):
        current_text = self.display_input.text()

        if current_text == "0":
            self.display_input.setText(func_name)  # Replace 0
        else:
            self.display_input.setText(current_text + func_name)  # Append to existing input
            
    def insert_xrt(self):
        current_text = self.display_input.text()

        if current_text == "0":
            self.display_input.setText("AnsX√(")  # Replace 0 with "AnsX√("
        else:
            self.display_input.setText(current_text + "X√(")  # Append "X√("

    def add_with_parenthetical(self):
        sender = self.sender()
        button_text = sender.text().lower() + "("
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if current_text == "0":
            self.display_input.setText(button_text)
        else:
            self.display_input.setText(current_text + button_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_log(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        
        if self.secondary_state:
            new_text = "10^("
        else:
            new_text = "log("
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_ln(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "e^("
        else:
            new_text = "ln("
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
    
    def add_zero(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "RESET"
        else:
            new_text = "0"
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_decimal(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "FIX"
        else:
            new_text = "."
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
                
    def add_inverse(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "E"
        else:
            new_text = "^(-1)"
        if current_text == "0" and new_text == "^(-1)":
            self.display_input.setText("Ans" + new_text)
        elif current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_square(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "√("
        else:
            new_text = "^2"
        if current_text == "0" and new_text == "^2":
            self.display_input.setText("Ans" + new_text)
        elif current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_divide(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "K="
        else:
            new_text = "÷"
        if new_text == "K=":
            self.display_input.setText(new_text)
        elif current_text == "0" and new_text == "÷":
            self.display_input.setText("Ans" + new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_negate(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "Ans"
        else:
            new_text = "(-)"
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_power(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "X√"
        else:
            new_text = "^"
        if current_text == "0" and new_text == "^":
            self.display_input.setText("Ans" + new_text)
        elif current_text == "0" and new_text == "X√":
            self.display_input.setText("Ans" + new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_open_parenthesis(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "%"
        else:
            new_text = "("
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_close_parenthesis(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = ","
        else:
            new_text = ")"
        if current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_prb(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "►f<>d"
        else:
            new_text = "PRB"
        if current_text == "0" and new_text == "►f<>d":
            self.display_input.setText("Ans" + new_text)
        elif new_text == "►f<>d":
            self.display_input.setText(current_text + new_text)
        else: 
            self.display_input.setText(new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_frac_conversion(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "►A B/C <> D/E"
        else:
            new_text = "┘"
        if current_text == "0" and new_text == "►A B/C <> D/E":
            self.display_input.setText("Ans" + new_text)
        elif new_text == "►A B/C <> D/E":
            self.display_input.setText(current_text + new_text)
        elif current_text == "0":
            self.display_input.setText(new_text)
        else:
            self.display_input.setText(current_text + new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_drg(self):
        if self.secondary_state:
            new_text = "SCI/ENG"
        else:
            new_text = "DRG"
        self.display_input.setText(new_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def add_symbol_menu(self):
        if self.secondary_state:
            new_text = "r<>p"
        else:
            new_text = "° ' \""
        self.display_input.setText(new_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def add_memvar(self):
        if self.secondary_state:
            new_text = "CLRVAR"
        else:
            new_text = "MEMVAR"
        self.display_input.setText(new_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def add_sto(self):
        if self.secondary_state:
            new_text = "RCL"
        else:
            new_text = "STO>"
        self.display_input.setText(new_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def add_data(self):
        if self.secondary_state:
            new_text = "STAT"
        else:
            new_text = "DATA"
        self.display_input.setText(new_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def add_statvar(self):
        if self.secondary_state:
            new_text = "EXIT STAT"
        else:
            new_text = "STATVAR"
        self.display_input.setText(new_text)
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
        
    def add_pi(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            new_text = "HYP"
        else:
            new_text = "π"
        if new_text == "π" and current_text == "0":
            self.display_input.setText(new_text)
        elif new_text == "π":
            self.display_input.setText(current_text + new_text)
        else:
            self.display_input.setText(new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_delete(self):
        current_text = self.display_input.text().replace("<u>", "").replace("</u>", "")
        if self.secondary_state:
            self.display_input.setText("INS")
        else:
            new_text = current_text[:-1] if current_text != "0" else "0"
            self.display_input.setText(new_text)
            
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()
            
    def add_equals(self):
        current_text = self.display_input.setText("who knows")
        
        self.cursor_position = len(self.display_input.text()) - 1
        self.update_display_with_cursor()