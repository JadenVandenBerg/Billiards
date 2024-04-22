import sys
import cgi
import Physics
import math
import os
import json
import time

# web server parts
from http.server import HTTPServer, BaseHTTPRequestHandler

# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse, parse_qsl

def write_svg( table_id, table ):
    with open( "table%d.svg" % table_id, "w" ) as fp:
        fp.write( table.svg() )

tableId = 0
tablePOSTId = 0
currentAmongusTable = None
db = Physics.Database(True)
db.createDB()
game = Physics.Game(None, "ok", "ok2", "ok3")

# handler for our web-server - handles both GET and POST requests
class MyHandler( BaseHTTPRequestHandler ):
    def do_GET(self):
        # parse the URL to get the path and form data
        parsed  = urlparse( self.path )
        print(parsed)

        # check if the web-pages matches the list
        if parsed.path in [ '/home.html' ]:

            fp = open( '.'+self.path )
            content = fp.read()

            self.send_response( 200 )
            self.send_header( "Content-type", "text/html" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()

        elif 'css' in parsed.path:
            fp = open( '.'+self.path )
            content = fp.read()

            self.send_response( 200 )
            self.send_header( "Content-type", "text/css" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()

        elif 'js' in parsed.path:
            fp = open( '.'+self.path )
            content = fp.read()

            self.send_response( 200 )
            self.send_header( "Content-type", "application/javascript" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()

        # check if the web-pages matches the list
        elif 'table' in parsed.path:
            # get the form data and turn it into a dictionary
            print(parsed.path)

            # retreive the HTML file & insert form data into the HTML file
            if os.path.exists(parsed.path[1:]):
                fp = open( '.'+parsed.path )
                content = fp.read()

                # generate the headers
                self.send_response( 200 ) # OK
                self.send_header( "Content-type", "image/svg+xml" )
                self.send_header( "Content-length", len( content ) )
                self.end_headers()

                # send it to the browser
                self.wfile.write( bytes( content, "utf-8" ) )
                fp.close()
            else:
                self.send_response( 404 ) # OK
                self.end_headers()

        elif 'display' in parsed.path:

            global tableId
            tableId += 1

            fp = None
            content = None
            try:
                fp = open( "table%02d.svg" % tableId, "r" )
                content = fp.read()
            except:
                self.send_response( 404 )
                self.end_headers()
                return


            self.send_response( 200 )
            self.send_header( "Content-type", "image/svg+xml" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()


        else:
            # generate 404 for GET requests that aren't the files above
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) )


    def do_POST(self):
        # hanle post request
        # parse the URL to get the path and form data
        parsed  = urlparse( self.path )

        if "amongus.html" in parsed.path:
            global tablePOSTId
            counter = 1
            while os.path.exists("table%d.svg" % counter):
                os.remove("table%d.svg" % counter)
                counter+=1

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            data = json.loads(post_data.decode('utf-8'))
            print("Received array:", data)
            print(data[0])
            print(data[1])

            global currentAmongusTable
            if currentAmongusTable is None:
                currentAmongusTable = Physics.generateStartTableNoStr()

            # Init game in name post request
            db = Physics.Database()

            if currentAmongusTable.cueBall() is None:
                currentAmongusTable = db.readTable( tablePOSTId )
            print(currentAmongusTable.cueBall())
            print(currentAmongusTable)

            currentAmongusTable = currentAmongusTable.copyTable(currentAmongusTable)

            global game
            game.shoot("ok", "ok2", currentAmongusTable, data[0], data[1])

            table_id = 0
            table = db.readTable( tablePOSTId )
            currentAmongusTable = table

            while table:
                table_id += 1
                tablePOSTId += 1
                table = db.readTable( tablePOSTId + 1 )
                if not table:
                    break
                else:
                    currentAmongusTable = table
                write_svg( table_id, table )
    

            # generate the headers
            content = str(table_id)
            self.send_response( 200 ) # OK
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            # send it to the browser
            self.wfile.write( bytes( content, "utf-8" ) )

            db.close()

            
        if parsed.path in [ '/display.html' ]:

            # get data send as Multipart FormData (MIME format)
            form = cgi.FieldStorage( fp=self.rfile,
                                     headers=self.headers,
                                     environ = { 'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': 
                                                   self.headers['Content-Type'],
                                               } 
                                   )
                                
            # read the file that came in the form and write it to local dir

            p1 = form["p1"].value
            p2 = form["p2"].value

            content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <link rel="shortcut icon" href="#">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
            <script src="script.js"></script>
            <style>
                html, body {{
                    font-family: Verdana, sans-serif;
                    color: white;
                    height: 100% !important;
                    background: darkgreen;
                }}
                table {{
                    background: #ffffff70;
                    width: 100%;
                    border-collapse: collapse;
                }}
                td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                    height: 50vh !important;
                    color: black;
                }}
                img {{
                    display: block;
                    margin: 0 auto;
                    height: 100%;
                }}
                .btn {{
                    background: #008c48;
                    background-image: -webkit-linear-gradient(top, #008c48, #000000);
                    background-image: -moz-linear-gradient(top, #008c48, #000000);
                    background-image: -ms-linear-gradient(top, #008c48, #000000);
                    background-image: -o-linear-gradient(top, #008c48, #000000);
                    background-image: linear-gradient(to bottom, #008c48, #000000);
                    -webkit-border-radius: 4;
                    -moz-border-radius: 4;
                    border-radius: 4px;
                    font-family: Courier New;
                    color: #ffffff;
                    font-size: 20px;
                    padding: 10px 20px 10px 20px;
                    border: solid #000000 2px;
                    text-decoration: none;
                }}
                .btn:hover {{
                    background: #3e9466;
                    text-decoration: none;
                }}
            </style>
            </head>
            <body>
            <center><h1>Billiards</h1></center>
            <table>
            <td id="p1">Player 1: {p1}<br/>DARK</td>
            <td id="middleTable">{Physics.generateStartTable()}</td>
            <td id="p2">Player 2: {p2}<br/>LIGHT</td>
            </tr>
            </table>
            </body>
            </html>
            """

            # generate the headers
            self.send_response( 200 ) # OK
            self.send_header( "Content-type", "text/html" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            # send it to the browser
            self.wfile.write( bytes( content, "utf-8" ) )

        else:
            # generate 404 for POST requests that aren't the file above
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) )


if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler )
    print( "Server listing in port:  ", int(sys.argv[1]) )
    httpd.serve_forever()