# calculator/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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

        # Add buttons (first row: including the "2nd" button)
        self.add_buttons(self.grid_layout)

        # Add button layout to the main layout
        main_layout.addLayout(self.grid_layout)

        # Set the central widget of the window
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # State to track if "2ND" button is active
        self.secondary_state = False

    def add_buttons(self, grid_layout):
        # Define your button layout with primary and secondary function
        self.buttons = [
            # row 1: 2nd/NULL, DRG/"SCI/ENG", DEL/INS
            ("2ND", "", 0, 1),
            ("DRG", "SCI/ENG", 0, 2),
            ("DEL", "INS", 0, 3),

            # row 2: log/10^x, prb/f<>d, ° ' \" /r<>p
            ("LOG", "10^x", 1, 1),
            ("PRB", "f<>d", 1, 2),
            ("° ' \"", "r<>p", 1, 3),

            # row 3: ln/e^x, "a b/c"/"a b/c <> d/e", data/stat, statvar/exit stat, clear/NULL
            ("LN", "e^x", 2, 0),
            ("A B/C", "A B/C <> D/E", 2, 1),
            ("DATA", "STAT", 2, 2),
            ("STATVAR", "EXIT STAT", 2, 3),
            ("CLEAR", "", 2, 4),

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

            # Set appropriate font size for buttons and labels
            button.setStyleSheet("font-size: 12px;")
            if label_secondary:
                label_secondary.setStyleSheet("font-size: 10px; color: gray;")

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

    def on_button_click(self):
        # Placeholder for button click functionality
        sender = self.sender()
        button_text = sender.text()

        # For now, this will print button text to show how it works
        print(button_text)

    def on_button_click(self):
        # Placeholder for button click functionality
        sender = self.sender()
        button_text = sender.text()

        # For now, this will print button text to show how it works
        print(button_text)
