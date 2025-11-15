import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Few-shot template examples for different website categories
TEMPLATE_EXAMPLES = {
    "ecommerce": """
<!-- E-COMMERCE EXAMPLE TEMPLATE -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Online Store</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-800">StoreName</h1>
                <div class="flex gap-6 items-center">
                    <a href="#" class="text-gray-600 hover:text-gray-900">Shop</a>
                    <a href="#" class="text-gray-600 hover:text-gray-900">About</a>
                    <button id="cart-btn" class="relative">
                        🛒 <span id="cart-count" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center">0</span>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-20">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <h2 class="text-5xl font-bold mb-4">Welcome to Our Store</h2>
            <p class="text-xl mb-8">Discover amazing products at great prices</p>
            <button class="bg-white text-purple-600 px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition">Shop Now</button>
        </div>
    </section>

    <!-- Products Grid -->
    <section class="max-w-7xl mx-auto px-4 py-16">
        <h3 class="text-3xl font-bold mb-8">Featured Products</h3>
        <div id="products-grid" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <!-- Products loaded dynamically -->
        </div>
    </section>

    <!-- Cart Modal -->
    <div id="cart-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-2xl font-bold">Shopping Cart</h3>
                <button id="close-cart" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
            </div>
            <div id="cart-items"></div>
            <div class="border-t pt-4 mt-4">
                <div class="flex justify-between text-xl font-bold mb-4">
                    <span>Total:</span>
                    <span id="cart-total">$0.00</span>
                </div>
                <button class="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition">Checkout</button>
            </div>
        </div>
    </div>

    <script>
        // Sample products data
        const products = [
            {id: 1, name: "Product 1", price: 29.99, image: "https://via.placeholder.com/300"},
            {id: 2, name: "Product 2", price: 49.99, image: "https://via.placeholder.com/300"},
            {id: 3, name: "Product 3", price: 19.99, image: "https://via.placeholder.com/300"},
            {id: 4, name: "Product 4", price: 39.99, image: "https://via.placeholder.com/300"}
        ];

        // Cart functionality (using in-memory storage instead of localStorage)
        let cart = [];

        function updateCartCount() {
            document.getElementById('cart-count').textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
        }

        function renderProducts() {
            const grid = document.getElementById('products-grid');
            grid.innerHTML = products.map(product => `
                <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition">
                    <img src="${product.image}" alt="${product.name}" class="w-full h-48 object-cover">
                    <div class="p-4">
                        <h4 class="font-bold text-lg mb-2">${product.name}</h4>
                        <p class="text-gray-600 mb-4">$${product.price.toFixed(2)}</p>
                        <button onclick="addToCart(${product.id})" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition">
                            Add to Cart
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            const existingItem = cart.find(item => item.id === productId);
            
            if (existingItem) {
                existingItem.quantity++;
            } else {
                cart.push({...product, quantity: 1});
            }
            
            updateCartCount();
        }

        function renderCart() {
            const cartItems = document.getElementById('cart-items');
            const cartTotal = document.getElementById('cart-total');
            
            if (cart.length === 0) {
                cartItems.innerHTML = '<p class="text-gray-500 text-center py-8">Your cart is empty</p>';
                cartTotal.textContent = '$0.00';
                return;
            }
            
            cartItems.innerHTML = cart.map(item => `
                <div class="flex justify-between items-center mb-4 pb-4 border-b">
                    <div class="flex items-center gap-4">
                        <img src="${item.image}" alt="${item.name}" class="w-16 h-16 object-cover rounded">
                        <div>
                            <h4 class="font-bold">${item.name}</h4>
                            <p class="text-gray-600">$${item.price.toFixed(2)}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <button onclick="updateQuantity(${item.id}, -1)" class="bg-gray-200 w-8 h-8 rounded">-</button>
                        <span class="w-8 text-center">${item.quantity}</span>
                        <button onclick="updateQuantity(${item.id}, 1)" class="bg-gray-200 w-8 h-8 rounded">+</button>
                        <button onclick="removeFromCart(${item.id})" class="text-red-500 ml-4">🗑️</button>
                    </div>
                </div>
            `).join('');
            
            const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            cartTotal.textContent = `$${total.toFixed(2)}`;
        }

        function updateQuantity(productId, change) {
            const item = cart.find(i => i.id === productId);
            if (item) {
                item.quantity += change;
                if (item.quantity <= 0) {
                    removeFromCart(productId);
                } else {
                    updateCartCount();
                    renderCart();
                }
            }
        }

        function removeFromCart(productId) {
            cart = cart.filter(item => item.id !== productId);
            updateCartCount();
            renderCart();
        }

        // Modal controls
        document.getElementById('cart-btn').addEventListener('click', () => {
            document.getElementById('cart-modal').classList.remove('hidden');
            renderCart();
        });

        document.getElementById('close-cart').addEventListener('click', () => {
            document.getElementById('cart-modal').classList.add('hidden');
        });

        // Initialize
        renderProducts();
        updateCartCount();
    </script>
</body>
</html>
""",

    "landing": """
<!-- LANDING PAGE EXAMPLE TEMPLATE -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white">
    <!-- Navigation -->
    <nav class="fixed w-full bg-white shadow-sm z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold text-blue-600">BrandName</h1>
            <div class="hidden md:flex gap-6">
                <a href="#features" class="text-gray-600 hover:text-blue-600">Features</a>
                <a href="#pricing" class="text-gray-600 hover:text-blue-600">Pricing</a>
                <a href="#contact" class="text-gray-600 hover:text-blue-600">Contact</a>
            </div>
            <button class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">Get Started</button>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="pt-32 pb-20 px-4">
        <div class="max-w-7xl mx-auto text-center">
            <h2 class="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Build Amazing Things
            </h2>
            <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                The perfect solution for your business. Fast, reliable, and easy to use.
            </p>
            <div class="flex gap-4 justify-center">
                <button class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold">
                    Start Free Trial
                </button>
                <button class="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg hover:bg-blue-50 text-lg font-semibold">
                    Watch Demo
                </button>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 bg-gray-50 px-4">
        <div class="max-w-7xl mx-auto">
            <h3 class="text-4xl font-bold text-center mb-16">Amazing Features</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="bg-white p-8 rounded-xl shadow-md hover:shadow-xl transition">
                    <div class="text-4xl mb-4">⚡</div>
                    <h4 class="text-xl font-bold mb-3">Lightning Fast</h4>
                    <p class="text-gray-600">Experience blazing fast performance that keeps your users engaged.</p>
                </div>
                <div class="bg-white p-8 rounded-xl shadow-md hover:shadow-xl transition">
                    <div class="text-4xl mb-4">🔒</div>
                    <h4 class="text-xl font-bold mb-3">Secure</h4>
                    <p class="text-gray-600">Enterprise-grade security to keep your data safe and protected.</p>
                </div>
                <div class="bg-white p-8 rounded-xl shadow-md hover:shadow-xl transition">
                    <div class="text-4xl mb-4">📱</div>
                    <h4 class="text-xl font-bold mb-3">Responsive</h4>
                    <p class="text-gray-600">Works perfectly on all devices, from mobile to desktop.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section id="pricing" class="py-20 px-4">
        <div class="max-w-7xl mx-auto">
            <h3 class="text-4xl font-bold text-center mb-16">Simple Pricing</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="border-2 rounded-xl p-8 hover:border-blue-600 transition">
                    <h4 class="text-2xl font-bold mb-4">Starter</h4>
                    <p class="text-4xl font-bold mb-6">$9<span class="text-lg text-gray-600">/mo</span></p>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Feature 1</li>
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Feature 2</li>
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Feature 3</li>
                    </ul>
                    <button class="w-full border-2 border-blue-600 text-blue-600 py-3 rounded-lg hover:bg-blue-50">
                        Choose Plan
                    </button>
                </div>
                <div class="border-2 border-blue-600 rounded-xl p-8 relative transform scale-105">
                    <div class="absolute top-0 right-0 bg-blue-600 text-white px-4 py-1 rounded-bl-lg rounded-tr-lg text-sm">Popular</div>
                    <h4 class="text-2xl font-bold mb-4">Pro</h4>
                    <p class="text-4xl font-bold mb-6">$29<span class="text-lg text-gray-600">/mo</span></p>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Everything in Starter</li>
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Feature 4</li>
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Feature 5</li>
                    </ul>
                    <button class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700">
                        Choose Plan
                    </button>
                </div>
                <div class="border-2 rounded-xl p-8 hover:border-blue-600 transition">
                    <h4 class="text-2xl font-bold mb-4">Enterprise</h4>
                    <p class="text-4xl font-bold mb-6">$99<span class="text-lg text-gray-600">/mo</span></p>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Everything in Pro</li>
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Feature 6</li>
                        <li class="flex items-center gap-2"><span class="text-green-500">✓</span> Priority Support</li>
                    </ul>
                    <button class="w-full border-2 border-blue-600 text-blue-600 py-3 rounded-lg hover:bg-blue-50">
                        Choose Plan
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 bg-gray-50 px-4">
        <div class="max-w-3xl mx-auto">
            <h3 class="text-4xl font-bold text-center mb-8">Get In Touch</h3>
            <form class="bg-white p-8 rounded-xl shadow-md">
                <div class="mb-6">
                    <label class="block text-gray-700 font-bold mb-2">Name</label>
                    <input type="text" class="w-full border-2 rounded-lg px-4 py-2 focus:border-blue-600 outline-none" required>
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 font-bold mb-2">Email</label>
                    <input type="email" class="w-full border-2 rounded-lg px-4 py-2 focus:border-blue-600 outline-none" required>
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 font-bold mb-2">Message</label>
                    <textarea class="w-full border-2 rounded-lg px-4 py-2 focus:border-blue-600 outline-none h-32" required></textarea>
                </div>
                <button class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-bold">
                    Send Message
                </button>
            </form>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12 px-4">
        <div class="max-w-7xl mx-auto text-center">
            <p>&copy; 2024 BrandName. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
""",

    "portfolio": """
<!-- PORTFOLIO EXAMPLE TEMPLATE -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white">
    <!-- Hero Section -->
    <section class="min-h-screen flex items-center justify-center px-4">
        <div class="text-center">
            <h1 class="text-6xl md:text-8xl font-bold mb-6 animate-fade-in">John Doe</h1>
            <p class="text-2xl text-gray-400 mb-8">Creative Developer & Designer</p>
            <div class="flex gap-6 justify-center">
                <a href="#work" class="bg-white text-gray-900 px-8 py-3 rounded-full hover:bg-gray-200 transition">View Work</a>
                <a href="#contact" class="border-2 border-white px-8 py-3 rounded-full hover:bg-white hover:text-gray-900 transition">Contact Me</a>
            </div>
        </div>
    </section>

    <!-- Work Section -->
    <section id="work" class="py-20 px-4 bg-gray-800">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-5xl font-bold mb-16 text-center">Selected Work</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="group cursor-pointer">
                    <div class="overflow-hidden rounded-lg">
                        <img src="https://via.placeholder.com/600x400" alt="Project 1" class="w-full transform group-hover:scale-110 transition duration-500">
                    </div>
                    <h3 class="text-2xl font-bold mt-4">Project Name</h3>
                    <p class="text-gray-400">Web Design • Development</p>
                </div>
                <div class="group cursor-pointer">
                    <div class="overflow-hidden rounded-lg">
                        <img src="https://via.placeholder.com/600x400" alt="Project 2" class="w-full transform group-hover:scale-110 transition duration-500">
                    </div>
                    <h3 class="text-2xl font-bold mt-4">Project Name</h3>
                    <p class="text-gray-400">Branding • UI/UX</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Skills Section -->
    <section class="py-20 px-4">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-5xl font-bold mb-16 text-center">Skills</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                <div class="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                    <div class="text-4xl mb-3">💻</div>
                    <p class="font-bold">Web Development</p>
                </div>
                <div class="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                    <div class="text-4xl mb-3">🎨</div>
                    <p class="font-bold">UI/UX Design</p>
                </div>
                <div class="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                    <div class="text-4xl mb-3">📱</div>
                    <p class="font-bold">Mobile Apps</p>
                </div>
                <div class="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                    <div class="text-4xl mb-3">⚡</div>
                    <p class="font-bold">Performance</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 px-4 bg-gray-800">
        <div class="max-w-2xl mx-auto text-center">
            <h2 class="text-5xl font-bold mb-8">Let's Work Together</h2>
            <p class="text-xl text-gray-400 mb-8">Have a project in mind? Let's create something amazing together.</p>
            <a href="mailto:hello@example.com" class="inline-block bg-white text-gray-900 px-12 py-4 rounded-full text-lg font-bold hover:bg-gray-200 transition">
                Get In Touch
            </a>
        </div>
    </section>

    <footer class="py-8 text-center text-gray-500">
        <p>&copy; 2024 John Doe. All rights reserved.</p>
    </footer>
</body>
</html>
""",

    "cake_shop": """
<!-- CAKE SHOP COMPLETE EXAMPLE TEMPLATE -->
<!-- INDEX PAGE -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sweet Bites - Cakes</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-pink-50">
    <!-- Header -->
    <header class="bg-white shadow-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-3xl font-bold text-pink-600">Sweet Bites</h1>
                <nav class="flex gap-6 items-center">
                    <a href="index.html" class="text-gray-700 hover:text-pink-600 transition">Home</a>
                    <a href="cart.html" class="text-gray-700 hover:text-pink-600 transition">
                        Cart (<span id="cart-count">0</span>)
                    </a>
                </nav>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
        <h2 class="text-4xl font-bold mb-8 text-gray-800">Our Cakes</h2>
        <div id="cakes-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <!-- Cakes will be loaded here dynamically -->
        </div>
    </main>

    <script>
        // Sample cake data
        const cakes = [
            {id: 1, name: "Chocolate Delight", price: 450, image: "https://via.placeholder.com/300x250/8B4513/FFFFFF?text=Chocolate+Cake"},
            {id: 2, name: "Vanilla Dream", price: 400, image: "https://via.placeholder.com/300x250/FFE4B5/8B4513?text=Vanilla+Cake"},
            {id: 3, name: "Strawberry Bliss", price: 500, image: "https://via.placeholder.com/300x250/FF69B4/FFFFFF?text=Strawberry+Cake"},
            {id: 4, name: "Red Velvet", price: 550, image: "https://via.placeholder.com/300x250/DC143C/FFFFFF?text=Red+Velvet"},
            {id: 5, name: "Black Forest", price: 600, image: "https://via.placeholder.com/300x250/2F1B0C/FFFFFF?text=Black+Forest"},
            {id: 6, name: "Butterscotch", price: 480, image: "https://via.placeholder.com/300x250/DAA520/FFFFFF?text=Butterscotch"},
            {id: 7, name: "Pineapple Cake", price: 420, image: "https://via.placeholder.com/300x250/FFD700/8B4513?text=Pineapple"},
            {id: 8, name: "Fruit Cake", price: 520, image: "https://via.placeholder.com/300x250/FF6347/FFFFFF?text=Fruit+Cake"}
        ];

        // Cart stored in memory
        let cart = [];

        // Load cart from memory on page load
        function loadCart() {
            // In a real app, this would load from backend/session
            const savedCart = sessionStorage.getItem('cart');
            if (savedCart) {
                cart = JSON.parse(savedCart);
            }
            updateCartCount();
        }

        // Save cart to session (temporary storage for demo)
        function saveCart() {
            sessionStorage.setItem('cart', JSON.stringify(cart));
            updateCartCount();
        }

        // Update cart count in header
        function updateCartCount() {
            const count = cart.reduce((sum, item) => sum + item.qty, 0);
            document.getElementById('cart-count').textContent = count;
        }

        // Render cakes grid
        function renderCakes() {
            const grid = document.getElementById('cakes-grid');
            grid.innerHTML = cakes.map(cake => `
                <div class="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition transform hover:-translate-y-1">
                    <img src="${cake.image}" alt="${cake.name}" class="w-full h-48 object-cover">
                    <div class="p-4">
                        <h3 class="text-xl font-bold text-gray-800 mb-2">${cake.name}</h3>
                        <p class="text-2xl font-semibold text-pink-600 mb-4">₹${cake.price}</p>
                        <button onclick="addToCart(${cake.id})" class="w-full bg-pink-600 text-white py-2 rounded-lg hover:bg-pink-700 transition font-semibold">
                            Add to Cart
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Add item to cart
        function addToCart(cakeId) {
            const cake = cakes.find(c => c.id === cakeId);
            const existingItem = cart.find(item => item.id === cakeId);
            
            if (existingItem) {
                existingItem.qty++;
            } else {
                cart.push({
                    id: cake.id,
                    name: cake.name,
                    price: cake.price,
                    qty: 1
                });
            }
            
            saveCart();
            
            // Show notification
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = 'Added!';
            btn.classList.add('bg-green-600', 'hover:bg-green-700');
            btn.classList.remove('bg-pink-600', 'hover:bg-pink-700');
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.classList.remove('bg-green-600', 'hover:bg-green-700');
                btn.classList.add('bg-pink-600', 'hover:bg-pink-700');
            }, 1000);
        }

        // Initialize
        loadCart();
        renderCakes();
    </script>
</body>
</html>

<!-- CART PAGE (cart.html) -->
<!-- This would be a separate file -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cart - Sweet Bites</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-pink-50">
    <header class="bg-white shadow-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-3xl font-bold text-pink-600">Sweet Bites</h1>
                <nav class="flex gap-6 items-center">
                    <a href="index.html" class="text-gray-700 hover:text-pink-600 transition">Home</a>
                    <a href="cart.html" class="text-gray-700 hover:text-pink-600 transition">Cart</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
        <h2 class="text-4xl font-bold mb-8 text-gray-800">Your Cart</h2>
        <div id="cart-content"></div>
    </main>

    <script>
        let cart = [];

        function loadCart() {
            const savedCart = sessionStorage.getItem('cart');
            if (savedCart) {
                cart = JSON.parse(savedCart);
            }
            renderCart();
        }

        function saveCart() {
            sessionStorage.setItem('cart', JSON.stringify(cart));
            renderCart();
        }

        function renderCart() {
            const container = document.getElementById('cart-content');
            
            if (cart.length === 0) {
                container.innerHTML = `
                    <div class="bg-white rounded-lg shadow-md p-8 text-center">
                        <p class="text-xl text-gray-600 mb-4">Your cart is empty</p>
                        <a href="index.html" class="inline-block bg-pink-600 text-white px-6 py-3 rounded-lg hover:bg-pink-700 transition">
                            Shop Cakes
                        </a>
                    </div>
                `;
                return;
            }

            const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);

            container.innerHTML = `
                <div class="bg-white rounded-lg shadow-md overflow-hidden">
                    <table class="w-full">
                        <thead class="bg-pink-100">
                            <tr>
                                <th class="px-6 py-3 text-left">Item</th>
                                <th class="px-6 py-3 text-center">Quantity</th>
                                <th class="px-6 py-3 text-right">Price</th>
                                <th class="px-6 py-3 text-right">Total</th>
                                <th class="px-6 py-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            ${cart.map(item => `
                                <tr class="border-b">
                                    <td class="px-6 py-4 font-semibold">${item.name}</td>
                                    <td class="px-6 py-4 text-center">
                                        <div class="flex items-center justify-center gap-2">
                                            <button onclick="updateQty(${item.id}, -1)" class="bg-gray-200 hover:bg-gray-300 w-8 h-8 rounded">-</button>
                                            <span class="w-12 text-center">${item.qty}</span>
                                            <button onclick="updateQty(${item.id}, 1)" class="bg-gray-200 hover:bg-gray-300 w-8 h-8 rounded">+</button>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-right">₹${item.price}</td>
                                    <td class="px-6 py-4 text-right font-semibold">₹${item.price * item.qty}</td>
                                    <td class="px-6 py-4 text-right">
                                        <button onclick="removeItem(${item.id})" class="text-red-600 hover:text-red-800">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    <div class="p-6 bg-gray-50">
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-2xl font-bold">Subtotal:</span>
                            <span class="text-2xl font-bold text-pink-600">₹${subtotal}</span>
                        </div>
                        <div class="flex gap-4">
                            <button onclick="updateCart()" class="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition font-semibold">
                                Update Cart
                            </button>
                            <a href="checkout.html" class="flex-1 bg-pink-600 text-white py-3 rounded-lg hover:bg-pink-700 transition font-semibold text-center">
                                Proceed to Checkout
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }

        function updateQty(id, change) {
            const item = cart.find(i => i.id === id);
            if (item) {
                item.qty += change;
                if (item.qty <= 0) {
                    removeItem(id);
                } else {
                    saveCart();
                }
            }
        }

        function removeItem(id) {
            cart = cart.filter(i => i.id !== id);
            saveCart();
        }

        function updateCart() {
            saveCart();
            alert('Cart updated successfully!');
        }

        loadCart();
    </script>
</body>
</html>
"""
}

