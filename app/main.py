from flask import Flask, render_template
from app.routes.statistics_route import statistics_bp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.register_blueprint(statistics_bp, url_prefix='/statistics')
    app.run(debug=True)