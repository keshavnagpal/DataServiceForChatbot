from sanic import Sanic, response
import json

app = Sanic()

@app.route("/")
async def test(request):
    return response.json({"Default App": "Running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)