class AIWebBuilder:
    def __init__(self):
        self.conversation_history = []
        self.project_name = None
        self.project_files = {}
        self.needs_backend = False
        
    def get_relevant_templates(self, user_prompt):
        """Select relevant template examples based on user prompt"""
        prompt_lower = user_prompt.lower()
        selected_templates = []
        
        # Check which templates are relevant
        if any(word in prompt_lower for word in ['cake', 'bakery', 'sweet', 'dessert', 'pastry']):
            selected_templates.append(('Cake Shop', TEMPLATE_EXAMPLES['cake_shop']))
        
        if any(word in prompt_lower for word in ['shop', 'store', 'ecommerce', 'e-commerce', 'cart', 'product', 'buy', 'sell']):
            selected_templates.append(('E-Commerce', TEMPLATE_EXAMPLES['ecommerce']))
        
        if any(word in prompt_lower for word in ['landing', 'saas', 'service', 'features', 'pricing', 'startup']):
            selected_templates.append(('Landing Page', TEMPLATE_EXAMPLES['landing']))
        
        if any(word in prompt_lower for word in ['portfolio', 'showcase', 'work', 'projects', 'designer', 'developer', 'artist']):
            selected_templates.append(('Portfolio', TEMPLATE_EXAMPLES['portfolio']))
        
        # If no specific match, include landing page as default
        if not selected_templates:
            selected_templates.append(('Landing Page', TEMPLATE_EXAMPLES['landing']))
        
        return selected_templates
        
    def generate_website(self, user_prompt):
        """Main function to generate website from user prompt"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_prompt
        })
        
        # Get relevant template examples
        relevant_templates = self.get_relevant_templates(user_prompt)
        template_context = "\n\n".join([
            f"=== {name} Template Example ===\n{code}" 
            for name, code in relevant_templates
        ])
        
        # System prompt for the AI agent with few-shot examples
        system_prompt = f"""You are an expert web developer AI agent. Your job is to:
