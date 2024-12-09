import cv2
import numpy as np
from PIL import Image 
import serial
import time


def convert_to_black_and_white(image_path, bw_output_path):
    # Open an image file
    image_path = 'lineart.jpg'  
    image = Image.open(image_path)

    # Convert the image to black and white
    bw_image = image.convert('L')

    # Save or display the black and white image
    bw_image.save('black_and_white_image.jpg')
    print(f"Black-and-white imaged saved to {bw_output_path}")
    
    return bw_output_path


def process_image(image_path, binary_output_path="binary_output.txt", scale_factor=0.5):
    # Load the black and white image using OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Resize the image (optional to reduce resolution for easier drawing)
    if scale_factor != 1.0:
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    # Apply edge detection (Canny)
    edges = cv2.Canny(image, threshold1=50, threshold2=150)

    # Convert edges to binary (1 for edge, 0 for background)
    binary_matrix = (edges > 0).astype(int)

    # Save the binary matrix to a text file
    np.savetxt(binary_output_path, binary_matrix, fmt='%d', delimiter="")
    print(f"Binary matrix saved to {binary_output_path}")

    return binary_matrix


def convert_to_coordinates(binary_matrix, scale=1.0):
    coordinates = []
    for row_idx, row in enumerate(binary_matrix):
        for col_idx, value in enumerate(row):
            if value == 1:  # Edge detected
                x = col_idx * scale
                y = row_idx * scale
                coordinates.append((x, y))
    return coordinates

def send_to_robot_arm(serial_port, coordinates):
    try:
        with serial.Serial(serial_port, baudrate=115200, timeout=1) as ser:
            # Initialize the arm (optional, depending on your setup)
            ser.write(b"G28\n")  # Home the robot arm
            time.sleep(2)  # Wait for homing to complete

            for x, y in coordinates:
                # Create G-code command
                command = f"G01 X{x:.2f} Y{y:.2f} F1500\n"  # F1500 sets feed rate
                ser.write(command.encode())
                time.sleep(0.1)  # Delay to allow execution
                print(f"Sent G-code command: {command.strip()}")

            # Finalize the arm's movements (optional)
            ser.write(b"M84\n")  # Disable steppers
            print("Robot arm movements complete.")

    except Exception as e:
        print(f"Error communicating with robot arm: {e}")


# Main Function
if __name__ == "__main__":
    # Input and output paths
    image_path = 'lineart.jpg'  # Input image file
    bw_output_path = 'black_and_white_image.jpg'
    binary_output_path = 'binary_output.txt'
    serial_port = '/dev/ttyUSB0'  # UPDATE with your xArm's serial port

    # Step 1: Convert image to black-and-white
    bw_image_path = convert_to_black_and_white(image_path, bw_output_path)

    # Step 2: Process the black-and-white image to detect edges
    binary_matrix = process_image(bw_image_path, binary_output_path)

    # Step 3: Convert binary matrix to robot arm coordinates
    coordinates = convert_to_coordinates(binary_matrix, scale=0.1)  # Adjust scale as needed

    # Step 4: Send coordinates as G-code commands to the robot arm
    send_to_robot_arm(serial_port, coordinates)