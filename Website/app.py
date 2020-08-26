from flask import Flask, render_template, request



app = Flask(__name__)

@app.route("/")
def index():
   
    return render_template("index.html")

@app.route("/separation", methods =['POST'])

def separation():

    if request.method == "POST":

        url = request.form["mix"]
        print(url)


    return render_template("results.html")

if __name__ == '__main__':
    app.run()
