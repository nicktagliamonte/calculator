TI-30X IIS Calculator
=====================

Overview
--------

A feature-rich scientific calculator inspired by the TI-30X IIS, reimagined with a modern dark interface and enhanced functionality. This first release includes a pre-built binary for Linux users.  
![Alt text](https://github.com/nicktagliamonte/calculator/blob/main/calculator/images/demo.png))

Download
--------

-   **Linux Binary**: [Release](https://github.com/nicktagliamonte/calculator/releases)

Platform Support
----------------

-   **Linux**: Ready-to-use binary included
-   **Windows/macOS**: Currently requires building from source (see instructions below)

Key Features
------------

-   Full scientific calculator functionality
-   Modern dark theme with 3D tactile buttons
-   Memory storage and recall
-   Statistical functions
-   Modulus operations
-   Fraction-decimal conversions
-   Keyboard shortcuts for common operations
-   Comprehensive error handling with descriptive messages
-   Enhanced insert mode for editing expressions
-   Session state preservation

Installation Instructions
-------------------------

### Linux

1.  Just download and run the `Calculator` file [here](https://github.com/nicktagliamonte/calculator/releases)

### Windows/macOS (Building from Source)

1.  Clone the repository:

    `git clone https://github.com/yourusername/calculator.git`

    `cd calculator`

2.  Install dependencies:

    `pip install -r requirements.txt`

3.  Build with PyInstaller:

    `pip install pyinstaller`

    `pyinstaller calculator.spec`

4.  The executable will be in the [dist](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) directory

Improvements Over Original TI-30X IIS
-------------------------------------

-   Added absolute value function
-   Radians as default angle mode
-   Simplified K value and statistical data entry
-   More descriptive error messages
-   Enhanced insert mode
-   Higher precision calculations  
-   Modular Arithmetic Capability
