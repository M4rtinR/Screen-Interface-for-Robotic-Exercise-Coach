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
post_address = "http://192.168.1.207:4999/output"
controller_post_address = "http://192.168.1.207:5000/cue"
ssh = paramiko.SSHClient()
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
# 4G hotspot:
# ssh.connect("192.168.43.57", username="nao", password="nao")
# ITT_Pepper router:
ssh.connect("192.168.1.5", username="nao", password="nao")

class requestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("get")
        global displayStringSpaces
        global picName
        global phase
        global repCount
        if self.path.endswith('/display'):
            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            #output = '<!DOCTYPE html><html><body><p>test</p></body></html>'

            output = '<!DOCTYPE html>'

            if phase == NON_EXERCISE:
                print("non-exercise")
                output += '<html><body>'
                output += '<div style="height:80%; background:black; position:absolute">'  # Main div
                output += '<button type="button" style="position:absolute; bottom:0; right:0, width:20%; height:20%; font-size:xx-large;">Repeat</button>'  # Repeat button
                output += '</div>'
                output += '<div style="height:20%; width:100%; background:grey; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
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
                output += '<div style="height:80%; position:absolute">'  # Main div
                # output += '<button type="button" style="position:absolute; top:10px; left:40%;">Stop</button>'  # Stop button
                # output += '<form action="http://192.168.1.207:8000/stop" method="POST"><button type="button" id="stop-btn" name="stop_button" value="stop" style="position:absolute; top:0px; left:40%;, width:20%; height:20%; font-size:xx-large;">Stop</button></form>'
                output += '<form action="http://192.168.1.207:8000/stop" method="POST">'
                output += '<input type="submit" name="stop" value="Stop" style="position:absolute; top:0px; left:40%;, width:20%; height:20%; font-size:xx-large;" />'
                output += '</form>'
                if picName is not None:
                    data_uri = base64.b64encode(open(picName, 'rb').read()).decode('utf-8')
                    output += '<img src="data:image/png;base64,{0}" alt="Current exercise" style="width:70%; height:100%; object-fit:fill;">'.format(data_uri)  # Exercise image
                output += '<div style="text-align:center;font-size:2000%;line-height:100%;width:30%;position:absolute;right:0;display:inline-block;padding:7.3% 0">' + repCount + '</div>'  # Rep counter
                output += '<button type="button" style="position:absolute; bottom:0; right:0;, width:20%; height:20%; font-size:xx-large;">Repeat</button>'  # Repeat button
                output += '</div>'
                output += '<div style="height:20%; width:100%; background:grey; display: flex; justify-content: center; align-items: center; position: absolute; bottom:0;">'  # Subtitle div
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
            self.send_response(200)
            self.send_header('content-type', 'text-html')
            self.end_headers()

            output = '<!DOCTYPE html>'

            print("stop screen")
            output += '<html><body>'
            output += '<div style="height:40%; width:100%; display: flex; justify-content: center; align-items: center; position:absolute; top:0;">'  # Main div
            output += '<div style="flex: 0 0 90%; text-align: center; font-size: xxx-large">Would you like to stop the whole session or just this exercise set?</div>'  # Repeat button
            output += '</div>'
            output += '<div style="height:60%; width:100%; background:grey; display: flex; justify-content: center; align-items: center; position:absolute; bottom:0;">'  # Subtitle div
            output += '<form action="http://192.168.1.207:8000/stopSession" method="POST">'
            output += '<input type="submit" name="stop_session" value="Stop Session" style="padding:30px; font-size:xx-large; margin-right:10%" />'
            output += '</form>'
            output += '<form action="http://192.168.1.207:8000/stopExercise" method="POST">'
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

            '''# Send signal to robot to pause the session.
            output = {
                "pause": "1"
            }
            r = requests.post(post_address, json=output)'''


    def do_POST(self):
        global displayStringSpaces
        global picName
        global phase
        global repCount
        if self.path.endswith('/newUtterance'):
            print(self.path)
            displayString = self.path.split('/')[1]
            phaseString = self.path.split('/')[2]
            # ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            # if ctype == 'application/json':
            displayStringSpaces = displayString.replace('%20', ' ')
            phase = phaseString == "exercise"
            # else:
            #     print("Didn't work")

        elif self.path.endswith('/newPicture'):
            # ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            # if ctype == 'application/json':
            picName = "ExercisePhotos/" + self.path.split('/')[1] + "Series.png"
            print("new picture: " + picName)
                #picName = picName + ".png"
            # else:
            #     print("Didn't work")

        elif self.path.endswith("/newRep"):
            repCount = self.path.split('/')[1]
            print("new rep: " + repCount)

        elif self.path.endswith("/stop"):
            print("POST stop")
            # Send signal to robot to pause the session.
            output = {
                "pause": "1"
            }
            r = requests.post(post_address, json=output)

        elif self.path.endswith("/stopSession"):
            # TODO: send message to controller with session goal PHASE_END, unpause and delete paused action.
            print("POST stopSession")
            pepper_output = {
                "pause": "3",
                "stop": "1"
            }
            r = requests.post(post_address, json=pepper_output)

            controller_output = {
                "goal_level": 1
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/stopSet"):
            # TODO: send message to controller with set goal PHASE_END, unpause and delete paused action.
            print("POST stopSet")
            pepper_output = {
                "pause": "0",
                "stop": "1"
            }
            r = requests.post(post_address, json=pepper_output)

            controller_output = {
                "goal_level": 2
            }
            r = requests.post(controller_post_address, json=controller_output)

        elif self.path.endswith("/cancel"):
            # TODO: unpause and execute paused action.
            print("POST stopSession")
            output = {
                "pause": "0"
            }
            r = requests.post(post_address, json=output)

        self.send_response(301)
        self.send_header('content-type', 'text/html')
        if self.path.endswith("/stop"):
            self.send_header('Location', '/stop')
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