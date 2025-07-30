"""
Flask-TSK E-commerce Components
E-commerce components for Flask applications
"""

from flask import render_template_string
from typing import Dict, List, Optional

class EcommerceComponent:
    """E-commerce component system for Flask-TSK"""
    
    @staticmethod
    def product_card(product: Dict, show_price: bool = True, show_rating: bool = True) -> str:
        """Generate a product card component"""
        
        template = '''
        <div class="product-card">
            <div class="product-image">
                <img src="{{ product.image }}" alt="{{ product.name }}">
                {% if product.discount %}
                <span class="product-badge product-badge-discount">{{ product.discount }}% OFF</span>
                {% endif %}
            </div>
            
            <div class="product-content">
                <h3 class="product-title">{{ product.name }}</h3>
                
                {% if product.description %}
                <p class="product-description">{{ product.description }}</p>
                {% endif %}
                
                {% if show_price %}
                <div class="product-price">
                    {% if product.original_price and product.original_price != product.price %}
                    <span class="product-price-original">${{ "%.2f"|format(product.original_price) }}</span>
                    {% endif %}
                    <span class="product-price-current">${{ "%.2f"|format(product.price) }}</span>
                </div>
                {% endif %}
                
                {% if show_rating and product.rating %}
                <div class="product-rating">
                    <div class="stars">
                        {% for i in range(5) %}
                        <span class="star {{ 'filled' if i < product.rating else '' }}">★</span>
                        {% endfor %}
                    </div>
                    <span class="rating-count">({{ product.review_count }})</span>
                </div>
                {% endif %}
                
                <div class="product-actions">
                    <button class="btn btn-primary add-to-cart" data-product-id="{{ product.id }}">
                        Add to Cart
                    </button>
                    <button class="btn btn-outline wishlist-btn" data-product-id="{{ product.id }}">
                        <i class="fas fa-heart"></i>
                    </button>
                </div>
            </div>
        </div>
        '''
        
        return render_template_string(template, product=product, show_price=show_price, show_rating=show_rating)
    
    @staticmethod
    def product_grid(products: List[Dict], columns: int = 4) -> str:
        """Generate a product grid"""
        
        template = '''
        <div class="product-grid product-grid-{{ columns }}-columns">
            {% for product in products %}
            <div class="product-grid-item">
                {{ product_card | safe }}
            </div>
            {% endfor %}
        </div>
        '''
        
        product_cards = [EcommerceComponent.product_card(product) for product in products]
        
        return render_template_string(template, products=products, columns=columns, product_card=''.join(product_cards))
    
    @staticmethod
    def shopping_cart(cart_items: List[Dict], show_totals: bool = True) -> str:
        """Generate a shopping cart component"""
        
        template = '''
        <div class="shopping-cart">
            <h3 class="cart-title">Shopping Cart</h3>
            
            {% if cart_items %}
            <div class="cart-items">
                {% for item in cart_items %}
                <div class="cart-item">
                    <div class="cart-item-image">
                        <img src="{{ item.image }}" alt="{{ item.name }}">
                    </div>
                    
                    <div class="cart-item-details">
                        <h4 class="cart-item-name">{{ item.name }}</h4>
                        <p class="cart-item-price">${{ "%.2f"|format(item.price) }}</p>
                    </div>
                    
                    <div class="cart-item-quantity">
                        <button class="quantity-btn minus" data-item-id="{{ item.id }}">-</button>
                        <input type="number" value="{{ item.quantity }}" min="1" class="quantity-input" data-item-id="{{ item.id }}">
                        <button class="quantity-btn plus" data-item-id="{{ item.id }}">+</button>
                    </div>
                    
                    <div class="cart-item-total">
                        ${{ "%.2f"|format(item.price * item.quantity) }}
                    </div>
                    
                    <button class="cart-item-remove" data-item-id="{{ item.id }}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                {% endfor %}
            </div>
            
            {% if show_totals %}
            <div class="cart-totals">
                <div class="cart-subtotal">
                    <span>Subtotal:</span>
                    <span>${{ "%.2f"|format(subtotal) }}</span>
                </div>
                <div class="cart-tax">
                    <span>Tax:</span>
                    <span>${{ "%.2f"|format(tax) }}</span>
                </div>
                <div class="cart-total">
                    <span>Total:</span>
                    <span>${{ "%.2f"|format(total) }}</span>
                </div>
            </div>
            
            <div class="cart-actions">
                <button class="btn btn-outline" onclick="clearCart()">Clear Cart</button>
                <button class="btn btn-primary" onclick="checkout()">Checkout</button>
            </div>
            {% endif %}
            
            {% else %}
            <div class="cart-empty">
                <p>Your cart is empty</p>
                <a href="/products" class="btn btn-primary">Continue Shopping</a>
            </div>
            {% endif %}
        </div>
        '''
        
        if cart_items:
            subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
            tax = subtotal * 0.08  # 8% tax
            total = subtotal + tax
        else:
            subtotal = tax = total = 0
        
        return render_template_string(template, cart_items=cart_items, show_totals=show_totals,
                                    subtotal=subtotal, tax=tax, total=total)
    
    @staticmethod
    def checkout_form(cart_items: List[Dict], user_info: Dict = None) -> str:
        """Generate a checkout form"""
        
        user_info = user_info or {}
        
        template = '''
        <div class="checkout-form">
            <h3 class="checkout-title">Checkout</h3>
            
            <form class="checkout-form-content" method="POST" action="/checkout">
                <div class="checkout-section">
                    <h4>Shipping Information</h4>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="first_name">First Name</label>
                            <input type="text" id="first_name" name="first_name" value="{{ user_info.first_name or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="last_name">Last Name</label>
                            <input type="text" id="last_name" name="last_name" value="{{ user_info.last_name or '' }}" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" value="{{ user_info.email or '' }}" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="address">Address</label>
                        <input type="text" id="address" name="address" value="{{ user_info.address or '' }}" required>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="city">City</label>
                            <input type="text" id="city" name="city" value="{{ user_info.city or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="state">State</label>
                            <input type="text" id="state" name="state" value="{{ user_info.state or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="zip">ZIP Code</label>
                            <input type="text" id="zip" name="zip" value="{{ user_info.zip or '' }}" required>
                        </div>
                    </div>
                </div>
                
                <div class="checkout-section">
                    <h4>Payment Information</h4>
                    <div class="form-group">
                        <label for="card_number">Card Number</label>
                        <input type="text" id="card_number" name="card_number" placeholder="1234 5678 9012 3456" required>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="expiry">Expiry Date</label>
                            <input type="text" id="expiry" name="expiry" placeholder="MM/YY" required>
                        </div>
                        <div class="form-group">
                            <label for="cvv">CVV</label>
                            <input type="text" id="cvv" name="cvv" placeholder="123" required>
                        </div>
                    </div>
                </div>
                
                <div class="checkout-summary">
                    <h4>Order Summary</h4>
                    {% for item in cart_items %}
                    <div class="summary-item">
                        <span>{{ item.name }} x{{ item.quantity }}</span>
                        <span>${{ "%.2f"|format(item.price * item.quantity) }}</span>
                    </div>
                    {% endfor %}
                    
                    <div class="summary-total">
                        <span>Total:</span>
                        <span>${{ "%.2f"|format(total) }}</span>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary btn-large">Place Order</button>
            </form>
        </div>
        '''
        
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        
        return render_template_string(template, cart_items=cart_items, user_info=user_info, total=total) 