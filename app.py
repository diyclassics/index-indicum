from app import app

app.config['SECRET_KEY'] = "This key need to be changed and kept secret"

if __name__ == '__main__':
    app.run()

