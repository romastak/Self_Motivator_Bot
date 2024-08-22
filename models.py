from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import Integer
import asyncpg
import asyncio

engine = create_async_engine(url='postgresql+asyncpg://postgres:1234@127.0.0.1:5432/motivator_db')  # Создание движка
async_session = async_sessionmaker(engine)  # Подключение к БД
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):  # Основной класс для всех моделей
    pass

class User(Base):
    __tablename__ = 'users'  # Название таблицы
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String)

class UserTemplates(Base):
    __tablename__ = 'user_templates'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    template_name: Mapped[str] = mapped_column(String)
	key_for_generating: Mapped[str] = mapped_column(String)
	global_score: Mapped[float] = mapped_column()

class TemplateCrit(Base):
    __tablename__ = 'template_crit'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_template_id: Mapped[int] = mapped_column(ForeignKey('user_templates.id'))
    crit_name: Mapped[str] = mapped_column(String)
    crit_score: Mapped[float] = mapped_column()
    crit_comment: Mapped[int] = mapped_column()

class TemplateMnoj(Base):
    __tablename__ = 'template_mnoj'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_template_id: Mapped[int] = mapped_column(ForeignKey('user_templates.id'))
    mnoj_name: Mapped[str] = mapped_column(String)
    mnoj_score: Mapped[float] = mapped_column()
    mnoj_comment: Mapped[int] = mapped_column()

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создание таблиц в БД согласно моделям

# Вызов функции для создания таблиц
if __name__ == "__main__":
    asyncio.run(async_main())
