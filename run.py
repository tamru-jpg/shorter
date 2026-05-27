from flask import render_template

from app import create_app

app = create_app()

@app.route('/test-500')
def test_500():
    return render_template('errors/500.html')
if __name__ == '__main__':
    print("http://127.0.0.1:5000")
    app.run()