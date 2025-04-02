from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QScrollArea # type: ignore
from PySide6.QtCore import Qt # type: ignore

class ManualWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TI-30X IIS Calculator Manual")
        self.setMinimumSize(600, 500)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create text browser for displaying content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setReadOnly(True)
        
        # Add scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.text_browser)
        scroll_area.setWidgetResizable(True)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        # Add widgets to layout
        layout.addWidget(scroll_area)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
        # Load manual content
        self.load_manual()
        
    def load_manual(self):
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #303030;
                color: #e0e0e0;
                border: 1px solid #555;
            }
            QScrollBar {
                background-color: #404040;
            }
        """)
        
        manual_md = """
# TI-30X IIS Calculator Manual

## Basic Operations
- Below is a table of keyboard shortcuts and their calculator equivalents

| Keyboard Input | Calculator Function | Category |
| -------------- | ------------------ | -------- |
| sin            | sin(                          | Trigonometric |
| cos            | cos(                          | Trigonometric |
| tan            | tan(                          | Trigonometric |
| asin           | sin^(-1)(                     | Inverse Trig |
| acos           | cos^(-1)(                     | Inverse Trig |
| atan           | tan^(-1)(                     | Inverse Trig |
| hyp            | Toggles Hyperbolic Mode       | Hyperbolic |
| nPr            | nPr                           | Combinatorial |
| nCr            | nCr                           | Combinatorial |
| !              | !                             | Combinatorial |
| log            | log(                          | Logarithmic |
| ln             | ln(                           | Logarithmic |
| sqrt           | √(                            | Root Functions |
| xrt            | X√(                           | Root Functions |
| pi             | π                             | Constants |
| ans            | Most Recent Answer            | Constants |
| clear          | Clear the Screen              | System |
| memclr         | Clear the Screen and Memory   | System |
| ctrl + c       | Copy                          | System |
| menu           | Display this menu             | System |
| fix            | FIX                           | Display Format |
| abs            | ABS(                          | Functions |
| '              | Seconds symbol                | Angle Notation |
| "              | Minutes symbol                | Angle Notation |
| deg            | set degree mode               | Angle Mode |
| rad            | set radian mode               | Angle Mode |
| grd            | set gradian                   | Angle Mode |
| ins            | set ins mode                  | Edit Mode |
| mod            | Enter the modulus menu        | Modulus Mode |

### Numbers and Arithmetic
- Enter numbers using the number keys (0-9)
- Use arithmetic operators (+, -, *, ÷) for calculations  
- note that '/' stands in for ÷ when inputting from keyboard
- Press = to compute the result
- The (-) button is used to denote negative values. (-) can also be entered via keyboard. Excluding the parentheses will result in an improperly parsed expression, as the '-' character will be read as strict subtraction

### Memory Functions
- STO> stores a value in memory (a, b, c, d, e, r)
- r is used as a seed for the random functions and is not accessed by RCL
- RCL recalls a stored value

### Special Functions
- 2ND activates the secondary function of buttons
- CLEAR erases the current entry
- DEL deletes the character at the cursor
- INS toggles insert mode
- ANS recalls the previous answer
- ABS calculates the absolute value

## Modes and Settings

### Number Theoretic Functions
- MOD access the modulus menu  
- With the modulus set to some integer, all calculations will be done modulo that integer
- The result is always a member of the least positive residue class
- The current modulus is shown in the status bar

### Angle Modes
- DRG cycles between Degree, Radian, and Gradian modes
- Hyp converts all trigonometric functions to hyperbolic functions
- Current mode is shown in the status bar

### Number Format
- FIX sets fixed decimal places (0-9)
- SCI/ENG toggles between scientific and engineering notation

## Statistical Functions

### Data Entry
- DATA enters the statistical data entry mode
- Only numeric values are accepted, non-numeric input will cause an error
- Expressions must be evaluated before entering. You cannot add "2*2" to the data set, you must first evaluate it to "4"
- STAT selects between 1-var and 2-var statistical modes
- STATVAR accesses statistical variables and calculations
- EXIT STAT exits stat mode
- Note that you must be in stat mode to access DATA or STATVAR menus

### Variables
- x̄: Mean of x values
- Sx: Sample standard deviation of x values
- σx: Population standard deviation of x values
- n: Number of data points
- Σx: Sum of x values
- Σx²: Sum of squares of x values
- ȳ: Mean of y values
- Sy: Sample standard deviation of y values
- σy: Population standard deviation of y values
- Σy: Sum of y values
- Σy²: Sum of squares of y values
- Σxy: Sum of product of x and y values
- a: Linear Regression Slope
- b: Linear Regression y-intercept
- r: Correlation coefficient
- x': mean centered value 
- y': mean centered value

## Advanced Features

### Fractions
- A B/C enters a character which allows the calculator to parse user-entered fractions
- i.e. 3 > A B/C > 1 > / > 2 is parsed as 3.5
- MIX<>IMP converts between different fraction formats (improper, mixed, and float)

### Trigonometry
- SIN, COS, TAN calculate trigonometric functions
- SIN⁻¹, COS⁻¹, TAN⁻¹ calculate inverse trigonometric functions
- HYP enables hyperbolic functions
- Use HYP to set hyperbolic mode, then the calculator will parse sin( as sinh(, etc.

### Logarithms and Powers
- LOG calculates base-10 logarithm
- LN calculates natural logarithm
- 10^x calculates 10 raised to a power
- e^x calculates e raised to a power
- X² calculates square of a number
- X^-1 calculates reciprocal
- ^ raises a number to a power
- √ calculates square root
- X√ calculates nth root

### Probability
- PRB accesses probability functions
- nPr: Permutations
- nCr: Combinations
- !: Factorial
- Rand: Returns a random number. If there is seed value in 'r', this random function will use that seed value
- Randi: Enter an ordered pair with the comma button (secondary to close parenthesis) to get a random number between the ordered pair, inclusive

### Constants
- π: Pi constant (3.14159...)
- Ans: The most recently obtained answer/return value

### K (2nd > divide)
- Press K to get to a screen to enter a K value
- Type some input and press enter/= to save it
- That value will be appended to the end of every expression you submit
- Press K again to exit K mode and stop adding this value to your expressions.

## Tips and Shortcuts
- Use the arrow keys to navigate input
- Press Up/Down arrows to navigate calculation history
- Use parentheses for complex expressions
- Use Ctrl + C to copy text from the display
- Replace individual characters on the input line by setting the cursor to the desired location and entering the new character
"""
        
        # Convert Markdown to HTML (simple conversion for basic formatting)
        html_content = self.markdown_to_html(manual_md)
        self.text_browser.setHtml(html_content)
    
    def markdown_to_html(self, markdown):
        # Change the body style to have light text on dark background
        html = "<html><body style='font-family: Arial, sans-serif; color: #e0e0e0; background-color: #303030;'>"
        
        # Process line by line
        lines = markdown.split('\n')
        in_list = False
        in_table = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for table start
            if line.strip().startswith('|') and not in_table:
                in_table = True
                html += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; border-color: #555;'>"
                
                # Process header row
                header_cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
                html += "<tr style='background-color: #444;'>"
                for cell in header_cells:
                    html += f"<th>{cell}</th>"
                html += "</tr>"
                
                # Skip the separator row (next line)
                i += 2  # Skip to the first data row
                
                # Process data rows with alternating colors
                row_number = 0
                while i < len(lines) and lines[i].strip().startswith('|'):
                    row_number += 1
                    data_cells = [cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                    
                    # Apply alternating row colors - darker shades for dark theme
                    if row_number % 2 == 0:  # Even rows
                        html += "<tr style='background-color: #3a3a3a;'>"
                    else:  # Odd rows
                        html += "<tr style='background-color: #333;'>"
                        
                    for cell in data_cells:
                        html += f"<td>{cell}</td>"
                    html += "</tr>"
                    i += 1
                
                html += "</table>"
                continue
            
            # Headers
            if line.startswith('# '):
                html += f"<h1>{line[2:]}</h1>"
            elif line.startswith('## '):
                html += f"<h2>{line[3:]}</h2>"
            elif line.startswith('### '):
                html += f"<h3>{line[4:]}</h3>"
            # List items
            elif line.startswith('- '):
                if not in_list:
                    html += "<ul>"
                    in_list = True
                html += f"<li>{line[2:]}</li>"
            # Regular text
            elif line.strip() == '':
                if in_list:
                    html += "</ul>"
                    in_list = False
                html += "<p></p>"
            else:
                if in_list:
                    html += "</ul>"
                    in_list = False
                html += f"<p>{line}</p>"
            
            i += 1
        
        if in_list:
            html += "</ul>"
        if in_table:
            html += "</table>"
        
        html += "</body></html>"
        return html