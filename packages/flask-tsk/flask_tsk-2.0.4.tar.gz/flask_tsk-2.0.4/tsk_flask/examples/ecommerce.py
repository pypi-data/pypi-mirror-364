"""
E-commerce Example

A complete e-commerce system showcasing product management, user accounts,
shopping cart functionality, and elephant services integration.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from .base_example import BaseExample
from tsk_flask.herd import Herd


class EcommerceExample(BaseExample):
    """E-commerce example with product management and elephant services"""
    
    def __init__(self):
        super().__init__(
            name="E-commerce System",
            description="Complete e-commerce system with product management, user accounts, and elephant services"
        )
        self.products = self._initialize_products()
        self.carts = {}  # Simple in-memory cart storage
    
    def create_app(self, config=None):
        """Create the e-commerce example app"""
        app = super().create_app(config)
        
        # Add e-commerce specific routes
        self._add_ecommerce_routes()
        
        return app
    
    def _initialize_products(self):
        """Initialize sample products using Babar for content management"""
        products = [
            {
                'id': '1',
                'name': 'Elephant Plush Toy',
                'description': 'A soft and cuddly elephant plush toy',
                'price': 29.99,
                'category': 'toys',
                'image': '/static/images/elephant-toy.jpg',
                'stock': 50
            },
            {
                'id': '2', 
                'name': 'Tusk Coffee Mug',
                'description': 'Beautiful ceramic coffee mug with tusk design',
                'price': 15.99,
                'category': 'kitchen',
                'image': '/static/images/tusk-mug.jpg',
                'stock': 25
            },
            {
                'id': '3',
                'name': 'Herd T-Shirt',
                'description': 'Comfortable cotton t-shirt with herd design',
                'price': 24.99,
                'category': 'clothing',
                'image': '/static/images/herd-tshirt.jpg',
                'stock': 30
            }
        ]
        
        # Store products using Babar if available
        if 'babar' in self.elephants:
            for product in products:
                try:
                    self.elephants['babar'].create_story({
                        'title': product['name'],
                        'content': product['description'],
                        'type': 'product',
                        'status': 'published',
                        'metadata': {
                            'product_id': product['id'],
                            'price': product['price'],
                            'category': product['category'],
                            'image': product['image'],
                            'stock': product['stock']
                        }
                    })
                except:
                    pass  # Continue if Babar is not available
        
        return products
    
    def _add_ecommerce_routes(self):
        """Add e-commerce specific routes"""
        
        @self.app.route('/shop')
        def shop():
            """Product catalog"""
            category = request.args.get('category')
            
            if category:
                filtered_products = [p for p in self.products if p['category'] == category]
            else:
                filtered_products = self.products
            
            return render_template('shop/index.html', products=filtered_products)
        
        @self.app.route('/shop/product/<product_id>')
        def product_detail(product_id):
            """Individual product page"""
            product = next((p for p in self.products if p['id'] == product_id), None)
            
            if not product:
                return render_template('error.html', error='Product not found'), 404
            
            # Get related products using Heffalump search
            related_products = []
            if 'heffalump' in self.elephants:
                try:
                    results = self.elephants['heffalump'].hunt(product['category'], ['category'])
                    for result in results[:3]:
                        related = next((p for p in self.products if p['id'] == result.id), None)
                        if related and related['id'] != product_id:
                            related_products.append(related)
                except:
                    pass
            
            return render_template('shop/product.html', 
                                product=product, 
                                related_products=related_products)
        
        @self.app.route('/cart')
        def cart():
            """Shopping cart"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user_id = Herd.id()
            user_cart = self.carts.get(user_id, [])
            
            total = sum(item['price'] * item['quantity'] for item in user_cart)
            
            return render_template('shop/cart.html', cart=user_cart, total=total)
        
        @self.app.route('/cart/add/<product_id>', methods=['POST'])
        def add_to_cart(product_id):
            """Add product to cart"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            product = next((p for p in self.products if p['id'] == product_id), None)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            quantity = int(request.form.get('quantity', 1))
            user_id = Herd.id()
            
            if user_id not in self.carts:
                self.carts[user_id] = []
            
            # Check if product already in cart
            cart_item = next((item for item in self.carts[user_id] if item['id'] == product_id), None)
            
            if cart_item:
                cart_item['quantity'] += quantity
            else:
                self.carts[user_id].append({
                    'id': product_id,
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'image': product['image']
                })
            
            # Notify with Koshik
            if 'koshik' in self.elephants:
                try:
                    self.elephants['koshik'].notify('success', {
                        'message': f'{product["name"]} added to cart!'
                    })
                except:
                    pass
            
            return jsonify({'success': True, 'message': 'Product added to cart'})
        
        @self.app.route('/cart/remove/<product_id>', methods=['POST'])
        def remove_from_cart(product_id):
            """Remove product from cart"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            user_id = Herd.id()
            if user_id in self.carts:
                self.carts[user_id] = [item for item in self.carts[user_id] if item['id'] != product_id]
            
            return jsonify({'success': True, 'message': 'Product removed from cart'})
        
        @self.app.route('/checkout', methods=['GET', 'POST'])
        def checkout():
            """Checkout process"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user_id = Herd.id()
            user_cart = self.carts.get(user_id, [])
            
            if not user_cart:
                flash('Your cart is empty', 'error')
                return redirect(url_for('cart'))
            
            if request.method == 'POST':
                # Process checkout
                total = sum(item['price'] * item['quantity'] for item in user_cart)
                
                # Create order using Horton background job
                if 'horton' in self.elephants:
                    try:
                        job_id = self.elephants['horton'].dispatch('process_order', {
                            'user_id': user_id,
                            'items': user_cart,
                            'total': total,
                            'shipping_address': request.form.get('shipping_address')
                        })
                    except:
                        pass
                
                # Clear cart
                self.carts[user_id] = []
                
                # Notify with Koshik
                if 'koshik' in self.elephants:
                    try:
                        self.elephants['koshik'].notify('success', {
                            'message': 'Order placed successfully!'
                        })
                    except:
                        pass
                
                flash('Order placed successfully!', 'success')
                return redirect(url_for('orders'))
            
            total = sum(item['price'] * item['quantity'] for item in user_cart)
            return render_template('shop/checkout.html', cart=user_cart, total=total)
        
        @self.app.route('/orders')
        def orders():
            """User's order history"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            # In a real app, this would fetch from database
            # For demo, we'll return empty list
            orders = []
            
            return render_template('shop/orders.html', orders=orders)
        
        @self.app.route('/admin/products')
        def admin_products():
            """Product management for admins"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            return render_template('admin/products.html', products=self.products)
        
        @self.app.route('/admin/products/create', methods=['GET', 'POST'])
        def create_product():
            """Create new product"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            if request.method == 'POST':
                # Handle file upload with Jumbo
                image_path = None
                if 'image' in request.files and request.files['image'].filename:
                    if 'jumbo' in self.elephants:
                        try:
                            file = request.files['image']
                            upload_result = self.elephants['jumbo'].start_upload(
                                file.filename, 
                                len(file.read())
                            )
                            # In real app, would handle chunked upload
                            image_path = f'/static/images/{file.filename}'
                        except:
                            image_path = '/static/images/default.jpg'
                
                # Create product
                new_product = {
                    'id': str(len(self.products) + 1),
                    'name': request.form.get('name'),
                    'description': request.form.get('description'),
                    'price': float(request.form.get('price')),
                    'category': request.form.get('category'),
                    'image': image_path or '/static/images/default.jpg',
                    'stock': int(request.form.get('stock', 0))
                }
                
                self.products.append(new_product)
                
                # Store in Babar
                if 'babar' in self.elephants:
                    try:
                        self.elephants['babar'].create_story({
                            'title': new_product['name'],
                            'content': new_product['description'],
                            'type': 'product',
                            'status': 'published',
                            'metadata': {
                                'product_id': new_product['id'],
                                'price': new_product['price'],
                                'category': new_product['category'],
                                'image': new_product['image'],
                                'stock': new_product['stock']
                            }
                        })
                    except:
                        pass
                
                flash('Product created successfully!', 'success')
                return redirect(url_for('admin_products'))
            
            return render_template('admin/create_product.html')
        
        @self.app.route('/api/shop/search')
        def search_products():
            """Search products using Heffalump"""
            query = request.args.get('q', '')
            
            if not query:
                return jsonify({'products': self.products})
            
            if 'heffalump' in self.elephants:
                try:
                    results = self.elephants['heffalump'].hunt(query, ['name', 'description'])
                    found_products = []
                    for result in results:
                        product = next((p for p in self.products if p['id'] == result.id), None)
                        if product:
                            found_products.append(product)
                    return jsonify({'products': found_products})
                except:
                    pass
            
            # Fallback to simple search
            found_products = [p for p in self.products 
                            if query.lower() in p['name'].lower() 
                            or query.lower() in p['description'].lower()]
            
            return jsonify({'products': found_products})


def create_ecommerce_example():
    """Factory function to create e-commerce example"""
    return EcommerceExample()


if __name__ == '__main__':
    example = create_ecommerce_example()
    example.run() 