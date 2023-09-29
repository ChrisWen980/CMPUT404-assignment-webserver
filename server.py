#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


######################################################################################################################################################
# References: - https://stackoverflow.com/questions/13503610/how-can-i-get-the-path-of-my-python-script
#             - https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
#             - https://www.geeksforgeeks.org/how-to-read-from-a-file-in-python/
######################################################################################################################################################


class MyWebServer(socketserver.BaseRequestHandler):

    ######################################################################################################################################################
    # Function Purpose: Calls the functions needed to handle the request.
    # Returns: Returns nothing indicating the completion of a request.
    ######################################################################################################################################################
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.datalist = self.data.decode('utf-8').split(' ')
        # Check to see if the method is accepted, if it isn't respond with 405 Method Not Allowed and end the request
        if not self.checkMethod():
            return
        # Get the complete path for the request
        filePath = self.createPath()
        # Check to see if the path exists, if it doesn't respond with 404 Not Found and end the request
        if not self.checkPath(filePath):
            return
        # Check to see if the file exists, respond with the corresponding status codes and end the request
        else:
            self.findFile(filePath)
            return
                
    ######################################################################################################################################################
    # Function Purpose: Checks to see if the method in the request is allowed (only GET should be allowed).
    # Returns: Returns False if the method is not allowed, returns True if the method is allowed.
    ######################################################################################################################################################
    def checkMethod(self):
        errorMethods = ['POST', 'PUT', 'DELETE']
        if self.datalist[0] in errorMethods:
            self.request.sendall(bytearray('HTTP/1.1 405 Method Not Allowed \r\n', 'utf-8'))
            return False
        else:
            return True
        
    ######################################################################################################################################################
    # Function Purpose: Checks to see if the method in the request is allowed (only GET should be allowed).
    # Returns: Returns False if the method is not allowed, returns True if the method is allowed.
    ######################################################################################################################################################
    def createPath(self):
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        webPath = '/www' + self.datalist[1]
        filePath = scriptPath + webPath
        return filePath
    
    ######################################################################################################################################################
    # Function Purpose: Checks to see if the path requested by the GET method exists.
    # Returns: Returns True if the path does exist, returns False if the path isn't found.
    ######################################################################################################################################################
    def checkPath(self, filePath):
        print('Starting checkPath...\n')
        print('This is filePath: ', filePath, '\n')
        if os.path.exists(filePath):
            return True
        else:
            print('filePath ', filePath, ' does not exist\n')
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found \r\n', 'utf-8'))
            return False


    ######################################################################################################################################################
    # Function Purpose: Checks to see if the file requested by the GET method exists. Assigns the index.html file by default if no file is specified.
    # Returns: Returns nothing, indicating the completion of the request.
    ######################################################################################################################################################
    def findFile(self, filePath):
        print('Starting findFile...\n')
        print('This is filePath: ', filePath, '\n')
        # If the path references a directory and doesn't end with '/'
        if os.path.isdir(filePath) and filePath[-1] != '/':
            filePath += '/'
            self.request.sendall(bytearray('HTTP/1.1 301 Moved Permanently \r\n', 'utf-8'))
            self.request.sendall(bytearray("Location: " + filePath, 'utf-8'))
        print('This is filePath: ', filePath, '\n')

        # If the path exists give the 200 OK status code, otherwise give the 404 Not Found error code and end the request
        if os.path.exists(filePath):
            print('Path ', filePath, ' exists.\n')
            if os.path.isdir(filePath) and filePath[-1] == '/':
                filePath += 'index.html'
            self.request.sendall(bytearray('HTTP/1.1 200 OK \r\n', 'utf-8'))
            fileType = mimetypes.guess_type(filePath)[0]
            self.request.sendall(bytearray('Content-Type: ' + fileType + '; \r\n', 'utf-8'))
            openFile = open(filePath, 'r')  
            self.request.sendall(bytearray(openFile.read(),'utf-8'))
            openFile.close()
        else:
            print('Path ', filePath, ' does not exist.\n')
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found \r\n', 'utf-8'))
        return
    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
