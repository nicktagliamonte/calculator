import os
import sys
import json
import logging
import platform
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Current state format version
STATE_VERSION = 1

def get_state_file_path():    
    # Detect operating system
    system = platform.system()
    
    if system == "Windows":
        # Windows: Use %APPDATA% (C:\Users\{username}\AppData\Roaming)
        app_dir = Path(os.environ.get('APPDATA', '')) / "Calculator"
    elif system == "Darwin":  # macOS
        # macOS: Use ~/Library/Application Support
        app_dir = Path.home() / "Library" / "Application Support" / "Calculator"
    else:  # Linux and other Unix-like systems
        # Linux: Follow XDG Base Directory Specification if possible
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            app_dir = Path(xdg_config_home) / "calculator"
        else:
            app_dir = Path.home() / ".config" / "calculator"
    
    # Create directory if it doesn't exist
    if not app_dir.exists():
        app_dir.mkdir(parents=True, exist_ok=True)
        
    return app_dir / "calculator_state.json"

def save_calculator_state(calculator):
    try:
        state_file = get_state_file_path()
        
        # Collect state from calculator
        state = {
            'version': STATE_VERSION,
            'memory': {
                'registers': calculator.memory_values,
                'rand_value': calculator.rand_value
            },
            'display': {
                'angle_mode': calculator.angle_mode,
                'output_format': calculator.output_format, 
                'decimal_places': calculator.decimal_places
            },
            'values': {
                'ans': calculator.ans,
                'k_value': calculator.k_value,
                'k_mode_active': calculator.k_mode_active
            },
            'modes': {
                'hyp': calculator.is_in_hyp
            },
            'history': {
                'session_memory': calculator.session_memory
            },
            'statistics': {
                'in_stat_mode': calculator.stat_manager.in_stat_mode,
                'stat_mode': calculator.stat_manager.stat_mode,
                'data_1': calculator.stat_manager.data_1 if hasattr(calculator.stat_manager, 'data_1') else None,
                'data_2': calculator.stat_manager.data_2 if hasattr(calculator.stat_manager, 'data_2') else None
            },
            'modulo': {
                'modulus': calculator.mod_value,
                'modulo_active': calculator.mod_mode_active
            },
            'number_theory': {
                'n_value': calculator.num_manager.n_value if hasattr(calculator, 'num_manager') else None,
                'm_value': calculator.num_manager.m_value if hasattr(calculator, 'num_manager') else None,
                'a_value': calculator.num_manager.a_value if hasattr(calculator, 'num_manager') else None
            }
        }
        
        # Write to file
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.info(f"Calculator state saved to {state_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving calculator state: {e}")
        return False

def load_calculator_state(calculator):
    try:
        state_file = get_state_file_path()
        
        # Check if file exists
        if not state_file.exists():
            logger.info("No saved state found")
            return False
            
        # Read from file
        with open(state_file, 'r') as f:
            state = json.load(f)
            
        # Check version
        if state.get('version', 0) != STATE_VERSION:
            logger.warning(f"State file version mismatch: {state.get('version')} (expected {STATE_VERSION})")
        
        # Apply memory values
        if 'memory' in state:
            calculator.memory_values = state['memory'].get('registers', calculator.memory_values)
            calculator.rand_value = state['memory'].get('rand_value', calculator.rand_value)
        
        # Apply display settings
        if 'display' in state:
            calculator.angle_mode = state['display'].get('angle_mode', calculator.angle_mode)
            calculator.output_format = state['display'].get('output_format', calculator.output_format)
            calculator.decimal_places = state['display'].get('decimal_places', calculator.decimal_places)
            
        # Apply values
        if 'values' in state:
            calculator.ans = state['values'].get('ans', calculator.ans)
            calculator.k_value = state['values'].get('k_value', calculator.k_value)
            calculator.k_mode_active = state['values'].get('k_mode_active', calculator.k_mode_active)
            
        # Apply modes
        if 'modes' in state:
            calculator.is_in_hyp = state['modes'].get('hyp', calculator.is_in_hyp)
            
        # Apply history
        if 'history' in state:
            calculator.session_memory = state['history'].get('session_memory', calculator.session_memory)
            
        # Apply statistics data
        if 'statistics' in state:
            calculator.stat_manager.in_stat_mode = state['statistics'].get('in_stat_mode', 
                                                        calculator.stat_manager.in_stat_mode)
            calculator.stat_manager.stat_mode = state['statistics'].get('stat_mode', 
                                                 calculator.stat_manager.stat_mode)
            if hasattr(calculator.stat_manager, 'data_1') and 'data_1' in state['statistics']:
                calculator.stat_manager.data_1 = state['statistics']['data_1']
            if hasattr(calculator.stat_manager, 'data_2') and 'data_2' in state['statistics']:
                calculator.stat_manager.data_2 = state['statistics']['data_2']
                
        # Apply modulo settings
        if 'modulo' in state:
            calculator.mod_value = state['modulo'].get('modulus', calculator.mod_value)
            calculator.mod_mode_active = state['modulo'].get('modulo_active', calculator.mod_mode_active)
            
        # Apply number theory settings
        if 'number_theory' in state:
            if hasattr(calculator, 'num_manager'):
                calculator.num_manager.n_value = state['number_theory'].get('n_value', None)
                calculator.num_manager.m_value = state['number_theory'].get('m_value', None)
                calculator.num_manager.a_value = state['number_theory'].get('a_value', None)
        
        # Update UI to reflect loaded state
        calculator.update_display_with_cursor()
        calculator.update_status_bar()
        
        logger.info(f"Calculator state loaded from {state_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading calculator state: {e}")
        return False

def delete_calculator_state():
    try:
        state_file = get_state_file_path()
        
        if state_file.exists():
            os.remove(state_file)
            logger.info(f"Calculator state deleted from {state_file}")
            return True
        else:
            logger.info("No state file to delete")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting calculator state: {e}")
        return False