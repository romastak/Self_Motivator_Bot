from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, delete
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


async def get_user_templates(telegram_id: int) -> list[str]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()  # Извлекаем единственное значение (user_id)

            if user_id:
                # Получаем все шаблоны пользователя
                result = await session.execute(
                    select(UserTemplates.template_name).filter_by(user_id=user_id)
                )
                # Преобразуем результат в список
                user_templ = [row[0] for row in result.fetchall()]
            else:
                user_templ = []  # Если пользователь не найден, возвращаем пустой список

    return user_templ

async def delete_user_template(telegram_id: int, template_name: str) -> bool:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()  # Извлекаем единственное значение (user_id)

            if not user_id:
                return False  # Если пользователь не найден, возвращаем False

            # Получаем шаблон по имени и user_id
            template_stmt = select(UserTemplates).filter_by(user_id=user_id, template_name=template_name)
            result = await session.execute(template_stmt)
            template = result.scalars().first()

            if not template:
                return False  # Если шаблон не найден, возвращаем False

            # Удаляем все связанные критерии
            await session.execute(
                TemplateCrit.__table__.delete().where(TemplateCrit.user_template_id == template.id)
            )

            # Удаляем все связанные множители
            await session.execute(
                TemplateMnoj.__table__.delete().where(TemplateMnoj.user_template_id == template.id)
            )

            # Удаляем сам шаблон
            await session.delete(template)

        await session.commit()  # Сохранение всех изменений

    return True  # Возвращаем True, если удаление прошло успешно


async def get_templ_key(telegram_id: int, template_name: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()  # Извлекаем единственное значение (user_id)

            if not user_id:
                return False  # Если пользователь не найден, возвращаем False

            # Получаем id шаблона по имени и user_id
            result = await session.execute(
                select(UserTemplates.id).filter_by(user_id=user_id, template_name=template_name)
            )
            template_id = result.scalar()  # Извлекаем единственное значение (template_id)

            if not template_id:
                return False  # Если шаблон не найден, возвращаем False

            current_templ = await session.execute(
                select(UserTemplates.key_for_generating).filter_by(id=template_id)
            )
            key = current_templ.scalar()

            return key

# Получить ключи всех шаблонов
async def get_all_templ_keys() -> list[int]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(UserTemplates.key_for_generating))
            templ_keys = [row[0] for row in result.fetchall()]
    return templ_keys

# Получаем данные шаблона по ключу
async def get_template_data_by_key(key: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            templ_id = await session.execute(
                select(UserTemplates.id).filter_by(key_for_generating=key)
            )
            templ_id_val = templ_id.scalar()

            templ_name = await session.execute(
                select(UserTemplates.template_name).filter_by(id=templ_id_val)
            )
            templ_name_val = templ_name.scalar()

            templ_crits = await session.execute(
                select(UserTemplates.template_name).filter_by(user_template_id=templ_id_val)
            )
            templ_crits_val = templ_crits.scalar()

            templ_mnoj = await session.execute(
                select(UserTemplates.template_name).filter_by(user_template_id=templ_id_val)
            )
            templ_mnoj_val = templ_mnoj.scalar()

            return templ_name_val, templ_crits_val, templ_mnoj_val


# Добавляем шаблон пользователю
async def add_template_to_user(telegram_id: int, templ_name_val, templ_crits_val, templ_mnoj_val):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()

            if not user_id:
                return False  # Если пользователь не найден, возвращаем False

            # Создаем новый шаблон для пользователя
            new_template = UserTemplates(
                user_id=user_id,
                template_name=templ_name_val,
                key_for_generating=123,
                global_score=0),
                TemplateCrit(
                user_id=user_id,
                template_name=templ_name_val,
                key_for_generating=123,
                global_score=0), # TODO need to ended request for created a new template for user

            )

            session.add(new_template)
            await session.commit()
            return True
