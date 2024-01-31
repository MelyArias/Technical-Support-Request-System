import keyboard
import time
import cv2
import sounddevice as sd
import os
from playsound import playsound  #recording imports
from scipy.io.wavfile import write  
import requests                  # Jira Imports
import json
from requests.auth import HTTPBasicAuth

#Function for taking image
def capture_image():
    cap = cv2.VideoCapture(0)   # Open the default camera (usually the built-in webcam)
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        return
    ret, frame = cap.read()  # Read a single frame from the camera
    
    if not ret:
        print("Error: Could not capture an image.")
        return
   
    cv2.imwrite("picture.jpg", frame)  # Save the captured image
    print("Image captured and saved as picture.jpg")

    cap.release()
    cv2.destroyAllWindows()
   
def on_space():
    capture_image()   #Take Picture
    os.system("./playintrovideo.sh" )   #Play  Video
    print('----Playing instructions----')
    time.sleep(15)
    
    fs = 44100 #Sample rate
    seconds = 18 #Duration of recording
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    print("---Recording---")
    sd.wait() #Wait until recording is finished
    write('output.wav', fs, myrecording) #Save as WAV file
    print('Done Recording')

    #Text-to-Speech AI
    os.system('whisper "output.wav" --model tiny.en')
    time.sleep(12)
    #Closes the terminal window
    os.system('osascript -e \'tell application "Terminal" to quit\'')
    
    #Send Request to Jira
    url = "https://peckschool.atlassian.net/rest/api/2/issue"  # Set your Jira Service Desk API URL

    #Jira Credentials
    username = "******@gmail.com"
    api_token = "APITOKEN"

    with open('output.txt', 'r') as file:  #Read the contents of the file 'output.txt'
        description_contents = file.read()

    data = {   #Create a dictionary with the data you want to send in the request body
        "fields" : {
            "project" : {
                "key": "TECH"
            },
            "summary": "HELPDESK REQUEST",
            "description": description_contents,
            "issuetype": {
                "id": "10003",
            }
        }
    }
    data_json = json.dumps(data)  #Convert the data to JSON format

    #Authorization
    BASIC_AUTH = HTTPBasicAuth(username,api_token)

    #Set the headers for the request
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json" 
    }
    
    #Make the POST request with basic authentication
    response = requests.post(url, data=data_json, headers=headers, auth=BASIC_AUTH)

    #Check the response status code
    if response.status_code ==201:
        print("Issue created successfully")
        response_json = response.json()
        issue_id = response_json["id"]
        print(issue_id)
        #Attach the image and and voice note
        #Attachment URL
        url2 = "https://peckschool.atlassian.net/rest/api/2/issue/"+issue_id+"/attachments"
        # JIRA required header (as per documentation)
        headers = { 'X-Atlassian-Token': 'no-check' }

        # (OPTIONAL) Multiple multipart-encoded files
        files = [
            ('file', ('output.txt', open('output.txt','rb'), 'text/plain')),
            ('file', ('picture.jpg', open('picture.jpg', 'rb'), 'image/jpeg')),
            {'file', ('output.wav', open('output.wav', 'rb'), 'audio/wav')}
        ] 
        r = requests.post(url2, auth=BASIC_AUTH, files=files, headers=headers)     # Run request
    
        #Check the response status code
        if r.status_code ==201:
            print("Issue created successfully")
            
    else:
        print(f"Failed to create issue. Status code: {response.status_code}")
        print(response.text)

keyboard.add_hotkey('space', on_space)  # Corresponds to the space pin on Makey Makey
keyboard.wait()