import sqlite3


def create_user_table():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    telegram_id BIGINT NOT NULL UNIQUE,
    phone TEXT
    );
    ''')


create_user_table()


def create_cart_tabel():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carts(
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id),
    total_price DECIMAL(12, 2) DEFAULT 0,
    total_products INTEGER DEFAULT 0
    );
    ''')


create_cart_tabel()


def create_cart_products_table():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_products (
                cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cart_id INTEGER NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE ON UPDATE CASCADE,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0), 
                final_price REAL NOT NULL CHECK(final_price >= 0),
                UNIQUE(product_id, cart_id)
            );
        ''')
        database.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        database.close()



create_cart_products_table()


def create_categories_table():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(30) NOT NULL UNIQUE
    );
    ''')
create_categories_table()


def insert_into_categories():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO categories(category_name) VALUES
        ('Лаваш'), 
        ('Донары'), 
        ('Бургеры'), 
        ('Хот-доги'), 
        ('Напитки'), 
        ('Соусы') 
        ''')
    database.commit()
    database.close()

# insert_into_categories()

def create_products_table():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products(
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name VARCHAR(50) NOT NULL UNIQUE,
        price DECIMAL(12, 2) NOT NULL,
        description VARCHAR(200),
        image TEXT,
        category_id INTEGER NOT NULL,
        FOREIGN KEY(category_id) REFERENCES category(category_id)
        );
        ''')
create_products_table()

def insert_into_products():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO products(category_id, product_name, price, description, image) VALUES
    (1, 'Лаваш говяжий с сыром', 30000, 'Мясо, огурчики, сыр, чипсы', 
    '.media/lavash/lavash_3.jpg'),
    (1, 'Лаваш говяжий', 28000, 'Мясо, огурчики, помидоры, чипсы', 
    '.media/lavash/lavash_3.jpg'),
    (1, 'Лаваш куриный', 26000, 'Мясо, огурчики, сыр, чипсы, помидоры', 
    '.media/lavash/lavash_3.jpg')
    ''')
    database.commit()
    database.close()

# insert_into_products()

def first_select_user(chat_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE telegram_id = ?
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()
    return user

def first_register_user(chat_id, full_name):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
       INSERT INTO users(telegram_id, full_name) VALUES(?, ?)   
    ''', (chat_id, full_name))
    database.commit()
    database.close()


def update_user_to_finish_register(chat_id, phone):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        UPDATE  users SET phone = ? WHERE telegram_id = ?
    ''', (phone, chat_id))
    database.commit()
    database.close()


def insert_into_cart(chat_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO carts(user_id) VALUES
        (
        (SELECT * FROM users WHERE telegram_id = ?)
        )
    ''', (chat_id,))
    database.commit()
    database.close()

def get_all_categories():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM categories
    ''')
    categories = cursor.fetchall()
    database.close()
    return categories

def get_products_by_category(category_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_id, product_name FROM products WHERE category_id = ?
    ''', (category_id,))
    products = cursor.fetchall()
    database.close()
    return products


def get_product_detail(product_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM products WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    database.close()
    return product


def get_cart_id(chat_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_id FROM carts 
    WHERE user_id = (
        SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))
    cart_id = cursor.fetchone()[0]
    database.close()
    return cart_id

def get_quantity(cart, product):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT quantity FROM cart_products WHERE cart_id = ? AND product_id = ?
    ''', (cart, product))
    quantity = cursor.fetchone()[0]
    database.close()
    return quantity


def insert_or_update_cart_product(cart_id, product_id, quantity, final_price):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
            INSERT INTO cart_products(cart_id, product_id, quantity, final_price) VALUES (?, ?, ?, ?)
        ''', (cart_id, product_id, quantity, final_price))
        database.commit()
        return True
    except:
        cursor.execute('''
            UPDATE cart_products
            SET quantity = ?,
            final_price = ?
            WHERE product_id= ? AND cart_id = ?
        ''', (quantity, final_price, product_id, cart_id))
        database.commit()
        return False
    finally:
        database.close()


def update_total_product_total_price(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
            UPDATE carts 
            SET 
                total_products = (
                    SELECT COALESCE(SUM(quantity), 0) 
                    FROM cart_products 
                    WHERE cart_id = :cart_id
                ),
                total_price = (
                    SELECT COALESCE(SUM(final_price), 0) 
                    FROM cart_products 
                    WHERE cart_id = :cart_id
                )
            WHERE cart_id = :cart_id
        ''', {'cart_id': cart_id})
        database.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        database.close()


def get_user_cart_product(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_id, quantity, final_price
    FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products

def get_product_and_price(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT total_products, total_price
        FROM carts WHERE cart_id = ?
        ''', (cart_id,))
    total_products, total_price = cursor.fetchone()
    database.close()
    return total_products, total_price

def get_product_name(product_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT product_name FROM products WHERE product_id = ?
    ''',(product_id,))
    product_name = cursor.fetchone()[0]
    database.close()
    return product_name

def get_cart_products_for_delete(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_product_id, product_id FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products


def delete_product_from_cart(cart_product_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        DELETE FROM cart_products WHERE cart_product_id = ?
    ''', (cart_product_id,))
    database.commit()
    database.close()

def drop_cart_products_default(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        DELETE FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    database.commit()
    database.close()

def order_total_price():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders_total_price(
            order_total_price_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER REFERENCES carts(cart_id),
            total_price DECIMAL(12, 2) DEFAULT 0,
            total_products INTEGER DEFAULT 0,
            time_now TEXT,
            new_date TEXT
        );
    ''')
    database.commit()
    database.close()

def order():
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders(
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_total_price_id INTEGER REFERENCES orders_total_price(order_total_price_id),
        product_name VARCHAR(100) NOT NULL,
        quantity INTEGER NOT NULL,
        final_price DECIMAL(12, 2) NOT NULL
    );
    ''')
    database.commit()
    database.close()

order_total_price()
order()

def save_order_total(cart_id, total_products, total_price, time_now, new_date):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO orders_total_price(cart_id, total_price, total_products, time_now, new_date) VALUES(?, ?, ?, ?, ?)
    ''', (cart_id, total_price, total_products, time_now, new_date))
    database.commit()
    database.close()

def order_total_price_id(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT order_total_price_id FROM orders_total_price WHERE cart_id = ?
    ''',    (cart_id,))
    order_total_id = cursor.fetchall()[-1][0]
    database.close()
    return order_total_id

def save_order(order_total_id, product_name, quantity, final_price):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
            INSERT INTO orders(order_total_price_id, product_name, quantity, final_price) VALUES(?, ?, ?, ?)
    ''', (order_total_id, product_name, quantity, final_price))
    database.commit()
    database.close()


def get_orders_total_price(cart_id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT * FROM orders_total_price WHERE cart_id = ? 
    ''', (cart_id,))
    order_price = cursor.fetchall()
    database.close()
    return order_price

def get_detail_product(id):
    database = sqlite3.connect('telegram_bot.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT product_name, quantity, final_price FROM orders WHERE order_total_price_id = ?
    ''', (id,))
    detail_product = cursor.fetchall()
    database.close()
    return detail_product

