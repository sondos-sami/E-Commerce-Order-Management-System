from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return {"message": "inventory_service is running"}

if __name__ == "__main__":
    app.run(port=5002, debug=True)
