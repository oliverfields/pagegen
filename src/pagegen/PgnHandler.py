import os
from http.server import SimpleHTTPRequestHandler
import mimetypes

ROUTES = [
    ('/assets/', '/home/oliver/Documents/tidesofsea/assets'),
]

class PgnHandler(SimpleHTTPRequestHandler):
    '''
    serves a pagegen site over http locally
    '''

    def __init__(self, serve_dir, site_base_url, serve_base_url, routes, directory_index, *args, **kwargs):
        # Extract additional variables passed
        self.serve_dir = serve_dir
        self.site_base_url = site_base_url
        self.serve_base_url = serve_base_url
        self.directory_index = directory_index

        # Routes format:
        # [
        #   ('<url path>', '<file system path>')
        #   [,...]
        # ]
        self.routes = routes

        super().__init__(*args, **kwargs)


    def translate_path(self, path):
        '''
        maps urls to filesystem objects
        '''

        # Strip any query strings or anchor # from url
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]

        # default root -> cwd
        root = self.serve_dir

        # look up routes and get root directory
        for patt, rootDir in self.routes:
            if path.startswith(patt):
                path = path[len(patt):]
                root = rootDir
                break

        # new path
        path = os.path.join(root.rstrip(os.path.sep), path.lstrip(os.path.sep))

        return path


    def do_GET(self):
        '''
        for files that have no extension, or certain extensions serve using custom logic, for all others use standard httpserver
        '''

        if not '.' in os.path.basename(self.path) or self.path.endswith(('.htm', '.html', '.css', '.js')):
            self.serve_and_modify_file()
        else:
            super().do_GET()


    def serve_and_modify_file(self):
        '''
        set mime types and rewrite any mention of section site, setting base_url to local address
        '''

        # Find the correct path to the file
        file_path = self.translate_path(self.path)

        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, self.directory_index)

        # Open and read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace base_url with 'http://localhost'
            modified_content = content.replace(self.site_base_url, self.serve_base_url)

            # Determine the MIME type for the response
            mime_type, _ = mimetypes.guess_type(self.path)
            if mime_type is None:
                mime_type = 'text/html'

            # Send response headers
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.end_headers()

            # Write the modified content to the response
            self.wfile.write(modified_content.encode('utf-8'))

        except FileNotFoundError:
            self.send_error(404, "File Not Found")


#if __name__ == '__main__':
#    httpd = HTTPServer(('127.0.0.1', 8000), PgnHandler)
#    httpd.serve_forever()
