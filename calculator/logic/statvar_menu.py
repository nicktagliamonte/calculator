class StatVarMenuManager:
    def __init__(self):
        self.active = False
        self.mode = None  # '1-var' or '2-var'
        self.cursor_pos = 0
        
        # 1-var menu configuration
        self.menu_text_1var = "n x̄ Sx σx Σx Σx²"
        self.valid_positions_1var = [0, 2, 5, 8, 11, 14]  # Positions of n, x̄, etc.
        self.stats_1var = {}  # Cache for calculated values
        
        # 2-var menu configuration
        self.menu_text_2var = "n x̄ Sx σx ȳ Sy σy Σx Σx² Σy Σy² Σxy a b r x\' y\'"
        self.valid_positions_2var = [0, 2, 5, 8, 11, 14, 17, 20, 23, 27, 30, 34, 38, 40, 42, 44, 47]  # Positions of n, x̄, etc.
        self.stats_2var = {}  # Cache for calculated values
        
    def activate(self, mode, stat_manager):
        self.active = True
        self.mode = mode
        self.cursor_pos = 0
        
        if mode == '1-var':
            self.stats_1var = stat_manager.calculate_1var_statistics()
            return self.menu_text_1var, self.get_current_value()
        else:
            self.stats_2var = stat_manager.calculate_2var_statistics()
            return self.menu_text_2var, self.get_current_value()
    
    def navigate(self, direction):
        if not self.active:
            return None, None
        
        if self.mode == '1-var':
            positions = self.valid_positions_1var
            idx = positions.index(self.cursor_pos) if self.cursor_pos in positions else 0
            
            if direction == 'left':
                idx = (idx - 1) % len(positions)
            else:  # right
                idx = (idx + 1) % len(positions)
            
            self.cursor_pos = positions[idx]
            return self.menu_text_1var, self.get_current_value()
        
        if self.mode == '2-var':
            positions = self.valid_positions_2var
            idx = positions.index(self.cursor_pos) if self.cursor_pos in positions else 0
            
            if direction == 'left':
                idx = (idx - 1) % len(positions)
            else:
                idx = (idx + 1) % len(positions)
            
            self.cursor_pos = positions[idx]
            return self.menu_text_2var, self.get_current_value()
    
    def get_current_value(self):
        if not self.active:
            return None
        
        if self.mode == '1-var':
            if self.cursor_pos == 0:  # n
                return self.stats_1var['n']
            elif self.cursor_pos == 2:  # x̄
                return self.stats_1var['mean']
            elif self.cursor_pos == 5:  # Sx
                return self.stats_1var['sx']
            elif self.cursor_pos == 8:  # σx
                return self.stats_1var['sigmax']
            elif self.cursor_pos == 11:  # Σx
                return self.stats_1var['sum_x']
            elif self.cursor_pos == 14:  # Σx²
                return self.stats_1var['sum_x_squared']
        
        if self.mode == '2-var':
            if self.cursor_pos == 0:
                return self.stats_2var['n']
            elif self.cursor_pos == 2:
                return self.stats_2var['mean_x']
            elif self.cursor_pos == 5:
                return self.stats_2var['sx']
            elif self.cursor_pos == 8:
                return self.stats_2var['sigmax']
            elif self.cursor_pos == 11:
                return self.stats_2var['mean_y']
            elif self.cursor_pos == 14:
                return self.stats_2var['sy']
            elif self.cursor_pos == 17:
                return self.stats_2var['sigmay']
            elif self.cursor_pos == 20:
                return self.stats_2var['sum_x']
            elif self.cursor_pos == 23:
                return self.stats_2var['sum_x_squared']
            elif self.cursor_pos == 27:
                return self.stats_2var['sum_y']
            elif self.cursor_pos == 30:
                return self.stats_2var['sum_y_squared']
            elif self.cursor_pos == 34:
                return self.stats_2var['sum_xy']
            elif self.cursor_pos == 38:
                return self.stats_2var['a']
            elif self.cursor_pos == 40:
                return self.stats_2var['b']
            elif self.cursor_pos == 42:
                return self.stats_2var['r']
            elif self.cursor_pos == 44:
                return "x'("
            elif self.cursor_pos == 47:
                return "y'("
        return None
    
    def deactivate(self):
        current_value = self.get_current_value()
        self.active = False
        return current_value