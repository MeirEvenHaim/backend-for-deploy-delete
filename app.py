from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename





 ##### EYAL!!! the ADMIN USERNAME IS:meire password is :112334 ###############################
 
 
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the directory exists; create if not
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'py', 'js'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit for file upload

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
UPLOAD_FOLDER = 'uploads'


class Register(db.Model):
    __tablename__ = 'register'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    address = Column(String(100), nullable=False)
    role = Column(Enum('admin', 'client', name='role_enum'), nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    image = Column(String(200), nullable=True)
    loans = relationship('Loan', backref='client', foreign_keys='Loan.client_id')
    admin_loans = relationship('Loan', backref='admin', foreign_keys='Loan.admin_id')

    def __init__(self, username, address, role, password, email, image=None):
        self.username = username
        self.address = address
        self.role = role
        self.set_password(password)
        self.email = email
        self.image = image

    def __repr__(self):
        return f"<Register(username='{self.username}', role='{self.role}', email='{self.email}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'address': self.address,
            'role': self.role,
            'email': self.email,
            'image': self.image
        }

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    book_name = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    date_of_publish = Column(Date, nullable=False)
    summary = Column(Text, nullable=False)
    image = Column(String(200), nullable=True)
    series = Column(Boolean, nullable=False, default=False)
    loans = relationship('Loan', backref='book')

    def __init__(self, book_name, author, date_of_publish, summary, image=None, series=False):
        self.book_name = book_name
        self.author = author
        self.date_of_publish = date_of_publish
        self.summary = summary
        self.image = image
        self.series = series

    def __repr__(self):
        return f"<Book(book_name='{self.book_name}', author='{self.author}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'book_name': self.book_name,
            'author': self.author,
            'date_of_publish': self.date_of_publish.isoformat(),
            'summary': self.summary,
            'image': self.image,
            'series': self.series
        }


class Loan(db.Model):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('register.id'), nullable=False)
    admin_id = Column(Integer, ForeignKey('register.id'), nullable=False)
    loan_date = Column(Date, nullable=False, default=datetime.utcnow)
    return_date = Column(Date, nullable=False)

    def __init__(self, book_id, client_id, admin_id, return_date):
        self.book_id = book_id
        self.client_id = client_id
        self.admin_id = admin_id
        self.return_date = return_date

    def __repr__(self):
        return f"<Loan(book_id='{self.book_id}', client_id='{self.client_id}', admin_id='{self.admin_id}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'book_name': self.book.book_name,
            'client_name': self.client.username,
            'client_address': self.client.address,
            'admin_name': self.admin.username,
            'admin_address': self.admin.address,
            'loan_date': self.loan_date.isoformat(),
            'return_date': self.return_date.isoformat()
        }


# Helper functions for role checks
def is_admin(current_user):
    current_user = get_jwt_identity()
    print(current_user)
    return current_user['role'] == 'admin'


def is_client():
    current_user = get_jwt_identity()
    return current_user['role'] == 'client'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 201
    else:
        return jsonify({"error": "Allowed file types are: .pdf, .jpg, .jpeg, .png, .gif, .txt, .py, .jfif"}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


# Endpoint to login and get a JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = Register.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity={
            'username': user.username,
            'role': user.role,
            'id': user.id  # Include the user's ID in the JWT token
        })
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401
# Endpoint to create a new user

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    address = data.get('address')
    role = data.get('role')
    password = data.get('password')
    email = data.get('email')
    image = data.get('image')  # Assuming you might include image in registration

    if not username or not address or not role or not password or not email:
        return jsonify({"error": "Missing required fields"}), 400

    existing_user = Register.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    new_user = Register(username=username, address=address, role=role, password=password, email=email, image=image)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# Endpoint to get details of all users (protected)
@app.route('/register', methods=['GET'])
def get_all_users():
    users = Register.query.all()
    return jsonify([user.to_dict() for user in users]), 200


