import asyncio
import random
import re
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State # Классы состояний
from aiogram.fsm.context import FSMContext # Инструмент управления состояниями
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from assets.other_modules.keyboards import main_keyboard, create_template_keyboard, cancel_keyboard, delete_crit_keyboard, delete_mnoj_keyboard
from assets.db_modules.requests import save_user_template





