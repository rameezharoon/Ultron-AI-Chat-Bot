Ultron AI Chatbot usage tutorial

need a working Gemini API key that API is replaced with genai.configure(api_key="YOUR_API_KEY") in the app.py and also main.py to make them workable

Python packages needed

for app.py

Flask, render_template, request, Response, jsonify
google.generativeai
gtts
playsound
threading 
queue 
json
os
re
uuid 
time

for main.py

google.generativeai
gtts
playsound
os
json
uuid
re

The Pyhton packages that need to manually download through PIP

for app.py

flask
google-generativeai
gTTS
playsound

for main.py

google-generativeai
gTTS
playsound

Code to downlaod all the Python packages that need to download manually through PIP

for main.py and app.py together

pip install flask google-generativeai gTTS playsound 

Paste this code in terminal like Command Prompt

To run the chat bot website on local host follow the given steps

1) in command prompt open the directory of the folder where the app.py is located with this command cd (YOUR_FOLDER_LOCATION)
2) then type python app.py to run the app.py file

To run the chat bot in terminal like Command Prompt do the same steps as same as to open the app.py just change the code that is python app.py as python main.py to run chat bot locally on terminal

also the independencies is need to install by

type pip install -r requirements.txt in command prompt to imstall independencies








