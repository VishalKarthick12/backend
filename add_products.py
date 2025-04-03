from app import app, db, Product
import json

# Sample products data with categories, descriptions and stock
products = [
    # Grains
    {
        "name": "Rice",
        "price": 50.00,
        "category": "Grains",
        "image": "/images/rice.jpg",
        "description": "High-quality premium rice grown locally",
        "stock": 50
    },
    {
        "name": "Wheat",
        "price": 45.00,
        "category": "Grains",
        "image": "/images/wheat.jpg",
        "description": "Organic whole wheat for healthy meals",
        "stock": 40
    },
    {
        "name": "Barley",
        "price": 40.00,
        "category": "Grains",
        "image": "/images/barley.jpg",
        "description": "Nutritious barley for soups and stews",
        "stock": 30
    },
    {
        "name": "Oats",
        "price": 60.00,
        "category": "Grains",
        "image": "/images/oats.jpg",
        "description": "Rolled oats for a healthy breakfast",
        "stock": 45
    },
    {
        "name": "Corn",
        "price": 35.00,
        "category": "Grains",
        "image": "/images/corn.jpg",
        "description": "Fresh sweet corn kernels",
        "stock": 55
    },
    {
        "name": "Millet",
        "price": 55.00,
        "category": "Grains",
        "image": "/images/millet.jpg",
        "description": "Nutritious millet for a healthy diet",
        "stock": 25
    },
    
    # Pulses
    {
        "name": "Moong Dal",
        "price": 65.00,
        "category": "Pulses",
        "image": "/images/moong.jpg",
        "description": "Protein-rich moong dal for everyday meals",
        "stock": 35
    },
    {
        "name": "Chana Dal",
        "price": 60.00,
        "category": "Pulses",
        "image": "/images/chana.jpg",
        "description": "Premium quality chana dal for delicious recipes",
        "stock": 30
    },
    {
        "name": "Toor Dal",
        "price": 70.00,
        "category": "Pulses",
        "image": "/images/toor.jpg",
        "description": "Split pigeon peas for traditional dishes",
        "stock": 40
    },
    {
        "name": "Urad Dal",
        "price": 75.00,
        "category": "Pulses",
        "image": "/images/urad.jpg",
        "description": "Black gram dal for south Indian dishes",
        "stock": 25
    },
    {
        "name": "Rajma",
        "price": 80.00,
        "category": "Pulses",
        "image": "/images/rajma.jpg",
        "description": "Kidney beans for rajma curry",
        "stock": 30
    },
    {
        "name": "Chickpeas",
        "price": 55.00,
        "category": "Pulses",
        "image": "/images/chickpeas.jpg",
        "description": "Whole chickpeas for curries and salads",
        "stock": 45
    },
    
    # Vegetables
    {
        "name": "Potatoes",
        "price": 30.00,
        "category": "Vegetables",
        "image": "/images/potatoes.jpg",
        "description": "Fresh farm potatoes harvested daily",
        "stock": 60
    },
    {
        "name": "Tomatoes",
        "price": 40.00,
        "category": "Vegetables",
        "image": "/images/tomatoes.jpg",
        "description": "Juicy red tomatoes from organic farms",
        "stock": 45
    },
    {
        "name": "Onions",
        "price": 35.00,
        "category": "Vegetables",
        "image": "/images/onions.jpg",
        "description": "Fresh red onions for daily cooking",
        "stock": 70
    },
    {
        "name": "Carrots",
        "price": 45.00,
        "category": "Vegetables",
        "image": "/images/carrots.jpg",
        "description": "Crunchy carrots rich in vitamins",
        "stock": 50
    },
    {
        "name": "Cauliflower",
        "price": 35.00,
        "category": "Vegetables",
        "image": "/images/cauliflower.jpg",
        "description": "Farm-fresh cauliflower",
        "stock": 30
    },
    {
        "name": "Spinach",
        "price": 25.00,
        "category": "Vegetables",
        "image": "/images/spinach.jpg",
        "description": "Leafy green spinach packed with nutrients",
        "stock": 40
    },
    {
        "name": "Okra",
        "price": 40.00,
        "category": "Vegetables",
        "image": "/images/okra.jpg",
        "description": "Fresh lady fingers for traditional dishes",
        "stock": 35
    },
    {
        "name": "Eggplant",
        "price": 30.00,
        "category": "Vegetables",
        "image": "/images/eggplant.jpg",
        "description": "Purple eggplants for various recipes",
        "stock": 25
    },
    
    # Fruits
    {
        "name": "Apples",
        "price": 120.00,
        "category": "Fruits",
        "image": "/images/apples.jpg",
        "description": "Crisp and sweet apples from the mountains",
        "stock": 25
    },
    {
        "name": "Bananas",
        "price": 60.00,
        "category": "Fruits",
        "image": "/images/bananas.jpg",
        "description": "Ripe yellow bananas, perfect for snacking",
        "stock": 40
    },
    {
        "name": "Oranges",
        "price": 80.00,
        "category": "Fruits",
        "image": "/images/oranges.jpg",
        "description": "Juicy oranges rich in vitamin C",
        "stock": 30
    },
    {
        "name": "Mangoes",
        "price": 150.00,
        "category": "Fruits",
        "image": "/images/mangoes.jpg",
        "description": "Sweet alphonso mangoes, the king of fruits",
        "stock": 20
    },
    {
        "name": "Grapes",
        "price": 90.00,
        "category": "Fruits",
        "image": "/images/grapes.jpg",
        "description": "Sweet seedless grapes in bunches",
        "stock": 35
    },
    {
        "name": "Watermelon",
        "price": 70.00,
        "category": "Fruits",
        "image": "/images/watermelon.jpg",
        "description": "Refreshing watermelon for hot summer days",
        "stock": 15
    },
    {
        "name": "Pineapple",
        "price": 100.00,
        "category": "Fruits",
        "image": "/images/pineapple.jpg",
        "description": "Sweet and tangy pineapple",
        "stock": 20
    },
    {
        "name": "Pomegranate",
        "price": 130.00,
        "category": "Fruits",
        "image": "/images/pomegranate.jpg",
        "description": "Ruby red pomegranate, full of antioxidants",
        "stock": 25
    },
    
    # Dairy
    {
        "name": "Milk",
        "price": 55.00,
        "category": "Dairy",
        "image": "/images/milk.jpg",
        "description": "Fresh cow's milk, pasteurized and healthy",
        "stock": 30
    },
    {
        "name": "Yogurt",
        "price": 40.00,
        "category": "Dairy",
        "image": "/images/yogurt.jpg",
        "description": "Creamy yogurt made from fresh milk",
        "stock": 20
    },
    {
        "name": "Cheese",
        "price": 120.00,
        "category": "Dairy",
        "image": "/images/cheese.jpg",
        "description": "Sliced cheese for sandwiches and snacks",
        "stock": 15
    },
    {
        "name": "Butter",
        "price": 60.00,
        "category": "Dairy",
        "image": "/images/butter.jpg",
        "description": "Creamy butter for cooking and spreading",
        "stock": 25
    },
    {
        "name": "Paneer",
        "price": 80.00,
        "category": "Dairy",
        "image": "/images/paneer.jpg",
        "description": "Fresh cottage cheese for Indian dishes",
        "stock": 20
    },
    {
        "name": "Ghee",
        "price": 250.00,
        "category": "Dairy",
        "image": "/images/ghee.jpg",
        "description": "Pure clarified butter for traditional cooking",
        "stock": 15
    }
]

# Add products to database
with app.app_context():
    # Clear existing products
    Product.query.delete()
    
    # Add new products
    for product_data in products:
        product = Product(
            name=product_data["name"],
            price=product_data["price"],
            category=product_data["category"],
            image=product_data["image"],
            description=product_data["description"],
            stock=product_data["stock"]
        )
        db.session.add(product)
    
    # Commit changes
    db.session.commit()

    print(f"Added {len(products)} products to the database.")
