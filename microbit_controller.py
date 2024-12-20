from microbit import *

while True:
    # Send "left" command when button A is pressed
    if button_a.is_pressed():
        uart.write("left\n")
    # Send "right" command when button B is pressed
    elif button_b.is_pressed():
        uart.write("right\n")
    else:
        uart.write("stop\n")

    sleep(100)  # Small delay to reduce communication frequency
