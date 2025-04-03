from flask import Flask, jsonify
from models import db, Product

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ✅ Added to prevent warnings

    db.init_app(app)

    # ✅ Ensure database tables exist
    with app.app_context():
        db.create_all()

    return app

app = create_app()  # ✅ Use app factory pattern

@app.route('/products', methods=['GET'])
def get_products():
    with app.app_context():  # ✅ Ensuring context exists before querying
        products = Product.query.all()
        product_list = [{
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "image": product.image
        } for product in products]
    
    return jsonify(product_list)

if __name__ == '__main__':
    app.run(debug=True)
