import requests
import os
import time

# Create images directory if it doesn't exist
images_dir = 'kiosk-frontend/public/images'
os.makedirs(images_dir, exist_ok=True)

# List of all required images from add_products.py
image_names = [
    'rice.jpg', 'wheat.jpg', 'barley.jpg', 'oats.jpg', 'corn.jpg', 'millet.jpg',
    'moong.jpg', 'chana.jpg', 'toor.jpg', 'urad.jpg', 'rajma.jpg', 'chickpeas.jpg',
    'potatoes.jpg', 'tomatoes.jpg', 'onions.jpg', 'carrots.jpg', 'cauliflower.jpg', 
    'spinach.jpg', 'okra.jpg', 'eggplant.jpg', 'apples.jpg', 'bananas.jpg',
    'oranges.jpg', 'mangoes.jpg', 'grapes.jpg', 'watermelon.jpg', 'pineapple.jpg',
    'pomegranate.jpg', 'milk.jpg', 'yogurt.jpg', 'cheese.jpg', 'butter.jpg',
    'paneer.jpg', 'ghee.jpg'
]

# Create default placeholder image first
default_placeholder_path = os.path.join(images_dir, 'placeholder-image.jpg')
if not os.path.exists(default_placeholder_path):
    try:
        print("Downloading default placeholder image...")
        response = requests.get("https://placehold.co/300x300?text=Product")
        response.raise_for_status()
        
        with open(default_placeholder_path, 'wb') as f:
            f.write(response.content)
            
        print("Default placeholder image created successfully!")
    except Exception as e:
        print(f"Error creating default placeholder: {e}")

# Download placeholder images
for image_name in image_names:
    # Extract product name without extension
    product_name = image_name.split('.')[0].capitalize()
    
    # Create file path
    file_path = os.path.join(images_dir, image_name)
    
    # Skip if file already exists
    if os.path.exists(file_path):
        print(f"Skipping existing image: {image_name}")
        continue
    
    # Use placeholder image service
    url = f"https://placehold.co/300x300?text={product_name}"
    
    try:
        # Download image
        print(f"Downloading: {image_name}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Save image to file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {image_name}")
        
        # Sleep a bit to avoid hitting rate limits
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error downloading {image_name}: {e}")

print("\nAll placeholder images have been downloaded!")
print(f"Images saved to: {os.path.abspath(images_dir)}") 