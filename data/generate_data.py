import random
from datetime import timedelta

import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)  # Reproducibility - same data every run
Faker.seed(42)

# 1. GENERATE 500 CUSTOMERS

city_state_pairs = [
    ('New York', 'NY'), ('Brooklyn', 'NY'), ('Buffalo', 'NY'),
    ('Los Angeles', 'CA'), ('San Francisco', 'CA'), ('San Diego', 'CA'),
    ('Chicago', 'IL'), ('Springfield', 'IL'),
    ('Houston', 'TX'), ('Austin', 'TX'), ('Dallas', 'TX'),
    ('Phoenix', 'AZ'), ('Tucson', 'AZ'),
    ('Philadelphia', 'PA'), ('Pittsburgh', 'PA'),
    ('Miami', 'FL'), ('Orlando', 'FL'), ('Tampa', 'FL'),
    ('Seattle', 'WA'), ('Boston', 'MA'), ('Denver', 'CO'),
    ('Atlanta', 'GA'), ('Portland', 'OR'), ('Las Vegas', 'NV')
]

customers = []
for i in range(1, 501):
    city, state = random.choice(city_state_pairs)
    signup_date = fake.date_between(start_date='-2y', end_date='today')

    customers.append({
        'customer_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.unique.email(),
        'city': city,
        'state': state,
        'signup_date': signup_date,
    })

df_customers = pd.DataFrame(customers)


# 2. GENERATE 100 PRODUCTS


categories = {
    'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Keyboard', 'Mouse', 'Tablet', 'Smartwatch'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Dress', 'Hoodie', 'Shorts', 'Socks'],
    'Home & Garden': ['Coffee Maker', 'Blender', 'Plant Pot', 'Lamp', 'Rug', 'Pillow', 'Curtains', 'Vase'],
    'Sports': ['Yoga Mat', 'Dumbbell Set', 'Bicycle', 'Tennis Racket', 'Basketball', 'Baseball Bat', 'Resistance Bands'],
    'Books': ['Novel', 'Cookbook', 'Self-Help Book', 'Biography', 'Science Fiction', 'History Book', 'Comic Book']
}

variants = ['Basic', 'Standard', 'Premium']


all_products = []

for category, base_names in categories.items():
    for base_name in base_names:
        for variant in variants:
            product_name = f"{variant} {base_name}"

            cost = round(random.uniform(10, 200), 2)
            price = round(cost * random.uniform(1.4, 2.5), 2)

            all_products.append({
                'product_name': product_name,
                'category': category,
                'price': price,
                'cost': cost
            })

# Randomly sample exactly 100 unique products
selected_products = random.sample(all_products, 100)

# Assign product_id sequentially
products = []
for i, product in enumerate(selected_products, start=1):
    product['product_id'] = i
    products.append(product)

df_products = pd.DataFrame(products)

# 3. GENERATE 2000 ORDERS

orders = []
for i in range(1, 2001):
    customer = random.choice(customers)
    customer_id = customer['customer_id']
    signup_date = customer['signup_date']

    # Order date MUST be after signup date
    order_date = fake.date_between(start_date=signup_date, end_date='today')

    # 90% completed, 10% cancelled
    order_status = random.choices(['Completed', 'Cancelled'], weights=[90, 10])[0]

    orders.append({
        'order_id': i,
        'customer_id': customer_id,
        'order_date': order_date,
        'order_status': order_status
    })

df_orders = pd.DataFrame(orders)

# 4. GENERATE ORDER_ITEMS

order_items = []
order_item_id = 1

for order in orders:
    order_id = order['order_id']

    # Each order has 1-5 line items
    num_items = random.randint(1, 5)

    # Pick random products (no duplicates in same order)
    selected_products = random.sample(products, min(num_items, len(products)))

    for product in selected_products:
        product_id = product['product_id']
        base_price = product['price']

        # 20% chance of discount
        if random.random() < 0.2:
            unit_price = round(base_price * random.uniform(0.7, 0.9), 2)
        else:
            unit_price = base_price

        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]

        order_items.append({
            'order_item_id': order_item_id,
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price
        })
        order_item_id += 1

df_order_items = pd.DataFrame(order_items)

# 5. GENERATE RETURNS

# Build set of completed order IDs (efficient lookup)
completed_order_ids = {
    order['order_id'] for order in orders
    if order['order_status'] == 'Completed'
}

# Filter order_items to only completed orders
completed_order_items = [
    item for item in order_items
    if item['order_id'] in completed_order_ids
]

# 15% of completed order items get returned
num_returns = int(len(completed_order_items) * 0.15)
items_to_return = random.sample(completed_order_items, num_returns)

return_reasons = [
    'Defective product',
    'Wrong item received',
    'Changed mind',
    'Better price elsewhere',
    'Item not as described',
    'Arrived too late',
    'No longer needed',
    'Quality not as expected'
]

returns = []
return_id = 1

# Build order_date lookup dictionary
order_date_lookup = {
    order['order_id']: order['order_date']
    for order in orders
}

for item in items_to_return:
    order_item_id = item['order_item_id']
    order_id = item['order_id']
    quantity_ordered = item['quantity']

    # Get order date efficiently
    order_date = order_date_lookup[order_id]

    # Returns happen 1-30 days after order, but NOT in the future
    max_return_date = min(
        pd.to_datetime(order_date) + timedelta(days=30),
        pd.to_datetime('today')
    )

    # Random date between order_date and max_return_date
    days_diff = (max_return_date - pd.to_datetime(order_date)).days

    # Skip return if it can't logically happen yet (order too recent)
    if days_diff <= 0:
        continue

    return_date = pd.to_datetime(order_date) + timedelta(days=random.randint(1, days_diff))

    # Return partial or full quantity
    if quantity_ordered > 1:
        return_quantity = random.randint(1, quantity_ordered)
    else:
        return_quantity = 1

    returns.append({
        'return_id': return_id,
        'order_item_id': order_item_id,
        'return_quantity': return_quantity,
        'return_date': return_date,
        'return_reason': random.choice(return_reasons)
    })
    return_id += 1

df_returns = pd.DataFrame(returns)

# 6. SAVE TO CSV

df_customers.to_csv('customers.csv', index=False)
df_products.to_csv('products.csv', index=False)
df_orders.to_csv('orders.csv', index=False)
df_order_items.to_csv('order_items.csv', index=False)
df_returns.to_csv('returns.csv', index=False)

print(f"Generated:")
print(f"  - {len(customers)} customers")
print(f"  - {len(products)} products")
print(f"  - {len(orders)} orders ({df_orders[df_orders['order_status']=='Completed'].shape[0]} completed, {df_orders[df_orders['order_status']=='Cancelled'].shape[0]} cancelled)")
print(f"  - {len(order_items)} order items")
print(f"  - {len(returns)} returns")
