import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from flask import Flask, request
from threading import Thread
import uuid

import config
import database as db
import free_kassa as fk

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

app = Flask(__name__)

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

class AddKeyStates(StatesGroup):
    waiting_for_key = State()

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать в AIR UC SHOP!\nВведите /buy чтобы купить ключ.")

@dp.message_handler(commands=["buy"])
async def buy_handler(message: types.Message):
    key_data = db.get_unused_key()
    if not key_data:
        await message.answer("Извините, сейчас нет доступных ключей.")
        return
    key_id, _ = key_data
    amount = 100  # Цена ключа
    order_id = str(uuid.uuid4())
    payment_url = fk.generate_payment_url(order_id, amount, "Покупка ключа", message.from_user.id)

    db.create_order(message.from_user.id, key_id, amount, "pending", order_id)

    await message.answer(f"Для оплаты перейдите по ссылке:\n{payment_url}")

@dp.message_handler(commands=["addkey"])
async def add_key_start(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    await message.answer("Отправьте ключ для добавления:")
    await AddKeyStates.waiting_for_key.set()

@dp.message_handler(state=AddKeyStates.waiting_for_key)
async def add_key_process(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("У вас нет доступа к этой команде.")
        await state.finish()
        return
    key_text = message.text.strip()
    db.add_key(key_text)
    await message.answer("Ключ успешно добавлен!")
    await state.finish()

@app.route("/pay_callback", methods=["POST"])
def pay_callback():
    data = request.form
    if not fk.check_signature(data):
        return "bad sign"

    out_summ = data.get("OutSum")
    inv_id = data.get("InvId")
    order = db.get_order_by_invoice(inv_id)
    if not order:
        return "order not found"

    db.update_order_status(inv_id, "paid")
    key_id = order[2]
    db.mark_key_used(key_id)

    user_id = order[1]
    # Чтобы отправить сообщение из Flask - используем loop
    import asyncio
    async def send_key():
        key_data = db.get_unused_key()
        await bot.send_message(user_id, f"Спасибо за оплату!\nВаш ключ:\n{key_data[1]}")

    asyncio.run(send_key())
    return "OK"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    db.create_tables()
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
