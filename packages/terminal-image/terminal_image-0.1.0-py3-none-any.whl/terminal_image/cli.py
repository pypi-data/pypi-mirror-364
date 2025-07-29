import cv2
import os
import sys
import time

def bgr_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def print_image(path, delay=0):
    img = cv2.imread(path)
    if img is None:
        print(f"Error: Cannot load image '{path}'")
        sys.exit(1)


    time.sleep(delay)
    
    term_width, term_height = os.get_terminal_size()
    term_height -= 1




    height, width, _ = img.shape
    max_width = min(width, term_width)
    max_height = min(height, term_height)


    



    os.system('cls' if os.name == 'nt' else 'clear')



    for y in range(max_height):
        for x in range(max_width):
            b, g, r = img[y, x]
            ansi = bgr_to_ansi(r, g, b)
            print(f"\033[{y+1};{x+1}H{ansi}█\033[0m", end='')







def main():
    if len(sys.argv) < 2:
        print("Usage: terminal-image <image_file> [delay]")
        sys.exit(1)

    image_path = sys.argv[1]
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print_image(image_path, delay)
