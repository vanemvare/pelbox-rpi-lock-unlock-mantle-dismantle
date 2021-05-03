from flask import Flask
from rpi.management import management

app = Flask(__name__)
app.register_blueprint(management)

def main():
    app.run(host='0.0.0.0', port=9002)

if __name__ == "__main__":
    main()