from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/home_improvement'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer)

    def __repr__(self):
        return f'<Product {self.name}>'

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    db.session.rollback()
    return jsonify({"error": "Database error occurred"}), 500

@app.errorhandler(NotFound)
def handle_not_found_error(error):
    return jsonify({"error": str(error.description)}), 404

@app.errorhandler(BadRequest)
def handle_bad_request_error(error):
    return jsonify({"error": str(error.description)}), 400

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        result = [{'id': p.id, 'name': p.name, 'category': p.category, 'price': str(p.price), 'stock': p.stock} for p in products]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    try:
        # Fetch the product based on id
        product = Product.query.get(id)
        
        # Manually raise NotFound exception if product is not found
        if not product:
            raise NotFound(f"Product with id {id} not found")
        
        # Return product details in JSON format
        return jsonify({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "stock": product.stock
        }), 200
    
    except NotFound as nf:
        # Handle the NotFound error raised when product is not found
        return jsonify({"error": str(nf)}), 404
    
    except SQLAlchemyError as e:
        # Handle any database-related errors
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

@app.route('/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        new_product = Product(
            name=data['name'],
            category=data.get('category'),
            price=data['price'],
            stock=data['stock']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product added"}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        data = request.get_json()
        product = Product.query.get_or_404(id)
        product.name = data.get('name', product.name)
        product.category = data.get('category', product.category)
        product.price = data.get('price', product.price)
        product.stock = data.get('stock', product.stock)
        db.session.commit()
        return jsonify({"message": "Product updated"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            raise NotFound(f"Product with id {id} not found")
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted"}), 200

    except NotFound as nf:
        # Handle the NotFound error raised when product is not found
        return jsonify({"error": str(nf)}), 404

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
