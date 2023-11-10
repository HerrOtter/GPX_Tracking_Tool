from app import app, db
import os

if not os.path.exists('database'):
    os.makedirs('database')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)