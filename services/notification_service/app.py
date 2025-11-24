from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return {"message": " notification_service is running"}

if __name__ == "__main__":
    app.run(port=5005, debug=True)