# Endpoint to get details of a specific user by ID (protected)
@app.route('/register/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = Register.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


# Endpoint to update a user by ID (protected, admin only)
@app.route('/register/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({"msg": "Admins only!"}), 403
    data = request.get_json()
    user = Register.query.get_or_404(user_id)

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    if 'password' in data:
        user.set_password(data['password'])
    user.address = data.get('address', user.address)
    user.role = data.get('role', user.role)

    db.session.commit()
    return jsonify(user.to_dict()), 200


# Endpoint to delete a user by ID (protected, admin only)
@app.route('/register/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({"msg": "Admins only!"}), 403
    user = Register.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted"}), 200


@app.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    current_user = get_jwt_identity()
    if not is_admin(current_user):  # Pass current_user to is_admin() for role check
        return jsonify({"msg": "Admins only!"}), 403
    
    data = request.form
    book_name = data['book_name']
    author = data['author']
    date_of_publish = datetime.strptime(data['date_of_publish'], '%Y-%m-%d').date()
    summary = data.get('summary')
    image = request.files['image'] if 'image' in request.files else None
    series = True if data.get('series') == 'on' else False  # Checkbox value

    image_filename = None
    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    new_book = Book(
        book_name=book_name,
        author=author,
        date_of_publish=date_of_publish,
        summary=summary,
        image=image_filename,
        series=series
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify(new_book.to_dict()), 201

# Endpoint to get details of a specific book by ID (public)
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify(book.to_dict()), 200

@app.route('/books/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    current_user = get_jwt_identity()
    if not is_admin(current_user):  # Assuming is_admin is a function to check admin role
        return jsonify({"msg": "Admins only!"}), 403
    
    book = Book.query.get_or_404(id)

    # Update book attributes based on FormData sent from front-end
    book.book_name = request.form.get('book_name', book.book_name)
    book.author = request.form.get('author', book.author)
    book.date_of_publish = datetime.strptime(request.form.get('date_of_publish', book.date_of_publish.isoformat()), '%Y-%m-%d').date()
    book.summary = request.form.get('summary', book.summary)
    # Assuming 'image' and 'series' are also sent as form data fields
    book.image = request.files.get('image') if request.files.get('image') else book.image
    book.series = True if request.form.get('series') == 'true' else False if request.form.get('series') == 'false' else book.series

    db.session.commit()
    return jsonify(book.to_dict()), 200

# Endpoint to delete a book by ID (admin only)
@app.route('/books/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({"msg": "Admins only!"}), 403
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return '', 204


# Endpoint to get details of all books (public)
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200


# Endpoint to create a new loan (admin only)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/<path:path>', methods=['OPTIONS'])
@app.route('/', methods=['OPTIONS'])
def handle_options(path=None):
    response = app.make_response('')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response


@app.route('/loans', methods=['POST'])
@jwt_required()
def create_loan():
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({"msg": "Admins only!"}), 403

    data = request.get_json()
    book_id = data['book_id']
    client_id = data['register_id']  # Assuming `register_id` is the ID from the Register table
    admin_id = current_user['id']  # Correctly retrieving admin's ID from JWT token
    return_date = datetime.strptime(data['return_date'], '%Y-%m-%d').date()

    new_loan = Loan(book_id=book_id, client_id=client_id, admin_id=admin_id, return_date=return_date)
    db.session.add(new_loan)
    db.session.commit()
    
    
    return jsonify(new_loan.to_dict()), 201

# Endpoint to get details of all loans (protected)
@app.route('/loans', methods=['GET'])
@jwt_required()
def get_loans():
    loans = Loan.query.all()
    return jsonify([loan.to_dict() for loan in loans]), 200


# Endpoint to delete a loan by ID (admin only)
@app.route('/loans/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_loan(id):
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({"msg": "Admins only!"}), 403
    loan = Loan.query.get_or_404(id)
    db.session.delete(loan)
    db.session.commit()
    return '', 204

# Endpoint to get details of a specific loan by ID (protected)
@app.route('/loans/<int:id>', methods=['GET'])
@jwt_required()
def get_loan(id):
    loan = Loan.query.get_or_404(id)
    return jsonify(loan.to_dict()), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)