#Imports :eyes:
from flask import Flask
from flask import request, render_template, redirect
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
import subprocess
import threading
import time

#Just a few variables
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt','py','python'}

app = Flask(__name__)
uploadfolder = "uploads"

app = Flask('app')

#functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#some stuff (needs to be optimised)
def sub():
  subprocess.check_output(f"python3 comp.py", shell=True, universal_newlines=True)
  
def waits(timex):
  for i in range(int(timex)):
    time.sleep(1)
    
def timer(time):
  #checking if the app times out
  x = threading.Thread(target=sub, args=())
  x.start()
  a = threading.Thread(target=waits, args=(time,))
  a.start()
  while a.is_alive():
    if x.is_alive() == False:
      return subprocess.check_output(f"python3 comp.py", shell=True, universal_newlines=True)
  return "Something went wrong...<br>looks like your request took too long to process for our servers, so we ended it."

#flask stuff
@app.route('/')
def home():
  #home base
  return "Welcome! Send python code to our servers for them to prosses for free! <br><a href='/upload-file'>upload a file to run</a>"

@app.route('/upload-file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #save
            file.save(os.path.join(uploadfolder, filename))
            #display
            f=open('server.dat','a')    
            a=open('uploads/'+file.filename,'r')
            id=uuid.uuid4()
            f.write(str(id)+'|'+a.read().replace('\n','`')+'\n')
            f.close()
            a.close()
            return redirect(f'/site/?query={id}|15')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/site/')
def runcode():
  #open stuff
  a = open('server.dat','r')
  ar = a.read()
  #code to use when there is no valid code
  code="Hmmm..."
  #get the code from the stored code
  for i in ar.split('\n'):
    if i.split('|')[0] == request.args.get('query').split('|')[0]:
      code = i.split('|')[1].replace('`','\n')
  #write and finish up
  f = open('comp.py','w')
  f.write(code)
  f.close()
  a.close()
  #display
  return timer(request.args.get('query').split('|')[1])

#Error handiling 
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html'), 404

@app.errorhandler(500)
def internalerror(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500

#Run
app.run(host='0.0.0.0', port=8080)
