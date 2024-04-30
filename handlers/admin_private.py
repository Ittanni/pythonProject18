from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_cloth, orm_get_clothes
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]))

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    placeholder="Выберите действие",
    sizes=(2,),
)


@admin_router.message(Command("admin88"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def starring_at_product(message: types.Message, session: AsyncSession):
    await message.answer("ОК, вот список товаров")
    for cloth in await orm_get_clothes(session):
        await message.answer_photo(
            cloth.image,
            caption=f"<strong>{cloth.name}\
                            </strong>\n{cloth.description}\nСтоимость: {round(cloth.price, 2)}",
        )


# Код ниже для машины состояний (FSM)

class AddClothing(StatesGroup):
    # Шаги состояний
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddClothing:name': 'Введите название заново:',
        'AddClothing:description': 'Введите описание заново:',
        'AddClothing:price': 'Введите стоимость заново:',
        'AddClothing:image': 'Этот стейт последний, поэтому...',
    }


# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddClothing.name)


# Хендлер отмены и сброса состояния
@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddClothing.name:
        await message.answer('Предыдущего шага нет, или введите название товара или напишите "отмена"')
        return

    previous = None
    for step in AddClothing.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddClothing.texts[previous.state]}")
            return
        previous = step


# Ловим данные для состояние name и потом меняем состояние на description
@admin_router.message(AddClothing.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    # Здесь можно сделать какую либо дополнительную проверку
    # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
    # например:
    if len(message.text) >= 200:
        await message.answer("Название товара не должно превышать 200 символов. \n Введите заново")
        return

    await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddClothing.description)


# Хендлер для отлова некорректных вводов для состояния name
@admin_router.message(AddClothing.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст названия товара")


# Ловим данные для состояние description и потом меняем состояние на price
@admin_router.message(AddClothing.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите стоимость товара")
    await state.set_state(AddClothing.price)


# Хендлер для отлова некорректных вводов для состояния description
@admin_router.message(AddClothing.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст описания товара")


# Ловим данные для состояние price и потом меняем состояние на image
@admin_router.message(AddClothing.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except ValueError:
        await message.answer("Введите корректное значение цены")
        return

    await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddClothing.image)


# Хендлер для отлова некорректного ввода для состояния price
@admin_router.message(AddClothing.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите стоимость товара")


# Ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddClothing.image, F.photo)
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.update_data()
    try:
        await orm_add_cloth(session, data)
        await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer('Возникла ошибка добавления товара!', reply_markup=ADMIN_KB)
        await state.clear()


@admin_router.message(AddClothing.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото элемента одежды")
