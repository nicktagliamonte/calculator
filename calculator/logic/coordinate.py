import math

def rectangular_to_polar_r(x, y):
    return math.sqrt(x**2 + y**2)

def rectangular_to_polar_theta(x, y, angle_mode="rad"):
    # Get raw angle in radians
    theta = math.atan2(y, x)
    
    # Convert to specified angle mode
    if angle_mode == "deg":
        return theta * 180 / math.pi
    elif angle_mode == "grd":
        return theta * 200 / math.pi
    else:  # radians
        return theta

def polar_to_rectangular_x(r, theta, angle_mode="rad"):
    # Convert theta to radians if needed
    if angle_mode == "deg":
        theta_rad = theta * math.pi / 180
    elif angle_mode == "grd":
        theta_rad = theta * math.pi / 200
    else:  # already radians
        theta_rad = theta
        
    return r * math.cos(theta_rad)

def polar_to_rectangular_y(r, theta, angle_mode="rad"):
    # Convert theta to radians if needed
    if angle_mode == "deg":
        theta_rad = theta * math.pi / 180
    elif angle_mode == "grd":
        theta_rad = theta * math.pi / 200
    else:  # already radians
        theta_rad = theta
        
    return r * math.sin(theta_rad)