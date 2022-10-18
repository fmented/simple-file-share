#!/usr/bin/env python3
from io import BytesIO
import os, json
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse as urlparse
from html import escape as html_escape
from mimetypes import MimeTypes
from cgi import FieldStorage
from pathlib import Path
from stat import FILE_ATTRIBUTE_HIDDEN
from socketserver import ThreadingMixIn
from http import HTTPStatus

PORT = 80

DEBUG = False

def assign_mimetypes(mt:MimeTypes):
    mj = '''$$MIME'''

    mime = json.loads(mj)
    for m in mime:
        for t in m['types']:
            mt.add_type(m['name'], t)

class Logger():
    @staticmethod
    def log(*args):
        print(*args)

class Page():
    def __init__(self, baseHTMLBody='', baseHTMLHead='', baseCSS='', baseJS=''):
        self.baseHTMLBody = baseHTMLBody
        self.baseHTMLHead = baseHTMLHead
        self.baseCSS = baseCSS
        self.baseJS = baseJS
    
    def construct(self, title, head='', body='', CSS='', JS=''):
        html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            {head}
            {self.baseHTMLHead}
            <style>{CSS}</style>
            <style>{self.baseCSS}</style>
        </head>
        <body>
            {body}
            {self.baseHTMLBody}
            
            <script>{JS}</script>
            <script>{self.baseJS}</script>
        </body>
        </html>
        '''

        return html

    def build(self, title, head='', body='', CSS='', JS=''):
        html = self.construct(title, head, body, CSS, JS)
        return bytes(html, 'utf-8')

page = Page(
    baseHTMLHead="<link rel='icon' type='image/svg+xml' href='/favicon.ico'>", 
    
    baseCSS='''$$CSS''',
    
    baseJS = '''$$JS'''

)

page.favicon = '''$$FAVICON'''

class FileInfo():
    units_map = [
            (1<<40, 'TB'),
            (1<<30, 'GB'),
            (1<<20, 'MB'),
            (1<<10, 'KB'),
            (1, ('Byte', 'Bytes'))        
        ] 

    mimetypes = MimeTypes()
    if not ('.docx' in mimetypes.types_map): assign_mimetypes(mimetypes)

    @staticmethod
    def has_hidden_attribute(file):
        return bool(os.stat(file).st_file_attributes & FILE_ATTRIBUTE_HIDDEN)

    @staticmethod
    def is_hidden(file):
        name:str = os.path.basename(os.path.abspath(file))
        if os.name == 'nt':
            return FileInfo.has_hidden_attribute(file)
        return name.startswith('.')

    def __init__(self, basedir, file):
        fullname = os.path.join(basedir, file)
        displayname = linkname = file
        self.size = None
        if os.path.isdir(fullname):
            displayname = file + "/"
            linkname = file + "/"
            self.type = 'folder'
        elif os.path.islink(fullname):
            displayname = file + "@"
            self.type = 'link'
        else:
            self.type = self.mimetypes.guess_type(fullname)[0]
            self.size = os.path.getsize(fullname)
        
        self.displayname = html_escape(displayname)
        self.linkname= urlparse.quote(linkname)
        self.hidden = self.is_hidden(fullname)

    @property
    def pretty_size(self):
        if self.type == "folder" or self.type=="link":
            return None 
        if self.size == 0:
            return "0 Bytes"
        for factor, suffix in self.units_map:
            if self.size >= factor:
                amount = int(self.size / factor)
                if isinstance(suffix, tuple):
                    sg, mt = suffix
                    return f'{amount} {sg if amount==1 else mt}'
                return f"{amount} {suffix}"

class FileCrawler():
    def get_file_list(self, path):
        files = os.listdir(path)
        files.sort(key=str.casefold)
        files.sort(key=lambda a:         
            os.path.isdir(os.path.join(path, a)) or os.path.islink(os.path.join(path, a)), reverse=True
        )
        return files

    def list_files(self, path):
        files = self.get_file_list(path)
        return [FileInfo(path, file) for file in files]

    def serialize_filelist(self, list):        
        return json.dumps([{**f.__dict__, **{"pretty_size":f.pretty_size}} for f in list])

    def crawl(self, path):
        return self.serialize_filelist(self.list_files(path))

class Handler(SimpleHTTPRequestHandler): 
    def __init__(self, request, client_address, server) -> None:
        self.crawler = FileCrawler()
        self.page = page
        self.error_page = Page(baseHTMLHead=page.baseHTMLHead, baseCSS=page.baseCSS)
        super().__init__(request, client_address, server)

    def has_param(self, param:str):
        o = urlparse.urlparse(self.path)
        q = urlparse.parse_qs(o.query)
        return param in q

    def is_streamable(self):
        path = self.translate_path(self.path)
        file = os.path.isfile(path)
        if not file: return False
        type = FileInfo.mimetypes.guess_type(path)[0]
        streamable = type is not None and (type.startswith('video') or type.startswith('audio'))
        return self.has_param('stream') and streamable  

    def create_folder(self):
        p = urlparse.unquote(urlparse.urlparse(self.path).path)
        path = Path(os.getcwd() + p)       
        form = FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
        if 'name' not in form: return (HTTPStatus.BAD_REQUEST, 'Field "name" not found')
        name = form.getvalue('name')
        try:
            os.mkdir(os.path.join(path, name))
            self.send_response(HTTPStatus.CREATED)
            self.send_header('Content-Length', '0')
            self.end_headers()
        except IOError:
            self.send_response(HTTPStatus.FORBIDDEN)
            self.send_header('Content-Length', '0')
            self.end_headers()
        self.wfile.write(bytes(b''))

    def receive_upload(self):
        result = (HTTPStatus.INTERNAL_SERVER_ERROR, 'Server error')
        p = urlparse.unquote(urlparse.urlparse(self.path).path)
        path = Path(os.getcwd() + p)       
        form = FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
        if 'files' not in form: return (HTTPStatus.BAD_REQUEST, 'Field "files" not found')
        
        fields = form['files']
        if not isinstance(fields, list):
            fields = [fields]
        
        for field in fields:
            if field.file and field.filename:
                filename = Path(field.filename).name
            else:
                filename = None
            
            if filename:
                with open(path / filename, 'wb') as f:
                    f.write(field.file.read())
                    result = (HTTPStatus.CREATED, None)
        
        self.send_response(result[0], result[1])
        self.send_header('Content-Length', '0')
        self.end_headers()
        self.wfile.write(bytes(b''))
        
    def send_json(self):
        path = self.translate_path(self.path)
        try:
            list = self.crawler.crawl(path)
            f = bytes(list, 'utf-8')
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.send_header('content-length', str(len(f)))
            self.end_headers()
            self.wfile.write(f)            

        except: self.send_error(HTTPStatus.FORBIDDEN, f"Cannot access {path}")
        
    def send_favicon(self):
        f = bytes(self.page.favicon, 'utf-8')
        self.send_response(200)
        self.send_header('content-type', 'image/svg+xml')
        self.send_header('content-length', str(len(f)))
        self.end_headers()
        self.wfile.write(f)      

    def log_request(self, format, *args): pass
 
    def do_GET(self):
        if self.path == '/favicon.ico': return self.send_favicon()
        if self.has_param('updateList'): return self.send_json()
        try:
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()  
        except (ConnectionAbortedError, ConnectionResetError): pass
                           
    def do_HEAD(self):
        f = self.send_head()
        if f: f.close()
 
    def do_POST(self):
        if self.has_param('upload'): self.receive_upload()     
        elif self.has_param('newfolder'): self.create_folder()       
        else: self.send_error(HTTPStatus.FORBIDDEN, 'Cannot POST to this URL')
 
    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else: return self.list_directory()

        ctype = FileInfo.mimetypes.guess_type(path)[0]
        try: f = open(path, 'rb')
        except IOError:
            self.send_error(HTTPStatus.NOT_FOUND, f"{self.path} not found")
            return None
        
        fs = os.fstat(f.fileno())       
        range = self.headers.get('Range')

        if self.is_streamable() and range is not None:
            # set chunk size to 2MB
            chunk = 2000 * 1024 
            range = range.split('=')[1].split('-')
            range[0] = int(range[0])
            range[1] = (range[0] + chunk) if (range[0] + chunk) <= fs[6] else fs[6]

            f.seek(range[0])
            data = f.read(range[1]-range[0])
            f.close()

            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-type", ctype)
            self.send_header("Accept-Range", 'bytes')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Range", f'bytes {range[0]}-{range[1]-1}/{fs[6]}')
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()          
            return BytesIO(data)
        
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def send_error(self, code, message):
        self.send_response(code)
        p = self.error_page.build(f'Error {message}', 
            body=f'<main><h1>😢 Something Went Wrong</h1><h2>{code} : {message}</h2></main>',
            CSS='h1, h2 {text-align:center;} body{display: grid; place-items:center;}'
            
            )
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(p)))
        self.end_headers()
        self.wfile.write(p)

    def list_directory(self):
        p = self.translate_path(self.path)
        page = self.page.build(f'List Files from {p}')
        l = len(page)
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(l))
        self.end_headers()
        self.wfile.write(page)

class CustomServer(ThreadingMixIn, HTTPServer):
    suppress_error = False

    def handle_error(self, *args):
        if (not self.suppress_error): return super().handle_error(*args)

    def server_activate(self) -> None:
        Logger.log('\nCreating server .....')
        super().server_activate()
        print_ip_address(PORT)
        Logger.log('\nServer is running .....')

    def shutdown(self) -> None:
        super().shutdown()
        Logger.log('\nServer is terminated')


def print_ip_address(port):
    import subprocess, re

    def get_ip():
        run = lambda cmd: subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.DEVNULL).communicate()[0].decode('utf-8')

        if os.name == 'nt':
            out = run('ipconfig')
            x = re.findall('IPv4.*: (([0-9]|\.)*)', out)
            return [i[0] for i in x]

        out1 = run('ip address')
        out2 = run('ifconfig')
        x = re.findall('inet (([0-9]|\.)*)', f'{out1}\n{out2}')
        return [*set([i[0] for i in x])]

    Logger.log_ip = lambda t: Logger.log(f'   http://{t}'+ ('' if port == 80 else f':{port}'))

    ni = list(filter(lambda ip: ip != '127.0.0.1', get_ip()))
    client = []; gate = []

    for n in ni: gate.append(n) if n.endswith('.1') else client.append(n)
    if len(client) > 0: Logger.log('\nClient Address :'); [Logger.log_ip(ip) for ip in client]
    if len(gate) > 0: Logger.log('\nGateway Address :'); [Logger.log_ip(ip) for ip in gate]
    Logger.log('\nLoopback Address'); Logger.log_ip('127.0.0.1')

def create_server():
    Handler.protocol_version = "HTTP/1.1"
    addr = ('0.0.0.0', PORT)
    httpd = CustomServer(addr, Handler)
    httpd.suppress_error = not DEBUG
    httpd.daemon = True
    httpd.daemon_threads = True
   
    return httpd

def run():
    with create_server() as httpd:
        try: httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            os.sys.exit(0)

def serve():
    try: run()
    except PermissionError:
        handle_permission_error()
        serve()      
    except OSError: handle_os_error()

def is_android():
    # there has to be a better way to do this
    from sys import prefix
    andro_app_detected = 'qpython' in prefix or 'pydroid' in prefix or 'termux' in prefix
    andro_env_detected = 'ANDROID_DATA' in os.environ
    return andro_app_detected or andro_env_detected

def handle_permission_error():
    if os.name == 'posix':
        global PORT
        PORT = 8080
        Logger.log(f'\nPort below 1024 requires super user privilege')
        Logger.log(f'\nPort is redirected to {PORT}')
    else: os.sys.exit(1)

def handle_os_error():
    if os.name == 'posix':      
        msg = f"\nChange the port or close the previous program"
        andro_msg = f"\nChange the port or restart the application"
        Logger.log(f"\nPort {PORT} is already used")
        Logger.log(andro_msg if is_android() else msg)
    os.sys.exit(1)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port', action='store',
                            type=int,
                            nargs='?',
                            help='Specify alternate port [default: 80]')

    parser.add_argument('--dir', '-d',
                            help='Specify alternative directory [default:current directory]')

    args = parser.parse_args()

    if args.port: PORT = args.port
    if args.dir: 
        try: os.chdir(args.dir)
        except: pass

    os.system("cls" if os.name == "nt" else "clear")

    if not is_android(): serve()
    else:      
        init = False; fail = False

        # elevating directory equivalent to /sdcard to have less restricted access
        # most android app will set cwd to /data/user/0/PACKAGE_NAME/files/
        # which is very restricted if the phone is unrooted
        os.chdir('/storage/emulated/0')      

        class Wrapper(Thread):   
            def run(self):
                global init; global fail
                try:
                    self.server = create_server()           
                    init = True
                    self.server.serve_forever()
                except PermissionError: 
                    handle_permission_error()
                    self.run()
                except OSError: fail = True
                finally: init = True
                       
            def stop(self):     
                if fail : return
                self.server.shutdown()   

        t = Wrapper()
        t.start()    

        # hacky way to support android phone that cannot trigger KeyboardInterrupt
        # normally vol down button mapped to CTRL 
        # however just in case the volume button is broken or the app doesnt support it
        # user can still stop the server with just on-screen keyboard
        # stoping the server is necessary to close the socket connection
        # otherwise the unclosed port wont be avilable until the app is closed and reopened

        def close(*args):
            t.stop()
            t.join()
            os.sys.exit(0)

        # this part is to mitigate weird python behavior while doing input() and pressing CTRL-C
        # while pressing CTRL-C python didnt raise KeyboardInterrupt
        # but after pressing CTRL-C and followed by CTRL-D python did raise both
        # however the exception block below didnt catch any of them
        # but if only CTRL-D is pressed, the exception block below did catch EOFError

        import signal
        signal.signal(signal.SIGINT, close)

        while not init: pass
        if not fail: 
            try: input("\nPress enter to stop the server\n")   
            except (EOFError, KeyboardInterrupt): pass               
        close()  