# Rural Kiosk Application

A full-stack web application designed for rural kiosks to sell essential goods like grains, pulses, vegetables, and fruits.

## Features

- **Product Browsing**: Browse products by categories (Grains, Pulses, Vegetables, Fruits, Dairy)
- **Search**: Search products by name and description 
- **Shopping Cart**: Add products to cart with quantity management
- **Checkout Process**: Smooth checkout with delivery information and payment options
- **Stock Management**: Real-time stock tracking and low stock indicators
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works on all device sizes (desktop, tablet, mobile)

## Tech Stack

### Backend (Flask)
- Python 3.8+
- Flask
- SQLAlchemy
- Flask-Migrate
- SQLite Database

### Frontend (React)
- React 18
- React Router v6
- Context API for state management
- CSS3 with modern features
- Responsive design principles

## Project Structure

```
├── app.py                 # Main Flask application file
├── add_products.py        # Script to populate the database
├── database.db            # SQLite database
├── migrations/            # Database migrations
├── kiosk-frontend/        # React frontend
│   ├── public/            # Static files
│   │   ├── components/    # React components
│   │   ├── context/       # React contexts
│   │   ├── styles/        # CSS files
│   │   ├── App.js         # Main App component
│   │   └── index.js       # Entry point
│   ├── package.json       # Frontend dependencies
│   └── README.md          # Frontend documentation
└── README.md              # Project documentation
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup
1. Clone the repository:
   ```
   git clone <repository-url>
   cd kiosk-backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install flask flask-sqlalchemy flask-cors flask-migrate
   ```

4. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Add sample products:
   ```
   python add_products.py
   ```

6. Run the backend server:
   ```
   python app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd kiosk-frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. The application will be available at http://localhost:3000

## Usage

1. Browse products by navigating to the main page
2. Use the category buttons to filter products by category
3. Use the search bar to find specific products
4. Click on a product to view details
5. Add products to your cart
6. View cart and adjust quantities
7. Proceed to checkout and enter delivery information
8. Select payment method and place order

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 