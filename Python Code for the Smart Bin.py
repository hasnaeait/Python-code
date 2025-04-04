import cv2  # Import the OpenCV library for video processing
from ultralytics import YOLO  # Import the YOLO model class from the ultralytics package
import serial  # Import the serial library for communication with Arduino
import smtplib  # Import the SMTP library for sending emails
from email.mime.text import MIMEText  # Import MIMEText to create email content
from email.mime.multipart import MIMEMultipart  # Import MIMEMultipart to handle multiple parts in the email

# Load the pre-trained YOLO model from a file
model = YOLO(r'Link to the pre-trained YOLO model')

# Initialize serial communication with Arduino on COM4 with a baud rate of 500000
ser = serial.Serial('COM4', 500000, timeout=0.01)

def read_serial():
    """Read data from the serial port connected to Arduino."""
    global ser
    # Read the data line from the serial port
    Information = ser.readline().decode().strip()
    # If the information is not empty, return it
    if Information:
        return Information
    # If no information is received, return a default value
    return '0.0'

def send_email(bin_status):
    """Send an email alert when the bin is full."""
    sender_email = "your_email@example.com"  # Replace with your email address
    receiver_email = "person_in_charge@example.com"  # Replace with the recipient's email address
    password = "your_password"  # Replace with your email password

    # Define the email subject and body content
    subject = "Smart Bin Alert: Bin is Full"
    body = f"The bin is currently {bin_status}. Please take the necessary action."

    # Create a multipart email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail server and send the email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()

        print("Email has been sent successfully.")
    except Exception as e:
        # Print any errors that occur during the email sending process
        print(f"Failed to send email: {e}")

# Load an image that will be displayed when plastic is detected
IMG = cv2.imread(r'Link to the image')

# Define the confidence threshold for object detection
threshold = 0.75

# Open the webcam for video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():  # Check if the webcam opened successfully
    print("Error: Could not open webcam.")
    exit()

# Main loop for processing video frames and communicating with Arduino
while True:
    # Read data from Arduino via serial communication
    Information_From_Arduino = int(read_serial())
    if Information_From_Arduino == 1:
        # If the bin is full, send an email alert
        send_email("full")

    # Capture a frame from the webcam
    ret, frame = cap.read()
    # Run object detection on the captured frame using the YOLO model
    results = model.predict(source=frame, conf=threshold, show=True)

    # Iterate through the detected results
    for result in results:
        for box in result.boxes:  # Iterate through each detected bounding box
            # Extract the coordinates of the bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # Get the confidence score of the detection
            conf = box.conf[0]
            # Get the class index of the detected object
            cls = int(box.cls[0])
            # Get the class label (name) from the model's class names
            label = model.names[cls]

            # Check if the detected object is plastic
            if label == "plastic":
                # Display an image indicating plastic detection
                cv2.imshow('Plastic Detected', IMG)
                # Send a command to Arduino to open the bin gate
                Command_From_Python = 1
                ser.write(f"{Command_From_Python}\n".encode())
                # Wait for acknowledgment from Arduino
                while True:
                    ack = read_serial()
                    if ack == "ACK":
                        print("Arduino confirmed the gate action.")
                        break

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
