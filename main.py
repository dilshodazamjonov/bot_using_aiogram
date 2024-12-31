import asyncio
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.filters import Filter
from pyexpat.errors import messages
from datetime import datetime
from database import *
from keyboards import *


TOKEN = '' # telegram token that is given by BotFather
PAYMENT = '' # Whatever the paying platform you choose, gives you testing or real token so you put it here
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f'Здравствуйте {message.from_user.full_name}. Вас приветствует бот вкусняха')
    await register_user(message)

async def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = first_select_user(chat_id)
    if user:
        await message.answer('Авторизация прошла успешно')
        await show_main_menu(message)# Insertion of function of main menu
    else:
        first_register_user(chat_id, full_name)
        await message.answer('Для регистрации поделитесь контактом', reply_markup=send_contact_button())

@dp.message(F.contact)
async def finish_register(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    update_user_to_finish_register(chat_id, phone)
    await create_cart_for_user(message)
    await message.answer('Регистрация прошла успешно')
    await show_main_menu(message)


async def create_cart_for_user(message: Message):
    chat_id = message.chat.id

    try:
        insert_into_cart(chat_id)
    except:
        pass

async def show_main_menu(message: Message):
    await message.answer('Выберите направление: ', reply_markup=generate_main_menu())

# @dp.message(regexp=r'✅ Сделать заказ')
@dp.message(lambda message: message.text and '✅ Сделать заказ' in message.text)
async def make_order(message: Message):
    await message.answer('Выберите категорию', reply_markup=generate_category_menu())


@dp.callback_query(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    await bot.edit_message_text(
        text='Выберите продукт:',
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=generate_products_by_category(category_id)
    )
@dp.callback_query(lambda call: 'main_menu' in call.data)
async def return_to_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                text='Выберите категорию', reply_markup=generate_category_menu())

@dp.callback_query(lambda call: 'product' in call.data)
async def show_product_detail(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product_id = int(product_id)
    product = get_product_detail(product_id)
    cart_id = get_cart_id(chat_id)
    try:
        quantity = get_quantity(cart_id, product[0])
        if quantity is None:
            quantity = 0
    except:
        quantity = 0

    await bot.delete_message(chat_id, message_id)
    await bot.send_photo(chat_id=chat_id, photo='https://sun9-10.userapi.com/impg/ifav6mvUDR4SW3vAy91ZetTQueYcpS3aHb7o7A/Ms7uaiibcAo.jpg?size=1200x675&quality=95&sign=8aa44fb751a57035856220bd791a651c&c_uniq_tag=fRFEoTtFd6VJ8j2b2jNEKXHefua2JVsw9NSsx05RrRI&type=album',
                         caption=f'''
    {product[1]}

Ингредиенты: {product[3]}

Цена: {product[2]}
    ''', reply_markup=generate_product_detail_menu(product_id=product_id, category_id=product[-1],
                                                   cart_id=cart_id, product_name=product[1], c=quantity))


@dp.callback_query(lambda call: 'back' in call.data)
async def back_to_category(call: CallbackQuery):
    chat_id = call.message.chat.id
    messages_id = call.message.message_id
    _, category_id = call.data.split('_')
    await bot.delete_message(chat_id=chat_id, message_id=messages_id)
    await bot.send_message(chat_id=chat_id, text='Выберите продукт', reply_markup=generate_products_by_category(category_id))



@dp.callback_query(lambda call: 'plus' in call.data)
async def add_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    messages_id = call.message.message_id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    quantity += 1
    product = get_product_detail(product_id)
    card_id = get_cart_id(chat_id)
    await bot.edit_message_caption(chat_id=chat_id, message_id=messages_id,
                                   caption=f'''{product[1]}
                                       
Ингредиенты: {product[3]}

Цена: {product[2]}''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                           category_id=product[-1],
                                           cart_id=card_id,
                                           product_name=product[1],
                                           c=quantity))

@dp.callback_query(lambda call: 'minus' in call.data)
async def remove_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    product = get_product_detail(product_id)
    cart_id = get_cart_id(chat_id)

    if quantity <= 1:
        await bot.answer_callback_query(call.id, 'Ниже нуля нельзя')
        return
    else:
        quantity -= 1

    new_caption = f'''{product[1]}

Ингредиенты: {product[3]}

Цена: {product[2]}'''
    new_reply_markup = generate_product_detail_menu(
        product_id=product_id,
        category_id=product[-1],
        cart_id=cart_id,
        product_name=product[1],
        c=quantity
    )
    if call.message.caption != new_caption or call.message.reply_markup != new_reply_markup:
        await bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=new_caption,
            reply_markup=new_reply_markup
        )

@dp.callback_query(lambda call: 'cart' in call.data)
async def add_chosen_product_to_card(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)
    cart_id = get_cart_id(chat_id)
    product = get_product_detail(product_id)
    final_price = product[2] * quantity

    if insert_or_update_cart_product(cart_id, product[0], quantity, final_price):
        await bot.answer_callback_query(call.id, text='Продукт успешно добавлен')
    else:
        await bot.answer_callback_query(call.id, 'Количество успешно изменено')


@dp.message(lambda mess: mess.text and '🧺 Корзина' in mess.text)
async def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    cart_id = get_cart_id(chat_id)

    try:
        update_total_product_total_price(cart_id)
    except Exception as e:
        await message.answer('Корзина недоступна. Обратитесь в тех поддержку')
        return

    cart_products = get_user_cart_product(cart_id)
    total_products, total_price = get_product_and_price(cart_id)

    text = 'Ваша корзина \n\n'

    i = 0
    for product_id, quantity, final_price in cart_products:
        i += 1
        product_name = get_product_name(product_id)
        text += f'''{i}. {product_name}
Количество: {quantity},
Общая стоимость: {final_price}\n\n'''

    text += f'''Общее количество продуктов: {0 if total_products is None else total_products}
Общая стоимость заказа: {0 if total_price is None else total_price}'''

    if edit_message:
        await  bot.edit_message_text(text=text, chat_id=chat_id, message_id=message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=generate_cart_menu(cart_id))

@dp.callback_query(lambda call: 'delete' in call.data)
async def delete_cart_products(call: CallbackQuery):
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)
    message = call.message
    delete_product_from_cart(cart_product_id)

    await bot.answer_callback_query(call.id, text='Продукт успешно удален')
    await show_cart(message, edit_message=True)

@dp.callback_query(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id

    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)

    time_now = datetime.now().strftime('%H:%M')
    new_date = datetime.now().strftime('%d:%m:%y')

    cart_products = get_user_cart_product(cart_id)
    total_products, total_price = get_product_and_price(cart_id)

    save_order_total(cart_id, total_products, total_price, time_now, new_date)
    order_total_id = order_total_price_id(cart_id)

    text = 'Ваша корзина:\n\n'

    for i, (product_id, quantity, final_price) in enumerate(cart_products, start=1):
        product_name = get_product_name(product_id)
        text += f"{i}. {product_name}\nКоличество: {quantity},\nОбщая стоимость: {final_price}\n\n"

        save_order(order_total_id, product_name, quantity, final_price)
    text += f"Общее количество продуктов: {0 if total_products is None else total_products}\n"
    text += f"Общая стоимость заказа: {0 if total_price is None else total_price}00"

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Заказ №{cart_id}',
        description=text,
        payload=f'order_{cart_id}',  # This can be dynamically defined for tracking orders
        provider_token=PAYMENT,  # Ensure `PAYMENT` is correctly set in your bot
        currency='UZS',
        prices=[
            LabeledPrice(label='Общая стоимость', amount=int(total_price)*100),
            LabeledPrice(label='Доставка', amount=1000000)
        ],
        start_parameter='start-parameter'
    )


# Pre-checkout query handler
@dp.pre_checkout_query()
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Ошибка, оплата не прошла')


# Successful payment handler
@dp.message(F.successful_payment)
async def get_payment(message: Message):
    chat_id = message.chat.id
    cart_id = get_cart_id(chat_id)
    await bot.send_message(chat_id, text='Оплата прошла успешно, ожидайте заказ')
    drop_cart_products_default(cart_id)


@dp.message(lambda message: message.text and '📒 История' in message.text)
async def show_history_orders(message: Message):
    chat_id = message.chat.id
    cart_id = get_cart_id(chat_id)
    order_price = get_orders_total_price(cart_id)
    for i in order_price:
        text = f'''Дата заказа: {i[-1]}
Время заказа: {i[-2]}
Общее количество: {i[3]}
Сумма счета: {i[2]}\n\n'''
        detail_products = get_detail_product(i[0])
        for j in detail_products:
            text += f'''Продукт: {j[0]}
Количество: {j[1]}
Общая стоимость: {j[2]}
'''
        await bot.send_message(chat_id, text)






async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())







