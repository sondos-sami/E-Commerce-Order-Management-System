from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return {"message": "order_service is running"}


@app.get("/test")
def test():
    return {"status": "service running"}


if __name__ == "__main__":
    app.run(port=5001, debug=True)
