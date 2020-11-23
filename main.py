from app import create_app, db
from app.models import User, Post, Like

app = create_app()


@app.shell_context_processor
def make_shell_processor():
    return {'db': db, 'User': User, 'Post': Post, 'Like': Like}


if __name__ == '__main__':
    app.run()
