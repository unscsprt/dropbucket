import sys

from flask         import Flask, send_from_directory, request, redirect, \
                            url_for
from datetime      import datetime
from time          import sleep
from threading     import Thread

from fileutils     import *
from converter     import RegexConverter
from template      import render
from constants     import *

app = Flask(__name__)
app.url_map.converters['regex'] = RegexConverter
app.config['UPLOAD_FOLDER'] = PATH_DATASTORE

# Routes ------------------------------------------------------------------
@app.route('/')
def route_root():
    return render('index.jade', {'files': get_file_info()})


# Upload and download files
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(PATH_DATASTORE, filename)

@app.route('/upload', methods=['POST'])
def upload_runner():
    try:
        f      = request.files.get('upload')
        thread = Thread(target=upload_file, args=[f])
        thread.daemon = True
        thread.start()
    except:
        print traceback.format_exc()
    return redirect('/')


# Debug
@app.route('/debug/list_files')
def debug_list_files():
    return map(lambda f: f+' ', list_files())

# Static assets
@app.route('/<regex(".*\.js"):filename>')
def javascripts(filename):
    return url_for('static', filename=filename)

@app.route('/<regex(".*\.css>"):filename>')
def stylesheets(filename):
    return url_for('static', filename=filename) 

@app.route('/<regex(".*\.(jpg|png|gif|ico)"):filename>')
def images(filename):
    return url_for('static', filename=filename)

@app.route('/<regex(".*\.(eot|ttf|woff|svg)"):filename>')
def fonts(filename):
    return url_for('static', filename=filename)


# Server ------------------------------------------------------------------
def main():
    # dummy call b/c strptime has thread-related bug
    datetime.strptime('2013-01-01', '%Y-%m-%d')

    # start function to delete expired files as a thread
    expire_files_thread = Thread(target=expire_files)
    expire_files_thread.daemon = True
    expire_files_thread.start()

    # start the server
    app.run(host='0.0.0.0', debug=True)

    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    main()
