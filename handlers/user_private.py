from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_clothes
from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет, я бот самого лучшего магазина! Помогу с выбором вещей и их заказом!"
        " Для того, чтобы войти в режим администратора введи секретную команду",
        reply_markup=get_keyboard(
            "Каталог",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            placeholder="Что вас интересует?",
            sizes=(2, 2)
        ),
    )


@user_private_router.message(or_f(Command("catalog"), (F.text.lower() == "каталог")))
async def catalog_cmd(message: types.Message, session: AsyncSession):
    await message.answer("Вот каталог:")
    for cloth in await orm_get_clothes(session):
        await message.answer_photo(
            cloth.image,
            caption=f"<strong>{cloth.name}\
                            </strong>\n{cloth.description}\nСтоимость: {round(cloth.price, 2)}",
        )


@user_private_router.message(F.text.lower() == "о магазине")
@user_private_router.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(F.text.lower() == "варианты оплаты")
@user_private_router.message(Command("payment"))
async def payment_cmd(message: types.Message):
    text = as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте (доставка почтой)",
        "При получении товара картой (доставка курьером)",
        "При получении товара наличными (доставка курьером)",
        "В магазине картой/наличными",
        marker="✅ ",
    )
    await message.answer(text.as_html())


@user_private_router.message(
    (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки"))
@user_private_router.message(Command("shipping"))
async def menu_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            Bold("Варианты получения товаров:"),
            "Курьер",
            "Самовывоз из магазина",
            "Доставка через почту",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Нельзя:"),
            "Голуби",
            marker="❌ "
        ),
        sep="\n----------------------\n",
    )
    await message.answer(text.as_html())