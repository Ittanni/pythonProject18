from sqlalchemy.ext.asyncio import AsyncSession
from database.models import ItemClothing
from sqlalchemy import select, update, delete


async def orm_add_cloth(session: AsyncSession, data: dict):
    obj = ItemClothing(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
    )
    session.add(obj)
    await session.commit()


async def orm_get_clothes(session: AsyncSession):
    query = select(ItemClothing)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_cloth(session: AsyncSession, cloth_id: int):
    query = select(ItemClothing).where(ItemClothing.id == cloth_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_cloth(session: AsyncSession, cloth_id: int, data):
    query = update(ItemClothing).where(ItemClothing.id == cloth_id).values(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"], )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, cloth_id: int):
    query = delete(ItemClothing).where(ItemClothing.id == cloth_id)
    await session.execute(query)
    await session.commit()