1. Understand user requirements for websites
2. Generate complete, production-ready HTML, CSS, and JavaScript code
3. Create modern, responsive, and accessible websites using Tailwind CSS
4. Learn from the template examples provided and generate similar quality code
5. Identify if backend is needed
6. Return code in a structured JSON format

IMPORTANT TEMPLATE EXAMPLES TO LEARN FROM:
{template_context}

Study these examples carefully! They demonstrate:
- Proper HTML structure and semantic markup
- Tailwind CSS usage for styling
- JavaScript for interactivity
- Responsive design patterns
- Component organization
- Cart functionality for e-commerce
- Form handling
- Modal dialogs
- Navigation patterns
- Layout best practices

When generating code, return a JSON object with this structure:
{{
    "project_name": "project-name",
    "needs_backend": true/false,
    "backend_requirements": "Brief description of what backend features are needed (if any)",
    "files": {{
        "index.html": "HTML content here",
        "cart.html": "Additional pages if needed",
        "checkout.html": "More pages as required",
        "styles.css": "Custom CSS if needed beyond Tailwind",
        "script.js": "JavaScript for functionality"
    }},
    "description": "Brief description of what was created"
}}

Set "needs_backend" to TRUE if the website requires:
- Database (storing products, users, orders, etc.)
- User authentication/login
- Payment processing
- Server-side operations
- API integration
- Real-time features
- Order management
- Email sending
- Admin panels with data persistence

