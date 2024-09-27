import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Integer, update
from assets.db_modules.models import User, UserTemplates, TemplateCrit, TemplateMnoj, async_session, AsyncSessionLocal


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

async def edit_user_template(telegram_id: int, username: str, template_name: str, crits: list, mnojs: list, chosen_templ_id: int): # TODO ended this func
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

            # Запоминаем глобальные очки и ключ генерации
            templ_global_score = await session.execute(
                select(UserTemplates.global_score).filter_by(id=chosen_templ_id)
            )
            templ_global_score = templ_global_score.scalar()

            templ_key_for_generating = await session.execute(
                select(UserTemplates.key_for_generating).filter_by(id=chosen_templ_id)
            )
            templ_key_for_generating = templ_key_for_generating.scalar()


            # Удаляем шаблон и связанные таблы
            await session.execute(delete(TemplateCrit).filter_by(user_template_id=chosen_templ_id))
            await session.execute(delete(TemplateMnoj).filter_by(user_template_id=chosen_templ_id))
            await session.execute(delete(UserTemplates).filter_by(id=chosen_templ_id))

            # И создаем обновленный, записывая очки и ключ с удаленного
            new_template = UserTemplates(
                user_id=user_id,
                template_name=template_name,
                key_for_generating=templ_key_for_generating,
                global_score=templ_global_score
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


async def get_user_templates(telegram_id: int) -> list[tuple[int, str]]:
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
                    select(UserTemplates.id, UserTemplates.template_name).filter_by(user_id=user_id)
                )
                # Преобразуем результат в список кортежей
                user_templ = [(row[0], row[1]) for row in result.fetchall()]
            else:
                user_templ = []  # Если пользователь не найден, возвращаем пустой список

    return user_templ

async def delete_user_template(telegram_id: int, templ_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        async with session.begin():

            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()  # Извлекаем единственное значение (user_id)

            # Удаляем все связанные критерии
            await session.execute(
                TemplateCrit.__table__.delete().where(TemplateCrit.user_template_id == templ_id)
            )

            # Удаляем все связанные множители
            await session.execute(
                TemplateMnoj.__table__.delete().where(TemplateMnoj.user_template_id == templ_id)
            )

            # Удаляем сам шаблон
            await session.execute(
                UserTemplates.__table__.delete().where(UserTemplates.id == templ_id)
            )

        await session.commit()  # Сохранение всех изменений

    return True  # Возвращаем True, если удаление прошло успешно


async def get_templ_key(telegram_id: int, templ_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():

            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()  # Извлекаем единственное значение (user_id)

            if not user_id:
                return False  # Если пользователь не найден, возвращаем False

            # Получаем ключ по id шаблона
            result = await session.execute(
                select(UserTemplates.key_for_generating).filter_by(user_id=user_id, id=templ_id)
            )
            key = result.scalar()  # Извлекаем единственное значение (template_id)

            return key

# Получить ключи всех шаблонов
async def get_all_templ_keys() -> list[int]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(UserTemplates.key_for_generating))
            templ_keys = [row[0] for row in result.fetchall()]
    return templ_keys

# Получаем данные шаблона по ключу
async def get_template_data(key: str, templ_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получение данных шаблона по ключу
            if templ_id == None:
                templ_id = await session.execute(
                    select(UserTemplates.id).filter_by(key_for_generating=key)
                )
                templ_id_val = templ_id.scalar()
            # Получение данных шаблона по ID
            elif key == None:
                templ_id_val = templ_id

            templ_name = await session.execute(
                select(UserTemplates.template_name).filter_by(id=templ_id_val)
            )
            templ_name_val = templ_name.scalar()

            templ_crit = await session.execute(
                select(TemplateCrit.crit_name, TemplateCrit.crit_score, TemplateCrit.crit_comment).filter_by(user_template_id=templ_id_val)
            )
            templ_crit_val = templ_crit.all()

            templ_mnoj = await session.execute(
                select(TemplateMnoj.mnoj_name, TemplateMnoj.mnoj_score, TemplateMnoj.mnoj_comment).filter_by(user_template_id=templ_id_val)
            )
            templ_mnoj_val = templ_mnoj.all()

            return templ_name_val, templ_crit_val, templ_mnoj_val


# Добавляем шаблон пользователю, который получен по ключу
async def add_template_to_user(telegram_id, templ_name_val, templ_crits_val, templ_mnoj_val):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем user_id по telegram_id
            result = await session.execute(
                select(User.id).filter_by(tg_id=telegram_id)
            )
            user_id = result.scalar()
            key_for_generating = str(random.randint(1000000000, 9999999999))

            # Создаем новый шаблон по ключу для пользователя
            if user_id:
                new_template = UserTemplates(
                    user_id=user_id,
                    template_name=templ_name_val,
                    key_for_generating=key_for_generating,
                    global_score=0
                )

                # Добавляем новый шаблон в сессию и сохраняем его, чтобы получить его id
                session.add(new_template)
                await session.flush()  # Сохраняет данные и обновляет new_template.id

            if templ_crits_val:
                new_template_crits = []
                for crit in templ_crits_val:
                    new_template_crits.append(TemplateCrit(
                        user_template_id=new_template.id,
                        crit_name=crit[0],
                        crit_score=crit[1],
                        crit_comment=crit[2],
                    ))
                session.add_all(new_template_crits)  # Добавляем все критерии за раз

            if templ_mnoj_val:
                new_template_mnoj = []
                for mnoj in templ_mnoj_val:
                    new_template_mnoj.append(TemplateMnoj(
                        user_template_id=new_template.id,
                        mnoj_name=mnoj[0],
                        mnoj_score=mnoj[1],
                        mnoj_comment=mnoj[2],
                    ))
                session.add_all(new_template_mnoj)  # Добавляем все множители за раз

            await session.commit()
            return True


# Получаем глобальные очки шаблона
async def get_template_global_score(templ_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():

            global_score = await session.execute(
                select(UserTemplates.global_score).filter_by(id=templ_id)
            )
            global_score_val = global_score.scalar()

            return global_score_val


# Обнуляем глобальные очки шаблона
async def make_null_template_global_score(templ_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():

            await session.execute(
                update(UserTemplates)
                .where(UserTemplates.id == templ_id)  # Находим шаблон по id
                .values(global_score=0)  # Обновляем поле global_score на 0
            )

            await session.commit()

            return True


# Изменяем глобальные очки шаблона
async def change_template_global_score(templ_id, score_val):
    async with AsyncSessionLocal() as session:
        async with session.begin():

            await session.execute(
                update(UserTemplates)
                .where(UserTemplates.id == templ_id)
                .values(global_score=score_val)
            )

            await session.commit()

            return True

# Получаем данные шаблона для редактирования
# Добавляем шаблон пользователю, который получен по ключу
async def get_templ_data_for_edit(templ_id):
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

            templ_crit = await session.execute(
                select(TemplateCrit.crit_name, TemplateCrit.crit_score, TemplateCrit.crit_comment).filter_by(
                    user_template_id=templ_id_val)
            )
            templ_crit_val = templ_crit.all()

            templ_mnoj = await session.execute(
                select(TemplateMnoj.mnoj_name, TemplateMnoj.mnoj_score, TemplateMnoj.mnoj_comment).filter_by(
                    user_template_id=templ_id_val)
            )
            templ_mnoj_val = templ_mnoj.all()

            return templ_name_val, templ_crit_val, templ_mnoj_val