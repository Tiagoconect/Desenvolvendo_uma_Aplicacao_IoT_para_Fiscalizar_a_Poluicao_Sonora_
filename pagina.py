from flask import Flask, render_template

pagina = Flask(__name__)

@pagina.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    pagina.run(debug=True)