IMPORTANT CODE QUALITY REQUIREMENTS:
1. Use Tailwind CSS CDN: <script src="https://cdn.tailwindcss.com"></script>
2. Make it fully responsive (mobile-first approach)
3. Include proper semantic HTML5 tags
4. Add accessibility features (ARIA labels, alt tags, proper form labels)
5. DO NOT use localStorage or sessionStorage - use JavaScript variables for cart/data
6. Include smooth transitions and hover effects
7. Add clear comments explaining functionality
8. For e-commerce: Implement full cart functionality like the example
9. Use modern JavaScript (ES6+) with arrow functions, template literals
10. Ensure clean, readable, well-organized code
11. Add proper error handling for forms
12. Include loading states for buttons when appropriate

STYLING GUIDELINES:
- Use consistent color schemes (primary, secondary, accent colors)
- Proper spacing and typography hierarchy
- Smooth transitions (transition-all duration-300)
- Hover effects on interactive elements
- Shadow effects for depth (shadow-md, shadow-lg)
- Rounded corners for modern look (rounded-lg, rounded-xl)
- Gradient backgrounds where appropriate
- Proper contrast for accessibility

FUNCTIONAL REQUIREMENTS:
- All forms should have validation
- Buttons should have hover and active states
- Navigation should be sticky or fixed
- Mobile menu for responsive navigation
- Shopping carts should use JavaScript variables (NOT localStorage)
- Modals should have backdrop and close buttons
- Images should be lazy-loaded where possible
- Add smooth scroll behavior

