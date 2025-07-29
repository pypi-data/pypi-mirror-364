import os
import random
from datetime import datetime, timedelta


os.environ['APP_ENV'] = 'test'


def generate_user_data():
    """Generate realistic user data for testing"""
    usernames = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'henry']
    domains = ['example.com', 'test.org', 'demo.net', 'sample.io']
    statuses = ['active', 'inactive', 'pending', 'suspended']

    username = random.choice(usernames)
    domain = random.choice(domains)

    return {
        'username': username,
        'email': '{}@{}'.format(username, domain),
        'age': random.randint(18, 80),
        'status': random.choice(statuses),
        'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 365)),
        'last_login': datetime.utcnow() - timedelta(hours=random.randint(0, 720)),
        'preferences': {
            'theme': random.choice(['light', 'dark']),
            'notifications': random.choice([True, False]),
            'language': random.choice(['en', 'es', 'fr', 'de'])
        },
        'tags': random.sample(['vip', 'beta', 'premium', 'student', 'staff'], k=random.randint(0, 3))
    }


def generate_product_data():
    """Generate product data for e-commerce testing"""
    categories = ['electronics', 'clothing', 'books', 'home', 'sports', 'automotive']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']

    category = random.choice(categories)
    brand = random.choice(brands)

    return {
        'name': '{} {} Item {}'.format(brand, category.title(), random.randint(1000, 9999)),
        'category': category,
        'brand': brand,
        'price': round(random.uniform(9.99, 999.99), 2),
        'in_stock': random.randint(0, 100),
        'rating': round(random.uniform(1.0, 5.0), 1),
        'reviews_count': random.randint(0, 500),
        'featured': random.choice([True, False]),
        'dimensions': {
            'length': round(random.uniform(5.0, 50.0), 1),
            'width': round(random.uniform(5.0, 50.0), 1),
            'height': round(random.uniform(2.0, 20.0), 1)
        },
        'attributes': {
            'color': random.choice(['red', 'blue', 'green', 'black', 'white']),
            'material': random.choice(['plastic', 'metal', 'wood', 'fabric', 'glass']),
            'weight': round(random.uniform(0.1, 10.0), 2)
        }
    }


def generate_event_data():
    """Generate event/log data for analytics testing"""
    event_types = ['page_view', 'click', 'purchase', 'signup', 'login', 'logout', 'error']
    user_agents = ['Chrome/91.0', 'Firefox/89.0', 'Safari/14.1', 'Edge/91.0']
    sources = ['organic', 'social', 'email', 'direct', 'referral', 'paid']

    return {
        'event_type': random.choice(event_types),
        'user_id': 'user_{}'.format(random.randint(1000, 9999)),
        'session_id': 'session_{}'.format(random.randint(100000, 999999)),
        'timestamp': datetime.utcnow() - timedelta(minutes=random.randint(0, 10080)),  # Past week
        'page_url': '/page/{}'.format(random.randint(1, 50)),
        'user_agent': random.choice(user_agents),
        'ip_address': '{}.{}.{}.{}'.format(
            random.randint(1, 255), random.randint(1, 255),
            random.randint(1, 255), random.randint(1, 255)
        ),
        'source': random.choice(sources),
        'metadata': {
            'screen_width': random.choice([1920, 1366, 1440, 1024, 768]),
            'screen_height': random.choice([1080, 768, 900, 768, 1024]),
            'browser_language': random.choice(['en-US', 'es-ES', 'fr-FR', 'de-DE']),
            'time_on_page': random.randint(5, 300)  # seconds
        }
    }


def generate_order_data():
    """Generate order data for transaction testing"""
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
    payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']

    items_count = random.randint(1, 5)
    items = []
    subtotal = 0

    for _ in range(items_count):
        price = round(random.uniform(10.0, 200.0), 2)
        quantity = random.randint(1, 3)
        items.append({
            'product_id': 'prod_{}'.format(random.randint(1000, 9999)),
            'name': 'Product {}'.format(random.randint(1, 100)),
            'price': price,
            'quantity': quantity,
            'total': round(price * quantity, 2)
        })
        subtotal += price * quantity

    tax = round(subtotal * 0.08, 2)  # 8% tax
    shipping = round(random.uniform(0, 25.0), 2) if subtotal < 50 else 0
    total = round(subtotal + tax + shipping, 2)

    return {
        'order_id': 'ORD-{}'.format(random.randint(100000, 999999)),
        'customer_id': 'cust_{}'.format(random.randint(1000, 9999)),
        'status': random.choice(statuses),
        'order_date': datetime.utcnow() - timedelta(days=random.randint(0, 90)),
        'payment_method': random.choice(payment_methods),
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
        'shipping_address': {
            'street': '{} Main St'.format(random.randint(100, 9999)),
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'state': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
            'zip_code': '{}'.format(random.randint(10000, 99999)),
            'country': 'US'
        }
    }


def generate_inventory_data():
    """Generate inventory/warehouse data for supply chain testing"""
    locations = ['warehouse_a', 'warehouse_b', 'store_1', 'store_2', 'store_3']
    conditions = ['new', 'refurbished', 'damaged', 'returned']

    quantity_on_hand = random.randint(0, 500)
    quantity_reserved = random.randint(0, 50)
    quantity_available = max(0, quantity_on_hand - quantity_reserved)

    return {
        'sku': 'SKU-{}'.format(random.randint(100000, 999999)),
        'product_name': 'Product {}'.format(random.randint(1, 1000)),
        'location': random.choice(locations),
        'quantity_on_hand': quantity_on_hand,
        'quantity_reserved': quantity_reserved,
        'quantity_available': quantity_available,
        'condition': random.choice(conditions),
        'last_updated': datetime.utcnow() - timedelta(hours=random.randint(0, 168)),  # Past week
        'reorder_point': random.randint(10, 50),
        'max_stock': random.randint(100, 1000),
        'unit_cost': round(random.uniform(5.0, 100.0), 2),
        'location_details': {
            'aisle': random.choice(['A', 'B', 'C', 'D']),
            'shelf': random.randint(1, 10),
            'bin': random.randint(1, 20)
        }
    }


# # Sample data sets for bulk testing
# SAMPLE_USERS = [generate_user_data() for _ in range(50)]
# SAMPLE_PRODUCTS = [generate_product_data() for _ in range(30)]
# SAMPLE_EVENTS = [generate_event_data() for _ in range(100)]
# SAMPLE_ORDERS = [generate_order_data() for _ in range(25)]
# SAMPLE_INVENTORY = [generate_inventory_data() for _ in range(40)]


# Test collection names
TEST_COLLECTIONS = {
    'users': 'test_users',
    'products': 'test_products',
    'events': 'test_events',
    'orders': 'test_orders',
    'inventory': 'test_inventory',
    'simple': 'test_simple',
    'crud': 'test_crud',
    'bulk_errors': 'test_bulk_errors'
}
