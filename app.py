from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Database Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key")

# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Test route for debugging
@app.route("/test", methods=["GET"])
def test_route():
    return jsonify({"message": "API is working!"}), 200

# Routes
@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        logger.debug("Received request for products")
        
        # Check if database exists
        db_exists = os.path.exists(os.path.join(BASE_DIR, 'database.db'))
        logger.debug(f"Database exists: {db_exists}")
        
        if not db_exists:
            logger.error("Database file not found")
            return jsonify({"error": "Database not initialized"}), 500
            
        # Get products
        category = request.args.get("category")
        logger.debug(f"Category filter: {category}")
        
        query = Product.query
        if category and category.lower() != 'all':
            query = query.filter(Product.category.ilike(category))
            
        products = query.all()
        logger.debug(f"Found {len(products)} products")
        
        if not products:
            logger.warning("No products found in database")
            return jsonify({"message": "No products available"}), 404

        product_list = [{
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category.lower(),  # Convert to lowercase for consistency
            "image": product.image,
            "description": product.description,
            "stock": product.stock
        } for product in products]
        
        logger.debug(f"Returning {len(product_list)} products")
        return jsonify(product_list)
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "image": product.image,
            "description": product.description,
            "stock": product.stock
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/checkout", methods=["POST"])
def checkout():
    try:
        data = request.json

        if not data or "cart" not in data or "total_price" not in data:
            return jsonify({"error": "Invalid request"}), 400

        # Validate cart items
        cart = data["cart"]
        for item in cart:
            product = Product.query.get(item["id"])
            if not product or product.stock < item["quantity"]:
                return jsonify({"error": f"Insufficient stock for {item['name']}"}), 400

        # Create order
        new_order = Order(
            items=json.dumps(cart),
            total_price=data["total_price"]
        )
        
        # Update stock
        for item in cart:
            product = Product.query.get(item["id"])
            product.stock -= item["quantity"]
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "message": "Order placed successfully!",
            "order_id": new_order.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/products", methods=["GET"])
def get_products_old():
    """Legacy endpoint for compatibility"""
    logger.debug("Received request on legacy /products endpoint")
    return get_products()

@app.route("/checkout", methods=["POST"])
def checkout_old():
    """Legacy endpoint for compatibility"""
    return checkout()

# Run App
if __name__ == "__main__":
    with app.app_context():
        logger.debug("Creating database tables...")
        db.create_all()
        # Check if products exist
        product_count = Product.query.count()
        logger.debug(f"Current product count: {product_count}")
        if product_count == 0:
            logger.warning("No products found in database. Please run add_products.py")
    app.run(debug=True, port=5000)