Make websites visually stunning and highly functional!"""

        # Prepare messages for OpenAI API
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation_history
        
        print("\n🤖 AI Agent is analyzing requirements and studying templates...\n")
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Get the response
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Parse the JSON response
        try:
            result = json.loads(assistant_message)
            self.project_name = result.get("project_name", f"website-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            self.project_files = result.get("files", {})
            self.needs_backend = result.get("needs_backend", False)
            backend_requirements = result.get("backend_requirements", "")
            description = result.get("description", "Website generated successfully")
            
            print(f"✅ {description}\n")
            print(f"📄 Generated {len(self.project_files)} file(s): {', '.join(self.project_files.keys())}\n")
            
            # Inform user about backend needs
            if self.needs_backend:
                print("⚠️  BACKEND REQUIRED")
                print("=" * 60)
                print(f"📋 Backend Requirements: {backend_requirements}")
                print("💡 A 'backend' folder will be created for your backend code")
                print("=" * 60)
                print()
            
            return result
            
        except json.JSONDecodeError:
            print("❌ Error: Could not parse AI response")
            return None
    
    def save_project(self, output_dir="output"):
        """Save the generated project to disk"""
        if not self.project_files:
            print("❌ No project to save. Generate a website first.")
            return
        
        # Create project directory
        project_path = os.path.join(output_dir, self.project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create backend folder if needed
        if self.needs_backend:
            backend_path = os.path.join(project_path, "backend")
            os.makedirs(backend_path, exist_ok=True)
            
            # Create README in backend folder
            readme_content = """# Backend Setup Instructions

