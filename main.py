import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8291703652:AAFJRqBXfTieoJIUcKFBHBi9My8GNUnpEF8"

IMAGES = {
    "desk_empty":            "https://files.catbox.moe/gxeb6p.jpg",
    "desk_toy":              "https://files.catbox.moe/hc05wj.jpg",
    "desk_plant":            "https://files.catbox.moe/p2jm1g.jpg",
    "desk_stationery":       "https://files.catbox.moe/zjsxr0.jpg",
    "desk_toy_plant":        "https://files.catbox.moe/25dfql.jpg",
    "desk_toy_stationery":   "https://files.catbox.moe/h4h629.jpg",
    "desk_plant_stationery": "https://files.catbox.moe/d12hnv.jpg",
    "desk_all_items":        "https://files.catbox.moe/nw9kag.jpg",
    "computer_password":     "https://files.catbox.moe/qzbiiu.jpg",
    "analytics_dashboard":   "https://files.catbox.moe/7st7is.jpg",
    "desk_mess":             "https://files.catbox.moe/1tnaze.jpg",
    "vending_machine":       "https://files.catbox.moe/zfeks4.jpg",
    "blurred_word":          "https://files.catbox.moe/qmg0dk.jpg",
    "celebration":           "https://files.catbox.moe/7akb49.jpg",
}

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Game(StatesGroup):
    desk = State()
    password = State()
    analytics = State()
    creative = State()
    mess = State()
    finance = State()
    lunch = State()
    lunch_task = State()
    blurred = State()
    logic = State()


def get_desk_image(items: list) -> str:
    s = set(items)
    if s == {"toy"}:                        return IMAGES["desk_toy"]
    if s == {"plant"}:                      return IMAGES["desk_plant"]
    if s == {"stationery"}:                 return IMAGES["desk_stationery"]
    if s == {"toy", "plant"}:               return IMAGES["desk_toy_plant"]
    if s == {"toy", "stationery"}:          return IMAGES["desk_toy_stationery"]
    if s == {"plant", "stationery"}:        return IMAGES["desk_plant_stationery"]
    if s == {"toy", "plant", "stationery"}: return IMAGES["desk_all_items"]
    return IMAGES["desk_empty"]

