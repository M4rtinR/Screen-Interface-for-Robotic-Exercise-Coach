import time

import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import base64
import os
import paramiko

NON_EXERCISE = False
EXERCISE = True

# app = Flask('poliy_webview_api')
# api = Api(app)

'''class UpdateWebView(Resource):
    def post(self):
        output = ''
        output += '<html><body>'
        output += '<h1>Json Test</h1>'
        if request.is_json:
            output += '<p>request is json</p>'
            output += '</body></html>'
            self.wfile.write(output.encode())
            new_data = {
                'completed': '1'
            }

            return new_data, 200
        else:
            output += '<p>not json. Oh dear</p>'
            output += '</body></html>'
            self.wfile.write(output.encode())
            new_data = {
                'completed': '0'
            }

            return new_data, 200'''

# api.add_resource(UpdateWebView, '/speech')
displayStringSpaces = ''
picName = None
phase = EXERCISE
repCount = '0'
OVERRIDE_QUESTION = 0
OVERRIDE_PRE_INSTRUCTION = 1
overrideQuestionOrPre = OVERRIDE_QUESTION
OVERRIDE_SHOT = 0
OVERRIDE_STAT = 1
overrideShotOrStat = OVERRIDE_STAT
shot = None
end = False
previous_page = None
baselineSet = False

# ITT Pepper router:
post_address = "http://192.168.1.207:4999/output"
controller_post_address = "http://192.168.1.207:5000/cue"

# Dusty on HRI lab 5G:
# post_address = "http://192.168.1.207:4999/output"
# controller_post_address = "http://192.168.1.207:5000/cue"

# Home wifi:
# post_address = "http://192.168.1.174:4999/output"
# controller_post_address = "http://192.168.1.174:5000/cue"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
# 4G hotspot:
# ssh.connect("192.168.43.57", username="nao", password="nao")
# ITT_Pepper router:
ssh.connect("192.168.1.5", username="nao", password="nao")
# Dusty in HRI lab
# ssh.connect("192.168.1.105", username="nao", password="mummer")

class requestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("get")
        global displayStringSpaces
        global picName
        global phase
        global repCount
        global overrideQuestionOrPre
        global overrideShotOrStat
        global end
        global previous_page
        if self.path.endswith('/display'):
            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            #output = '<!DOCTYPE html><html><body><p>test</p></body></html>'

            output = '<!DOCTYPE html>'

            if phase == NON_EXERCISE:
                print("non-exercise")
                output += '<html><body>'
                output += '<div style="height:80%; width:100%; position:absolute; bottom:20%;">'
                if end:
                    output += '<form action="http://192.168.1.207:8000/ok" method="POST">'
                    output += '<input type="submit" name="ok" value="OK" style="position:absolute; top:0px; left:40%;, width:20%; height:20%; font-size:xx-large;" />'
                    output += '</form>'
                output += '<form action="http://192.168.1.207:8000/repeat" method="POST">'
                output += '<input type="submit" name="repeat" value="Repeat" style="position:absolute; bottom:0; right:0; width:20%; height:20%; font-size:xx-large;" />'
                output += '</form>'
                output += '<form action="http://192.168.1.207:8000/repeat" method="POST">'
                output += '<input type="submit" name="repeat" value="Repeat" style="position:absolute; bottom:0; right:0; width:20%; height:20%; font-size:xx-large;" />'
                output += '</form>'
                output += '</div>'
                output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
                output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
                output += '</div>'
                output += '</body></html>'

            elif phase == EXERCISE:
                print("exercise")
                # This will contain image of exercise and rep counter.
                output += '<html><body>'
                '''output += '<script>'
                output += 'const button = document.getElementById("stop-btn");\n'
                output += 'button.addEventListener("click", async _ => {\n'
                output += '  var xmlHttp = new XMLHttpRequest();\n'
                output += '  xmlHttp.onreadystatechange = function() {\n'
                output += '    if (xmlHttp.readyState == 4 & & xmlHttp.status == 200)\n'
                output += '      console.log(xmlHttp.responseText);\n'
                output += '  }\n'
                output += '  xmlHttp.open("POST", "http://192.168.1.207:8000/stop", true); // true for asynchronous\n'
                output += '  xmlHttp.send(null);\n'
                output += '  try {\n'
                output += '    const response = await fetch("http://192.168.1.207:8000/stop", {\n'
                output += '      method: "get",\n'
                output += '      body: {\n'
                output += '        // Your body\n'
                output += '      }\n'
                output += '    });\n'
                output += '    console.log("Completed!"", response);\n'
                output += '  } catch(err) {\n'
                output += '    console.error(`Error: ${err}`);\n'
                output += '  }\n'
                output += '});\n'
                output += '</script>'''
                output += '<div style="height:80%; position:absolute;">'  # Main div
                #output += '<button type="button" style="position:absolute; top:10px; left:40%;">Stop</button>'  # Stop button
                #output += '<form action="  http://192.168.1.207:8000/stop" method="POST"><button type="button" id="stop-btn" name="stop_button" value="stop" style="position:absolute; top:0px; left:40%;, width:20%; height:20%; font-size:xx-large;">Stop</button></form>'
                if int(repCount) > 0:
                    output += '<form action="http://192.168.1.207:8000/stop" method="POST">'
                    output += '<input type="submit" name="stop" value="Stop" style="position:absolute; top:0px; left:40%;, width:20%; height:20%; font-size:xx-large;" />'
                    output += '</form>'
                if picName is not None:
                    data_uri = base64.b64encode(open(picName, 'rb').read()).decode('utf-8')
                    output += '<img src="data:image/png;base64,{0}" alt="Current exercise" style="width:70%; height:100%; object-fit:scale-down;">'.format(data_uri)  # Exercise image
                output += '<div style="text-align:center;font-size:2000%;line-height:100%;width:30%;position:absolute;bottom:0;right:0;text-align:right;display:inline-block;padding:7.3%">' + repCount + '</div>'  # Rep counter
                output += '<form action="http://192.168.1.207:8000/repeat" method="POST">'
                output += '<input type="submit" name="repeat" value="Repeat" style="position:absolute; bottom:0; right:0; width:20%; height:20%; font-size:xx-large;" />'
                output += '</form>'
                output += '</div>'
                output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position: absolute; bottom:0;">'  # Subtitle div
                output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large">' + displayStringSpaces + '</div>'  # Subtitle text
                output += '</div>'
                output += '</body></html>'

            self.wfile.write(output.encode())
            f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
            f.writelines(output)
            f.close()

            sftp = ssh.open_sftp()
            sftp.put("/var/www/html/RehabInterface/webpages/index.html", ".local/share/PackageManager/apps/boot-config/html/index.html")
            sftp.close()
            end = False
        elif self.path.endswith("/video"):
            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            output = '<!DOCTYPE html>'

            output += '<html><body>'
            data_uri = base64.b64encode(open('/home/martin/TestVid.webm', 'rb').read()).decode('utf-8')
            #output += '<img src="data:image/png;base64,{0}" alt="Current exercise" style="width:70%; height:100%; object-fit:fill;">'.format(
                #data_uri)  # Exercise image
            #output += '<iframe src="/home/martin/TestVid.mp4" width="100%"></iframe>'
            output += '<video width="100%" controls>'
            output += '<source src="data:video/webm;base64,{0}" type="video/webm">'.format(data_uri)
            #output += '<source src="/home/martin/TestVid.webm" type = "video/webm">'
            #output += '<source src="/home/martin/TestVid.ogg" type = "video/ogg">'
            #output += 'Your browser does not support playing a video'
            output += '</video>'
            output += '</body></html>'

            self.wfile.write(output.encode())
            f = open("/var/www/html/RehabInterface/webpages/video.html", "w")
            f.writelines(output)
            f.close()

            sftp = ssh.open_sftp()
            sftp.put("/var/www/html/RehabInterface/webpages/video.html",
                     ".local/share/PackageManager/apps/boot-config/html/video.html")
            sftp.close()

        elif self.path.endswith("/stop"):
            previous_page = "/stop"

            output = '<!DOCTYPE html>'

            print("stop screen")
            output += '<html><body>'
            output += '<div style="height:40%; width:100%; display: flex; justify-content: center; align-items: center; position:absolute; top:0;">'  # Main div
            output += '<div style="flex: 0 0 90%; text-align: center; font-size: xx-large">Would you like to stop the whole session or just this exercise set?</div>'  # Repeat button
            output += '</div>'
            output += '<div style="height:60%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
            output += '<form action="http://192.168.1.207:8000/stopSession" method="POST">'
            output += '<input type="submit" name="stop_session" value="Stop Session" style="padding:30px; font-size:xx-large; margin-right:10%" />'
            output += '</form>'
            output += '<form action="http://192.168.1.207:8000/stopSet" method="POST">'
            output += '<input type="submit" name="stop_set" value="Stop Set" style="padding:30px; font-size:xx-large; margin-right:10%" />'
            output += '</form>'
            output += '<form action="http://192.168.1.207:8000/cancel" method="POST">'
            output += '<input type="submit" name="cancel" value="Cancel" style="padding:30px; font-size:xx-large;" />'
            output += '</form>'
            output += '</div>'
            output += '</body></html>'

            self.wfile.write(output.encode())
            f = open("/var/www/html/RehabInterface/webpages/stop.html", "w")
            f.writelines(output)
            f.close()

            sftp = ssh.open_sftp()
            sftp.put("/var/www/html/RehabInterface/webpages/stop.html",
                     ".local/share/PackageManager/apps/boot-config/html/index.html")
            sftp.close()

            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            # Send signal to robot to pause the session.
            output = {
                'pause': '1'
            }
            print("sending pause signal to robot")
            r = requests.post(post_address, json=output)

        elif self.path.endswith("/override"):
            previous_page = "/override"
            if overrideQuestionOrPre == OVERRIDE_PRE_INSTRUCTION:
                print("override pre instruction")

                self.send_response(200)
                self.send_header('content-type', 'text-html')
                self.end_headers()

                output = '<!DOCTYPE html>'

                output += '<html><head><style>\n'
                output += '.continueButton {grid-area: leftButton; }\n'
                output += '.chooseButton {grid-area: rightButton; }\n'
                output += '.repeatButton {grid-area: bottomButton; }\n'
                output += '.grid-container {display: grid; grid-template-areas: \'leftButton rightButton\' \'bottomButton bottomButton\'; gap: 10px; padding: 10px; }\n'
                output += '.grid-container > div {height: 150px; text-align: center; padding:10px 0; font-size: 50px; }\n'
                output += '.button {width: 95%; height: 40px; }\n'
                output += '</style></head><body>'
                output += '<div class="grid-container">'
                if overrideShotOrStat == OVERRIDE_SHOT:
                    output += '<div class="chooseButton"><form action="http://192.168.1.207:8000/shotChoice" method="POST">'
                    output += '<input type="submit" name="selectShot" value="Select Shot" class="button" />'
                    output += '</form></div>'
                    output += '<div class="continueButton"><form action="http://192.168.1.207:8000/continue" method="POST">'
                    output += '<input type="submit" name="continue" value="Continue with Chosen Shot" class="button"/>'
                    output += '</form></div>'
                else:
                    output += '<div class="chooseButton"><form action="http://192.168.1.207:8000/statChoice" method="POST">'
                    output += '<input type="submit" name="selectStat" value="Select Metric" class="button" />'
                    output += '</form></div>'
                    output += '<div class="continueButton"><form action="http://192.168.1.207:8000/continue" method="POST">'
                    output += '<input type="submit" name="continue" value="Continue with Chosen Metric" class="button"/>'
                    output += '</form></div>'
                output += '<div class="repeatButton"><form action="http://192.168.1.207:8000/repeat" method="POST">'
                output += '<input type="submit" name="repeat" value="Repeat" class="button"/>'
                output += '</form></div>'
                output += '</div>'
                output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
                output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
                output += '</div>'
                output += '</body></html>'

                self.wfile.write(output.encode())
                f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
                f.writelines(output)
                f.close()

                sftp = ssh.open_sftp()
                sftp.put("/var/www/html/RehabInterface/webpages/index.html",
                         ".local/share/PackageManager/apps/boot-config/html/index.html")
                sftp.close()
            else:
                print("override questioning")

                self.send_response(200)
                self.send_header('content-type', 'text-html')
                self.end_headers()

                if overrideShotOrStat == OVERRIDE_SHOT:

                    output = '<!DOCTYPE html>'
                    output += '<html><head><style>\n'
                    output += '.leftButton {grid-area: leftButton; }\n'
                    output += '.middleButton {grid-area: middleButton; }\n'
                    output += '.rightButton {grid-area: rightButton; }\n'
                    output += '.grid-container {display: grid; grid-template-areas: \'leftButton middleButton rightButton\'; gap: 5px; padding: 5px; }\n'
                    output += '.grid-container > div {height: 40px; text-align: center; padding: 5px; font-size: 30px; }\n'
                    output += '.button {width: 100%; height: 100%; }\n'
                    output += '</style></head><body>'

                    output += '<div class="grid-container">'
                    output += '<div class="leftButton"><form action="http://192.168.1.207:8000/drop/handChoice" method="POST">'
                    output += '<input name="drop" type="submit" value="Straight Drop" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="middleButton"><form action="http://192.168.1.207:8000/drive/handChoice" method="POST">'
                    output += '<input type="submit" name="drive" value="Straight Drive" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="rightButton"><form action="http://192.168.1.207:8000/cross%20court%20lob/handChoice" method="POST">'
                    output += '<input type="submit" name="lob" value="Cross Court Lob" class="button"/>'
                    output += '</form></div>'
                    output += '</div>'

                    output += '<div class="grid-container">'
                    output += '<div class="leftButton"><form action="http://192.168.1.207:8000/two%20wall%20boast/handChoice" method="POST">'
                    output += '<input type="submit" name="boast" value="Two Wall Boast" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="middleButton"><form action="http://192.168.1.207:8000/straight%20kill/handChoice" method="POST">'
                    output += '<input type="submit" name="kill" value="Straight Kill" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="rightButton"><form action="http://192.168.1.207:8000/volley%20kill/handChoice" method="POST">'
                    output += '<input type="submit" name="volleyKill" value="Volley Kill" class="button"/>'
                    output += '</form></div>'
                    output += '</div>'

                    output += '<div class="grid-container">'
                    output += '<div class="leftButton"><form action="http://192.168.1.207:8000/volley%20drop/handChoice" method="POST">'
                    output += '<input type="submit" name="volleyDrop" value="Volley Drop" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="middleButton"><form action="http://192.168.1.207:8000/chooseForMe" method="POST">'
                    output += '<input type="submit" name="chooseForMe" value="Choose For Me" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="rightButton"><form action="http://192.168.1.207:8000/repeat" method="POST">'
                    output += '<input type="submit" name="repeat" value="Repeat" class="button"/>'
                    output += '</form></div>'
                    output += '</div>'

                    output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
                    output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
                    output += '</div>'
                    output += '</body></html>'

                    self.wfile.write(output.encode())
                    f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
                    f.writelines(output)
                    f.close()

                    sftp = ssh.open_sftp()
                    sftp.put("/var/www/html/RehabInterface/webpages/index.html",
                             ".local/share/PackageManager/apps/boot-config/html/index.html")
                    sftp.close()
                else:

                    output = '<!DOCTYPE html>'
                    output += '<html><head><style>\n'
                    output += '.leftButton {grid-area: leftButton; }\n'
                    output += '.middleButton {grid-area: middleButton; }\n'
                    output += '.rightButton {grid-area: rightButton; }\n'
                    output += '.grid-container {display: grid; grid-template-areas: \'leftButton middleButton rightButton\'; gap: 5px; padding: 5px; }\n'
                    output += '.grid-container > div {height: 40px; text-align: center; padding: 5px; font-size: 30px; }\n'
                    output += '.button {width: 100%; height: 100%; }\n'
                    output += '</style></head><body>'

                    output += '<div class="grid-container">'
                    output += '<div class="leftButton"><form action="http://192.168.1.207:8000/racketPreparation/statSelection" method="POST">'
                    output += '<input type="submit" name="prep" value="Racket Preparation" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="middleButton"><form action="http://192.168.1.207:8000/approachTiming/statSelection" method="POST">'
                    output += '<input type="submit" name="downSwing" value="Approach Timing" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="rightButton"><form action="http://192.168.1.207:8000/impactCutAngle/statSelection" method="POST">'
                    output += '<input type="submit" name="cutAngle" value="Impact Cut Angle" class="button"/>'
                    output += '</form></div>'
                    output += '</div>'

                    output += '<div class="grid-container">'
                    output += '<div class="leftButton"><form action="http://192.168.1.207:8000/impactSpeed/statSelection" method="POST">'
                    output += '<input type="submit" name="speed" value="Impact Speed" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="middleButton"><form action="http://192.168.1.207:8000/followThroughRoll/statSelection" method="POST">'
                    output += '<input type="submit" name="followThroughSwing" value="Follow Through Roll" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="rightButton"><form action="http://192.168.1.207:8000/followThroughTime/statSelection" method="POST">'
                    output += '<input type="submit" name="followThroughTime" value="Follow Through Time" class="button"/>'
                    output += '</form></div>'
                    output += '</div>'

                    output += '<div class="grid-container">'
                    output += '<div class="leftButton"><form action="http://192.168.1.207:8000/chooseForMe" method="POST">'
                    output += '<input type="submit" name="chooseForMe" value="Choose For Me" class="button"/>'
                    output += '</form></div>'
                    output += '<div class="rightButton"><form action="http://192.168.1.207:8000/repeat" method="POST">'
                    output += '<input type="submit" name="repeat" value="Repeat" class="button"/>'
                    output += '</form></div>'
                    output += '</div>'

                    output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
                    output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
                    output += '</div>'
                    output += '</body></html>'

                    self.wfile.write(output.encode())
                    f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
                    f.writelines(output)
                    f.close()

                    sftp = ssh.open_sftp()
                    sftp.put("/var/www/html/RehabInterface/webpages/index.html",
                             ".local/share/PackageManager/apps/boot-config/html/index.html")
                    sftp.close()
        elif self.path.endswith("/shotChoice"):
            print("shotChoice")
            previous_page = "/shotChoice"

            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            output = '<!DOCTYPE html>'
            output += '<html><head><style>\n'
            output += '.leftButton {grid-area: leftButton; }\n'
            output += '.middleButton {grid-area: middleButton; }\n'
            output += '.rightButton {grid-area: rightButton; }\n'
            output += '.grid-container {display: grid; grid-template-areas: \'leftButton middleButton rightButton\'; gap: 5px; padding: 5px; }\n'
            output += '.grid-container > div {height: 40px; text-align: center; padding: 5px; font-size: 30px; }\n'
            output += '.button {width: 100%; height: 100%; }\n'
            output += '</style></head><body>'

            output += '<div class="grid-container">'
            output += '<div class="leftButton"><form action="http://192.168.1.207:8000/drop/handChoice" method="POST">'
            output += '<input type="submit" name="drop" value="Straight Drop" class="button"/>'
            output += '</form></div>'
            output += '<div class="middleButton"><form action="http://192.168.1.207:8000/drive/handChoice" method="POST">'
            output += '<input type="submit" name="drive" value="Straight Drive" class="button"/>'
            output += '</form></div>'
            output += '<div class="rightButton"><form action="http://192.168.1.207:8000/cross%20court%20lob/handChoice" method="POST">'
            output += '<input type="submit" name="lob" value="Cross Court Lob" class="button"/>'
            output += '</form></div>'
            output += '</div>'

            output += '<div class="grid-container">'
            output += '<div class="leftButton"><form action="http://192.168.1.207:8000/two%20wall%20boast/handChoice" method="POST">'
            output += '<input type="submit" name="boast" value="Two Wall Boast" class="button"/>'
            output += '</form></div>'
            output += '<div class="middleButton"><form action="http://192.168.1.207:8000/straight%20kill/handChoice" method="POST">'
            output += '<input type="submit" name="kill" value="Straight Kill" class="button"/>'
            output += '</form></div>'
            output += '<div class="rightButton"><form action="http://192.168.1.207:8000/volley%20kill/handChoice" method="POST">'
            output += '<input type="submit" name="volleyKill" value="Volley Kill" class="button"/>'
            output += '</form></div>'
            output += '</div>'

            output += '<div class="grid-container">'
            output += '<div class="leftButton"><form action="http://192.168.1.207:8000/volley%20drop/handChoice" method="POST">'
            output += '<input type="submit" name="volleyDrop" value="Volley Drop" class="button"/>'
            output += '</form></div>'
            output += '<div class="rightButton"><form action="http://192.168.1.207:8000/repeat" method="POST">'
            output += '<input type="submit" name="repeat" value="Repeat" class="button"/>'
            output += '</form></div>'
            output += '</div>'

            output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
            output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
            output += '</div>'
            output += '</body></html>'

            self.wfile.write(output.encode())
            f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
            f.writelines(output)
            f.close()

            sftp = ssh.open_sftp()
            sftp.put("/var/www/html/RehabInterface/webpages/index.html",
                     ".local/share/PackageManager/apps/boot-config/html/index.html")
            sftp.close()
        elif self.path.endswith("/statChoice"):
            print("statChoice")
            previous_page = "/statChoice"

            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            output = '<!DOCTYPE html>'
            output += '<html><head><style>\n'
            output += '.leftButton {grid-area: leftButton; }\n'
            output += '.middleButton {grid-area: middleButton; }\n'
            output += '.rightButton {grid-area: rightButton; }\n'
            output += '.grid-container {display: grid; grid-template-areas: \'leftButton middleButton rightButton\'; gap: 5px; padding: 5px; }\n'
            output += '.grid-container > div {height: 40px; text-align: center; padding: 5px; font-size: 30px; }\n'
            output += '.button {width: 100%; height: 100%; }\n'
            output += '</style></head><body>'

            output += '<div class="grid-container">'
            output += '<div class="leftButton"><form action="http://192.168.1.207:8000/racketPreparation/statSelection" method="POST">'
            output += '<input type="submit" name="prep" value="Racket Preparation" class="button"/>'
            output += '</form></div>'
            output += '<div class="middleButton"><form action="http://192.168.1.207:8000/approachTiming/statSelection" method="POST">'
            output += '<input type="submit" name="downSwing" value="Approach Timing" class="button"/>'
            output += '</form></div>'
            output += '<div class="rightButton"><form action="http://192.168.1.207:8000/impactCutAngle/statSelection" method="POST">'
            output += '<input type="submit" name="cutAngle" value="Impact Cut Angle" class="button"/>'
            output += '</form></div>'
            output += '</div>'

            output += '<div class="grid-container">'
            output += '<div class="leftButton"><form action="http://192.168.1.207:8000/impactSpeed/statSelection" method="POST">'
            output += '<input type="submit" name="speed" value="Impact Speed" class="button"/>'
            output += '</form></div>'
            output += '<div class="middleButton"><form action="http://192.168.1.207:8000/followThroughRoll/statSelection" method="POST">'
            output += '<input type="submit" name="followThroughSwing" value="Follow Through Roll" class="button"/>'
            output += '</form></div>'
            output += '<div class="rightButton"><form action="http://192.168.1.207:8000/followThroughTime/statSelection" method="POST">'
            output += '<input type="submit" name="followThroughTime" value="Follow Through Time" class="button"/>'
            output += '</form></div>'
            output += '</div>'

            output += '<div class="grid-container">'
            output += '<div class="rightButton"><form action="http://192.168.1.207:8000/repeat" method="POST">'
            output += '<input type="submit" name="repeat" value="Repeat" class="button"/>'
            output += '</form></div>'
            output += '</div>'

            output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
            output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
            output += '</div>'
            output += '</body></html>'

            self.wfile.write(output.encode())
            f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
            f.writelines(output)
            f.close()

            sftp = ssh.open_sftp()
            sftp.put("/var/www/html/RehabInterface/webpages/index.html",
                     ".local/share/PackageManager/apps/boot-config/html/index.html")
            sftp.close()
        elif self.path.endswith('/handChoice'):
            print("hand choice get")
            previous_page = "/handChoice"

            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            output = '<!DOCTYPE html>'

            output += '<html><head><style>\n'
            output += '.continueButton {grid-area: leftButton; }\n'
            output += '.chooseButton {grid-area: rightButton; }\n'
            output += '.repeatButton {grid-area: bottomButton; }\n'
            output += '.grid-container {display: grid; grid-template-areas: \'leftButton rightButton\' \'bottomButton bottomButton\'; gap: 10px; padding: 10px; }\n'
            output += '.grid-container > div {height: 150px; text-align: center; padding: 10px 0; font-size: 50px; }\n'
            output += '.button {width: 95%; height: 40px; }\n'
            output += '</style></head><body>'
            output += '<div class="grid-container">'
            output += '<div class="continueButton"><form action="http://192.168.1.207:8000/FH/' + self.path.split('/')[1] + '/shotSelection" method="POST">'
            output += '<input type="submit" name="forehand" value="Forehand" class="button"/>'
            output += '</form></div>'
            output += '<div class="chooseButton"><form action="http://192.168.1.207:8000/BH/' + self.path.split('/')[1] + '/shotSelection" method="POST">'
            output += '<input type="submit" name="backhand" value="Backhand" class="button" />'
            output += '</form></div>'
            output += '<div class="repeatButton"><form action="http://192.168.1.207:8000/repeat" method="POST">'
            output += '<input type="submit" name="repeat" value="Repeat" class="button"/>'
            output += '</form></div>'
            output += '</div>'
            output += '<div style="height:20%; width:100%; background:lightgray; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
            output += '<div style="flex: 0 0 90%; text-align: center; font-size: x-large;">' + displayStringSpaces + '</div>'
            output += '</div>'
            output += '</body></html>'

            self.wfile.write(output.encode())
            f = open("/var/www/html/RehabInterface/webpages/index.html", "w")
            f.writelines(output)
            f.close()

            sftp = ssh.open_sftp()
            sftp.put("/var/www/html/RehabInterface/webpages/index.html",
                     ".local/share/PackageManager/apps/boot-config/html/index.html")
            sftp.close()

    def do_POST(self):
        global displayStringSpaces
        global picName
        global phase
        global repCount
        global overrideQuestionOrPre
        global overrideShotOrStat
        global shot
        global end
        global previous_page
        global baselineSet

        print("Post")
        if self.path.endswith('/newUtterance'):
            print(self.path)
            displayString = self.path.split('/')[1]
            phaseString = self.path.split('/')[2]
            # ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            # if ctype == 'application/json':
            displayStringSpaces = displayString.replace('%20', ' ')
            displayStringSpaces = displayStringSpaces.replace('%2520', ' ')
            displayStringSpaces = displayStringSpaces.replace('%25', '%')
            phase = phaseString == "exercise"
            if self.path.split('/')[3] == "end":
                end = True
            # else:
            #     print("Didn't work")

        elif self.path.endswith('/newPicture'):
            # ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            # if ctype == 'application/json':
            picNameUnformatted = "ShotPhotos/" + self.path.split('/')[1] + ".jpg"
            picName = picNameUnformatted.replace('%20', ' ')
            print("new picture: " + picName)
                #picName = picName + ".png"
            # else:
            #     print("Didn't work")

        elif self.path.endswith("/newRep"):
            repCount = self.path.split('/')[1]
            print("new rep: " + repCount)

        elif self.path.endswith("/stop"):
            print("POST stop")

        elif self.path.endswith("/stopSession"):
            print("POST stopSession")
            pepper_output = {
                "pause": "0",
                "stop": "1"
            }
            r = requests.post(post_address, json=pepper_output)

            controller_output = {
                "goal_level": 1,
                "stop": 1
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/stopSet"):
            print("POST stopSet")
            pepper_output = {
                "pause": "0",
                "stop": "1"
            }
            r = requests.post(post_address, json=pepper_output)

            controller_output = {
                "goal_level": 2,
                "stop": 1
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/cancel"):
            print("POST cancel")
            output = {
                "pause": "0"
            }
            r = requests.post(post_address, json=output)

        elif self.path.endswith("/repeat"):
            print("POST repeat")
            output = {
                "repeat": "1"
            }
            r = requests.post(post_address, json=output)

        elif self.path.endswith("/overrideOption"):
            print("Override option")
            displayString = self.path.split('/')[1]
            displayStringSpaces = displayString.replace('%20', ' ')

            questionOrPre = self.path.split('/')[2]
            if questionOrPre == "question":
                overrideQuestionOrPre = OVERRIDE_QUESTION
            else:
                overrideQuestionOrPre = OVERRIDE_PRE_INSTRUCTION

            shotOrStat = self.path.split('/')[3]
            if shotOrStat == "shot":
                overrideShotOrStat = OVERRIDE_SHOT
            else:
                overrideShotOrStat = OVERRIDE_STAT

        elif self.path.endswith("/continue"):
            print("continue (no override)")

            controller_output = {
                "override": "False"
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/shotChoice") or self.path.endswith("/statChoice") or self.path.endswith("/chooseForMe"):
            print("override selected by user")

            controller_output = {
                "override": "True"
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/shotSelection"):
            print("shot selected")
            hand = self.path.split('/')[1]
            localShot = shot
            controller_output = {
                "hand": hand,
                "shot_selection": localShot
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/statSelection"):
            print("stat selected")
            stat = self.path.split('/')[1]
            controller_output = {
                "stat_selection": stat
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/handChoice"):
            print("hand choice post")
            shot = self.path.split('/')[1]

        print("Post sending response")
        self.send_response(301)
        self.send_header('content-type', 'text/html')
        if self.path.endswith("/stop"):
            # if repCount == 0 and baselineSet:
                # Send message to robot: "You must play at least 1 shot before you can end this baseline set."
            # else:
            print("post going to stop screen")
            self.send_header('Location', '/stop')
        elif self.path.endswith("/overrideOption"):
            self.send_header('Location', '/override')
        elif self.path.endswith("/handChoice"):
            self.send_header('Location', '/handChoice')
        else:
            if self.path.endswith("/ok"):
                if previous_page is None:
                    self.send_header('Location', '/display')
                else:
                    self.send_header('Location', previous_page)
            else:
                self.send_header('Location', '/display')
        self.end_headers()


if __name__ == '__main__':
    PORT = 8000
    server_address = ('0.0.0.0', PORT)
    server = HTTPServer(server_address, requestHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()
    # app.run()  # run our Flask app