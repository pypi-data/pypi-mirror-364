# main.py (Alternative Correction)
from Velra import *

app_instance = VelraApp(__name__)

@app_instance.route('/hello')
def hello():
    return app_instance.render('index.html')

@app_instance.route('/', endpoint='main_home_page')
def home():
    return "Welcome to the Velra test application! Go to /hello to see custom rendering."

if __name__ == '__main__':
    app_instance.run(debug=True)