## This website requires a backend implementation.

### Recommended Backend Options:

1. **Supabase** (Recommended - Free tier available)
   - Database: PostgreSQL
   - Authentication: Built-in
   - Storage: File storage included
   - Setup: https://supabase.com

2. **Firebase** (Google - Free tier available)
   - Database: Firestore (NoSQL)
   - Authentication: Built-in
   - Storage: Cloud Storage
   - Setup: https://firebase.google.com

3. **PocketBase** (Self-hosted - Completely free)
   - Database: SQLite
   - Authentication: Built-in
   - Storage: Local storage
   - Setup: https://pocketbase.io

4. **Custom Backend**
   - Node.js + Express + PostgreSQL/MongoDB
   - Python + FastAPI + PostgreSQL/MongoDB
   - Any backend framework of your choice

### Next Steps:
1. Choose a backend option from above
2. Set up the backend service
3. Configure API endpoints
4. Connect your frontend to the backend API
5. Test the integration

### Frontend Integration:
- Update API endpoint URLs in your JavaScript files
- Add authentication logic if needed
- Connect database queries to your backend
"""
            with open(os.path.join(backend_path, "README.md"), "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            print(f"📁 Created backend folder: {backend_path}")
            print(f"📄 Created backend/README.md with setup instructions\n")
        
        # Save all files
        for filename, content in self.project_files.items():
            file_path = os.path.join(project_path, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"📄 Created: {file_path}")
        
        print(f"\n✅ Project saved to: {project_path}")
        print(f"💡 Open {os.path.join(project_path, 'index.html')} in your browser to view the website\n")
    
    def preview_file(self, filename):
        """Preview a generated file"""
        if filename not in self.project_files:
            print(f"❌ File '{filename}' not found. Available files: {', '.join(self.project_files.keys())}")
            return
        
        print(f"\n{'='*60}")
        print(f"📄 Preview: {filename}")
        print(f"{'='*60}\n")
        print(self.project_files[filename][:1000])  # Show first 1000 chars
        if len(self.project_files[filename]) > 1000:
            print("\n... (truncated, use 'save' to see full file)")
        print()
    
    def modify_website(self, modification_request):
        """Modify existing website based on user request"""
        if not self.project_files:
            print("❌ No project to modify. Generate a website first.")
            return None
        
        # Add modification request to conversation
        modification_prompt = f"MODIFY REQUEST: {modification_request}\n\nCurrent project files:\n"
        for filename in self.project_files.keys():
            modification_prompt += f"- {filename}\n"
        
        self.conversation_history.append({
            "role": "user",
            "content": modification_prompt
        })
        
        return self.generate_website(modification_request)

def main():
    """Main interactive loop"""
    print("=" * 60)
    print("🤖 AI WEB BUILDER AGENT")
    print("=" * 60)
    print("👋 Welcome! I can build any website you describe.")
    print("\n💡 Commands:")
    print("   - Type any website description to generate")
    print("   - 'save' - Save project to output folder")
    print("   - 'preview' - View generated code")
    print("   - 'modify: <changes>' - Update existing project")
    print("   - 'new' - Start fresh project")
    print("   - 'quit' - Exit")
    print("=" * 60)
    
    builder = AIWebBuilder()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'save':
                builder.save_project()
            
            elif user_input.lower() == 'preview':
                if not builder.project_files:
                    print("❌ No project to preview. Generate a website first.")
                    continue
                print("\n📂 Available files:")
                for i, filename in enumerate(builder.project_files.keys(), 1):
                    print(f"   {i}. {filename}")
                file_choice = input("\n📄 Enter filename to preview: ").strip()
                builder.preview_file(file_choice)
            
            elif user_input.lower() == 'new':
                builder = AIWebBuilder()
                print("✨ Started new project!")
            
            elif user_input.lower().startswith('modify:'):
                modification = user_input[7:].strip()
                if modification:
                    builder.modify_website(modification)
                else:
                    print("❌ Please specify what to modify. Example: modify: make header sticky")
            
            else:
                # Generate new website
                builder.generate_website(user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("💡 Set it with: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    main()