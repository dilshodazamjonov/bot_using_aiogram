from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import *

def send_contact_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Поделиться контактом', request_contact=True)]],
        resize_keyboard=True
    )


def generate_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='✅ Сделать заказ')],
        [KeyboardButton(text='📒 История')],[KeyboardButton(text='🧺 Корзина')],[KeyboardButton(text='⚙️ Настройки')]
    ], resize_keyboard=True)



def generate_category_menu():
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    markup.inline_keyboard.append(
        [InlineKeyboardButton(text='Всё меню', url='https://telegra.ph/Vkusnyaha-Fast-Food-12-29')]
    )

    categories = get_all_categories()

    row = []
    for i, category in enumerate(categories):
        button = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        row.append(button)

        if len(row) == 2:
            markup.inline_keyboard.append(row)
            row = []

    if row:
        markup.inline_keyboard.append(row)

    return markup

def generate_products_by_category(category_id):
    mark_up = InlineKeyboardMarkup(inline_keyboard=[])

    products = get_products_by_category(category_id)

    row = []
    for i, product in enumerate(products):
        button = InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}')
        row.append(button)

        if len(row) == 2:
            mark_up.inline_keyboard.append(row)
            row = []
    if row:
        mark_up.inline_keyboard.append(row)
    mark_up.inline_keyboard.append(
        [InlineKeyboardButton(text='🔙 Назад', callback_data='main_menu')]
    )
    return mark_up


def generate_product_detail_menu(product_id, category_id, cart_id, product_name='', c=0):
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    try:
        quantity = get_quantity(cart_id, product_name)
    except:
        quantity = c

    # Create buttons
    btn_minus = InlineKeyboardButton(text='➖', callback_data=f'minus_{quantity}_{product_id}')
    btn_quantity = InlineKeyboardButton(text=str(quantity), callback_data='coll')
    btn_plus = InlineKeyboardButton(text='➕', callback_data=f'plus_{quantity}_{product_id}')

    # Add the buttons to the inline_keyboard list
    markup.inline_keyboard.append([btn_minus, btn_quantity, btn_plus])

    # Add the other buttons
    markup.inline_keyboard.append(
        [InlineKeyboardButton(text='Добавить в корзину', callback_data=f'cart_{product_id}_{quantity}')])
    markup.inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data=f'back_{category_id}')])

    return markup


def generate_cart_menu(cart_id):
    # Initialize InlineKeyboardMarkup with an empty list for inline_keyboard
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    # Add the "Place Order" button
    markup.inline_keyboard.append(
        [InlineKeyboardButton(text='Оформить заказ', callback_data=f'order_{cart_id}')]
    )

    # Fetch products in the cart
    cart_products = get_cart_products_for_delete(cart_id)

    for cart_product_id, product_id in cart_products:
        # Fetch the product name
        product_name = get_product_name(product_id)
        # Add a delete button for each product
        markup.inline_keyboard.append(
            [InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{cart_product_id}')]
        )

    return markup


















