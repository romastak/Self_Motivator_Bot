from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert
from models import User, UserTemplates, TemplateCrit, TemplateMnoj, async_session, AsyncSessionLocal
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Integer


async def save_user_template(telegram_id: int, username: str, template_name: str, key_for_generating: str, crits: list, mnojs: list):
    async with async_session() as session:
        async with session.begin():
            # Проверка существования пользователя в базе
            user_stmt = select(User).where(User.tg_id == telegram_id)
            result = await session.execute(user_stmt)
            user = result.scalars().first()

            if not user:
                # Если пользователя нет в базе, нужно его создать
                new_user = User(tg_id=telegram_id, username=username)  # username можно взять из другого места
                session.add(new_user)
                await session.flush()  # Получаем ID пользователя
                user_id = new_user.id
            else:
                user_id = user.id

            # Сохранение шаблона в таблицу user_templates
            new_template = UserTemplates(
                user_id=user_id,
                template_name=template_name,
                key_for_generating=key_for_generating
            )
            session.add(new_template)
            await session.flush()  # Получаем ID шаблона

            # Сохранение критериев
            for crit in crits:
                new_crit = TemplateCrit(
                    user_template_id=new_template.id,
                    crit_name=crit['name'],
                    crit_score=crit['score'],
                    crit_comment=crit['comment']
                )
                session.add(new_crit)

            # Сохранение множителей
            for mnoj in mnojs:
                new_mnoj = TemplateMnoj(
                    user_template_id=new_template.id,
                    mnoj_name=mnoj['name'],
                    mnoj_score=mnoj['score'],
                    mnoj_comment=mnoj['comment']
                )
                session.add(new_mnoj)

        await session.commit()  # Сохранение всех изменений


async def get_all_telegram_ids() -> list[int]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User.tg_id))
            telegram_ids = [row[0] for row in result.fetchall()]
    return telegram_ids


async def get_user_templates(telegram_id) -> list[int]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user_id = await session.execute(
                select(User.tg_id).filter_by(tg_id=telegram_id)
            )
            result = await session.execute(
                select(UserTemplates.template_name).filter_by(user_id=user_id)
            )
            user_templ = [row[0] for row in result.fetchall()]
    return user_templ # TODO need to ended. result in chat gpt in this branch