from flask import Flask, render_template, request, jsonify

from foundry_agent import ask_agent


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        })

    try:

        result = ask_agent(question)

        return jsonify({
            "answer": result
        })

    except Exception as error:

        print("Foundry Agent Error:", error)

        return jsonify({
            "answer": f"Error: {str(error)}"
        }), 500


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )