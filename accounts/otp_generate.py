import math
import random

def generate_otp():
    # Declare a digits variable   
    # which stores all digits  
    digits = "0123456789"
    OTP = ""

    # length of password can be chaged
    # by changing value in range
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP
