from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
import json
from datetime import datetime, timedelta
import logging
import pandas as pd
import io
import jwt
from functools import wraps
from models import db, Product, Order

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "https://*", "http://*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}, supports_credentials=True)

# Database Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}")
# If DATABASE_URL starts with postgres://, replace it with postgresql:// (SQLAlchemy requirement)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your-jwt-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# Initialize Database
db.init_app(app)
migrate = Migrate(app, db)

# Admin credentials (in a real app, this would be stored securely in a database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # In a real app, this would be hashed

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

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

# New endpoint to save order details
@app.route("/api/order-details", methods=["POST"])
def save_order_details():
    try:
        data = request.json
        logger.debug(f"Received order details: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        transaction_id = data.get("transactionId", "UNKNOWN")
        
        # Check if order with this transaction ID already exists
        existing_order = Order.query.filter_by(transaction_id=transaction_id).first()
        
        if existing_order:
            logger.debug(f"Order with transaction ID {transaction_id} already exists, returning success")
            return jsonify({
                "message": "Order already exists",
                "order_id": existing_order.id
            }), 200
        
        # Create a new order with the provided details
        new_order = Order(
            transaction_id=transaction_id,
            items=json.dumps(data.get("items", [])),
            total_price=data.get("totalPrice", 0),
            payment_method=data.get("paymentMethod", "Unknown"),
            street=data.get("address", {}).get("street", ""),
            city=data.get("address", {}).get("city", ""),
            state=data.get("address", {}).get("state", ""),
            zip_code=data.get("address", {}).get("zipCode", ""),
            expected_delivery=datetime.fromisoformat(data.get("expectedDelivery", datetime.now().isoformat())),
            customer_name=data.get("customerName", ""),
            customer_email=data.get("customerEmail", ""),
            customer_phone=data.get("customerPhone", ""),
            notes=data.get("notes", "")
        )
        
        db.session.add(new_order)
        db.session.commit()
    
        logger.debug(f"Order saved successfully with ID: {new_order.id}")
        return jsonify({
            "message": "Order details saved successfully",
            "order_id": new_order.id
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving order details: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint to export orders to Excel
@app.route("/api/export-orders", methods=["GET"])
def export_orders():
    try:
        # Get all orders
        orders = Order.query.all()
        
        if not orders:
            # If no orders in database, return test orders
            logger.debug("No orders found, returning test orders for export")
            test_orders = [
                {
                    "id": 1,
                    "transaction_id": "TEST-1234",
                    "items": [
                        {"name": "Apple", "quantity": 2, "price": 2.99},
                        {"name": "Banana", "quantity": 3, "price": 1.99}
                    ],
                    "total_price": 11.95,
                    "payment_method": "Cash on Delivery",
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "Test State",
                    "zip_code": "12345",
                    "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "expected_delivery": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    "customer_name": "Test Customer",
                    "customer_phone": "555-1234",
                    "customer_email": "test@example.com",
                    "status": "pending",
                    "notes": "Test order for debugging"
                },
                {
                    "id": 2,
                    "transaction_id": "TEST-5678",
                    "items": [
                        {"name": "Carrot", "quantity": 1, "price": 1.49},
                        {"name": "Water", "quantity": 2, "price": 0.99}
                    ],
                    "total_price": 3.47,
                    "payment_method": "Credit Card",
                    "street": "456 Test Ave",
                    "city": "Test City",
                    "state": "Test State",
                    "zip_code": "12345",
                    "order_time": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    "expected_delivery": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "customer_name": "Another Customer",
                    "customer_phone": "555-5678",
                    "customer_email": "another@example.com",
                    "status": "delivered",
                    "notes": "Another test order"
                }
            ]
            
            # Prepare data for Excel from test orders
            data = []
            for order in test_orders:
                items_str = ", ".join([f"{item['name']} (x{item['quantity']})" for item in order["items"]])
                
                data.append({
                    "Order ID": order["id"],
                    "Transaction ID": order["transaction_id"],
                    "Order Time": order["order_time"],
                    "Expected Delivery": order["expected_delivery"],
                    "Items": items_str,
                    "Total Price": order["total_price"],
                    "Payment Method": order["payment_method"],
                    "Street": order["street"],
                    "City": order["city"],
                    "State": order["state"],
                    "Zip Code": order["zip_code"],
                    "Customer Name": order["customer_name"],
                    "Customer Email": order["customer_email"],
                    "Customer Phone": order["customer_phone"],
                    "Status": order["status"],
                    "Notes": order["notes"]
                })
        else:
            # Prepare data for Excel from real orders
            data = []
            for order in orders:
                try:
                    items = json.loads(order.items) if isinstance(order.items, str) else order.items
                    items_str = ", ".join([f"{item['name']} (x{item['quantity']})" for item in items])
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error processing items for order {order.id}: {str(e)}")
                    items_str = "Error parsing items"
                
                data.append({
                    "Order ID": order.id,
                    "Transaction ID": order.transaction_id,
                    "Order Time": order.order_time.strftime("%Y-%m-%d %H:%M:%S") if order.order_time else "N/A",
                    "Expected Delivery": order.expected_delivery.strftime("%Y-%m-%d %H:%M:%S") if order.expected_delivery else "N/A",
                    "Items": items_str,
                    "Total Price": order.total_price,
                    "Payment Method": order.payment_method,
                    "Street": order.street,
                    "City": order.city,
                    "State": order.state,
                    "Zip Code": order.zip_code,
                    "Customer Name": order.customer_name,
                    "Customer Email": order.customer_email,
                    "Customer Phone": order.customer_phone,
                    "Status": order.status,
                    "Notes": order.notes
                })
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        
        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Orders', index=False)
            
        # Seek to the beginning of the stream
        output.seek(0)
        
        # Return the Excel file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'grocer_go_orders_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        logger.error(f"Error exporting orders: {str(e)}")
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

@app.route("/api/orders", methods=["GET"])
@token_required
def get_orders(current_user):
    try:
        logger.debug("Fetching orders...")
        orders = Order.query.order_by(Order.order_time.desc()).all()
        logger.debug(f"Found {len(orders)} orders")
        
        if not orders:
            logger.info("No orders found in database")
            return jsonify([])  # Return empty array instead of 404
            
        order_list = []
        for order in orders:
            try:
                items = json.loads(order.items) if isinstance(order.items, str) else order.items
                logger.debug(f"Order {order.id} items: {items}")
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding items for order {order.id}: {str(e)}")
                items = []
            
            order_data = {
                "id": order.id,
                "transaction_id": order.transaction_id,
                "items": items,
                "total_price": order.total_price,
                "payment_method": order.payment_method,
                "street": order.street,
                "city": order.city,
                "state": order.state,
                "zip_code": order.zip_code,
                "order_time": order.order_time.isoformat() if order.order_time else None,
                "expected_delivery": order.expected_delivery.isoformat() if order.expected_delivery else None,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone,
                "status": order.status,
                "notes": order.notes
            }
            order_list.append(order_data)
            logger.debug(f"Processed order {order.id}")
            
        logger.debug(f"Returning {len(order_list)} orders")
        return jsonify(order_list)
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
@token_required
def update_order_status(current_user, order_id):
    try:
        data = request.json
        if not data or "status" not in data:
            return jsonify({"error": "No status provided"}), 400
            
        status = data["status"]
        if status not in ["pending", "processing", "shipped", "delivered", "cancelled"]:
            return jsonify({"error": "Invalid status"}), 400
            
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
            
        order.status = status
        db.session.commit()
        
        return jsonify({"message": "Order status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating order status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    try:
        data = request.json
        if not data or "username" not in data or "password" not in data:
            return jsonify({"message": "Missing username or password"}), 400
            
        # Check credentials
        if data["username"] != ADMIN_USERNAME or data["password"] != ADMIN_PASSWORD:
            return jsonify({"message": "Invalid credentials"}), 401
            
        # Generate token
        token = jwt.encode({
            "username": data["username"],
            "exp": datetime.utcnow() + app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        }, app.config["JWT_SECRET_KEY"], algorithm="HS256")
        
        # Convert token to string if it's bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        logger.debug(f"Admin login successful, token: {token[:10]}...")
        return jsonify({"token": token}), 200
    except Exception as e:
        logger.error(f"Error during admin login: {str(e)}")
        return jsonify({"message": "Login failed"}), 500

@app.route("/api/test-products", methods=["GET"])
def get_test_products():
    """Test endpoint that always returns sample products"""
    test_products = [
        {
            "id": 1,
            "name": "Apple",
            "price": 2.99,
            "category": "fruits",
            "image": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
            "description": "Fresh red apples",
            "stock": 100
        },
        {
            "id": 2,
            "name": "Banana",
            "price": 1.99,
            "category": "fruits",
            "image": "https://images.unsplash.com/photo-1566393028639-d108a42c46a7?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
            "description": "Yellow bananas",
            "stock": 150
        },
        {
            "id": 3,
            "name": "Carrot",
            "price": 1.49,
            "category": "vegetables",
            "image": "https://images.unsplash.com/photo-1598170845058-32b9d6a5d167?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
            "description": "Fresh carrots",
            "stock": 80
        },
        {
            "id": 4,
            "name": "Water",
            "price": 0.99,
            "category": "beverages",
            "image": "https://images.unsplash.com/photo-1523362628745-0c100150b504?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
            "description": "Bottled water",
            "stock": 200
        }
    ]
    logger.debug(f"Returning {len(test_products)} test products")
    return jsonify(test_products)

@app.route("/api/admin/test-token", methods=["GET"])
def test_admin_token():
    """Test endpoint that returns a valid admin token for debugging"""
    token = jwt.encode({
        "username": ADMIN_USERNAME,
        "exp": datetime.utcnow() + app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    }, app.config["JWT_SECRET_KEY"], algorithm="HS256")
    
    # Convert token to string if it's bytes
    if isinstance(token, bytes):
        token = token.decode('utf-8')
        
    return jsonify({
        "token": token,
        "username": ADMIN_USERNAME,
        "expires": (datetime.utcnow() + app.config["JWT_ACCESS_TOKEN_EXPIRES"]).isoformat()
    })

@app.route("/api/test-orders", methods=["GET"])
def get_test_orders():
    """Test endpoint that returns sample orders for debugging"""
    test_orders = [
        {
            "id": 1,
            "transaction_id": "TEST-1234",
            "items": [
                {"id": 1, "name": "Apple", "quantity": 2, "price": 2.99},
                {"id": 2, "name": "Banana", "quantity": 3, "price": 1.99}
            ],
            "total_price": 11.95,
            "payment_method": "Cash on Delivery",
            "street": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "zip_code": "12345",
            "order_time": datetime.now().isoformat(),
            "expected_delivery": (datetime.now() + timedelta(days=1)).isoformat(),
            "customer_name": "Test Customer",
            "customer_phone": "555-1234",
            "customer_email": "test@example.com",
            "status": "pending",
            "notes": "Test order for debugging"
        },
        {
            "id": 2,
            "transaction_id": "TEST-5678",
            "items": [
                {"id": 3, "name": "Carrot", "quantity": 1, "price": 1.49},
                {"id": 4, "name": "Water", "quantity": 2, "price": 0.99}
            ],
            "total_price": 3.47,
            "payment_method": "Credit Card",
            "street": "456 Test Ave",
            "city": "Test City",
            "state": "Test State",
            "zip_code": "12345",
            "order_time": (datetime.now() - timedelta(days=1)).isoformat(),
            "expected_delivery": datetime.now().isoformat(),
            "customer_name": "Another Customer",
            "customer_phone": "555-5678",
            "customer_email": "another@example.com",
            "status": "delivered",
            "notes": "Another test order"
        }
    ]
    
    logger.debug(f"Returning {len(test_orders)} test orders")
    return jsonify(test_orders)

@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'message': 'Order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting order: {str(e)}")
        return jsonify({'error': 'Failed to delete order'}), 500

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