def desk_keyboard(items: list) -> InlineKeyboardMarkup:
    buttons = []
    if "toy" not in items:
        buttons.append([InlineKeyboardButton(text="🧸", callback_data="toy")])
    if "plant" not in items:
        buttons.append([InlineKeyboardButton(text="🌿", callback_data="plant")])
    if "stationery" not in items:
        buttons.append([InlineKeyboardButton(text="✏️", callback_data="stationery")])
    buttons.append([InlineKeyboardButton(text="🚀 К работе!", callback_data="work")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer_photo(
        photo=IMAGES["desk_empty"],
        caption="👋 Добро пожаловать в ОТП Банк!\n"
                "Сегодня твой первый день стажировки.\n"
                "Давай обустроим рабочее место 😉",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🚀 Старт", callback_data="start_game")]]
        )
    )


@dp.callback_query()
async def callbacks(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    current_state = await state.get_state()

    if data == "restart":
        await state.clear()
        await call.message.delete()
        await start(call.message, state)
        await call.answer()
        return

    if data == "start_game":
        await state.set_state(Game.desk)
        await state.update_data(items=[])
        await call.message.delete()
        await call.message.answer_photo(
            photo=IMAGES["desk_empty"],
            caption="Выбери, что добавить на стол:",
            reply_markup=desk_keyboard([])
        )
        await call.answer()
        return

    if current_state == Game.desk.state:
        user_data = await state.get_data()
        items = user_data.get("items", [])

        if data in ["toy", "plant", "stationery"] and data not in items:
            items.append(data)
            await state.update_data(items=items)

        if data == "work" or set(items) == {"toy", "plant", "stationery"}:
            await state.set_state(Game.password)
            await call.message.delete()
            await call.message.answer_photo(
                photo=IMAGES["desk_all_items"],
                caption="✨ Красота! Теперь приступаем к работе.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="💻 К компьютеру", callback_data="to_computer")]]
                )
            )
            await call.answer()
            return

        await call.message.delete()
        await call.message.answer_photo(
            photo=get_desk_image(items),
            caption="✨ Отличный выбор! Добавим ещё что-нибудь или сразу к работе?",
            reply_markup=desk_keyboard(items)
        )
        await call.answer()
        return

    if data == "to_computer":
        await call.message.delete()
        await call.message.answer_photo(
            photo=IMAGES["computer_password"],
            caption="💻 Рабочий компьютер ждёт тебя.\n"
                    "Введи пароль, чтобы приступить к задачам."
        )
        await call.answer()
        return

    if current_state == Game.analytics.state:
        if data == "C":
            await state.set_state(Game.creative)
            await call.message.delete()
            await call.message.answer(
                "🎨 Креативная команда запускает рекламную кампанию.\n"
                "Помоги выбрать корректный и законный слоган.\n\n"
                "A) «Карта без условий — деньги просто так!»\n"
                "B) «ОТП Карта — кэшбэк до 35% с прозрачными условиями»\n"
                "C) «Гарантированный доход каждому»\n"
                "D) «ОТП Банк — номер 1 в стране»",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=l, callback_data=l)] for l in ["A", "B", "C", "D"]]
                )
            )
        else:
            await call.answer("Попробуй ещё раз 😉")
        return

    if current_state == Game.creative.state:
        if data == "B":
            await state.set_state(Game.mess)
            await call.message.delete()
            await call.message.answer_photo(
                photo=IMAGES["desk_mess"],
                caption="😅 Ого, что тут произошло?\n"
                        "Наведи порядок на столе и посчитай, каких предметов больше.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=i)]
                                     for i in ["Скрепки", "Карточки", "Печати", "Флешки"]]
                )
            )
        else:
            await call.answer("Этот вариант может нарушать закон о рекламе или вводить в заблуждение.")
        return

    if current_state == Game.mess.state:
        if data == "Скрепки":
            await state.set_state(Game.finance)
            await call.message.delete()
            await call.message.answer(
                "💰 Финансовый отдел на связи.\n\n"
                "Клиент открыл вклад на 200 000 ₽ под 8% годовых.\n"
                "Сколько он заработает за 1 год?",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=t)]
                                     for t in ["8000", "16000", "20000", "24000"]]
                )
            )
        else:
            await call.answer("Попробуй ещё раз 😉")
        return

    if current_state == Game.finance.state:
        if data == "16000":
            await state.set_state(Game.lunch)
            await call.message.delete()
            await call.message.answer_photo(
                photo=IMAGES["vending_machine"],
                caption="⏰ Половина дня позади — пора на перерыв.\n"
                        "Что выберешь на обед?",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=t)]
                                     for t in ["🥤 Газировка", "🥪 Сэндвич", "🍫 Батончик", "🍙 Онигири"]]
                )
            )
        else:
            await call.answer("Неверно 😉")
        return

    if current_state == Game.lunch.state:
        await state.set_state(Game.lunch_task)
        await call.message.delete()
        await call.message.answer(
            "Пока ждёшь заказ — мини-задача.\n\n"
            "В автомате 12 напитков и 8 снеков.\n"
            "Какова вероятность случайно выбрать напиток?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=t)]
                                 for t in ["40%", "50%", "60%", "70%"]]
            )
        )
        await call.answer()
        return

    if current_state == Game.lunch_task.state:
        if data == "60%":
            await state.set_state(Game.blurred)
            await call.message.delete()
            await call.message.answer_photo(
                photo=IMAGES["blurred_word"],
                caption="📊 Помогай!\n\n"
                        "В презентации по запуску нового продукта одно ключевое слово оказалось размыто.\n"
                        "Напиши его:"
            )
        else:
            await call.answer("Попробуй ещё раз 😉")
        return

    if current_state == Game.logic.state:
        if data == "Мария":
            await call.message.delete()
            await call.message.answer_photo(
                photo=IMAGES["celebration"],
                caption="🎉 Классная работа!\n\n"
                        "Ты прошёл свой первый день в ОТП Банке — "
                        "попробовал себя в аналитике, финансах, маркетинге и логике."
            )
            await call.message.answer(
                "А теперь самое интересное 👇\n\n"
                "В ОТП Банке открыты стажировки по разным направлениям:\n"
                "— аналитика и финансы\n"
                "— маркетинг и digital\n"
                "— IT и разработка\n"
                "— риски и аудит\n"
                "— клиентский сервис и другие команды.\n\n"
                "Мы ищем внимательных, инициативных и любопытных — возможно, именно тебя 😉\n\n"
                "🚀 Переходи по ссылке, выбирай направление и подавай заявку.\n"
                "Стань частью команды ОТП и начни строить карьеру уже сейчас!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🚀 Подать заявку", url="https://t.me/otplifestyle")],
                        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart")]
                    ]
                )
            )
            await state.clear()
        else:
            await call.answer("Подумай ещё раз 😉")
        return


@dp.message(Game.password)
async def check_password(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == "отп":
        await state.set_state(Game.analytics)
        await message.answer("🔓 Доступ открыт. Начинаем!")
        await message.answer_photo(
            photo=IMAGES["analytics_dashboard"],
            caption="📊 Отдел аналитики на связи!\n\n"
                    "Мы сравниваем три кредита.\n"
                    "Какой из них принесёт банку наибольший процентный доход за год?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="A", callback_data="A")],
                    [InlineKeyboardButton(text="B", callback_data="B")],
                    [InlineKeyboardButton(text="C", callback_data="C")],
                    [InlineKeyboardButton(text="Доход
