from app.api_v1.users.repo import UsersRepo
from app.api_v1.users.schemas import UserRead, UserCreate, UserFilter
from app.api_v1.users.repo import users_repo
from app.api_v1.auth.utils import hash_password
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
import random
import logging
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


animals = [
    "Аллигатор",
    "Антерес",
    "Армадилло",
    "Аурокс",
    "Аксолотль",
    "Барсук",
    "Летучая мышь",
    "Бобёр",
    "Буйвол",
    "Капля",
    "Капибара",
    "Хамелеон",
    "Гепард",
    "Шиншилла",
    "Чипмaнк",
    "Чупакабра",
    "Коршун",
    "Койот",
    "Динго",
    "Динозавр",
    "Дельфин",
    "Утка",
    "Слон",
    "Хорёк",
    "Лиса",
    "Жираф",
    "Гофер",
    "Гризли",
    "Ёж",
    "Гиппо",
    "Гиена",
    "Ибис",
    "Ифрит",
    "Игуана",
    "Джекaл",
    "Кенгуру",
    "Коала",
    "Кракен",
    "Лемур",
    "Леопард",
    "Лигер",
    "Лама",
    "Мантa",
    "Миска",
    "Обезьяна",
    "Лось",
    "Нарвал",
    "Nyan Cat",
    "Орангутан",
    "Выдра",
    "Панда",
    "Пингвин",
    "Утконос",
    "Питон",
    "Квага",
    "Кролик",
    "Енот",
    "Носорог",
    "Овца",
    "Шип",
    "Скунс",
    "Белка",
    "Тигр",
    "Черепаха",
    "Морж",
    "Волк",
    "Волкособ",
    "Вомбат",
]

adjectives = {
    "m": [
        "Весёлый",
        "Грустный",
        "Сонный",
        "Игривый",
        "Задумчивый",
        "Быстрый",
        "Медленный",
        "Пушистый",
        "Голодный",
        "Довольный",
        "Загадочный",
        "Яркий",
        "Неуклюжий",
        "Шустрый",
        "Ленивый",
    ],
    "f": [
        "Весёлая",
        "Грустная",
        "Сонная",
        "Игривая",
        "Задумчивая",
        "Быстрая",
        "Медленная",
        "Пушистая",
        "Голодная",
        "Довольная",
        "Загадочная",
        "Яркая",
        "Неуклюжая",
        "Шустрая",
        "Ленивая",
    ],
    "n": [
        "Весёлое",
        "Грустное",
        "Сонное",
        "Игривое",
        "Задумчивое",
        "Быстрое",
        "Медленное",
        "Пушистое",
        "Голодное",
        "Довольное",
        "Загадочное",
        "Яркое",
        "Неуклюжее",
        "Шустрое",
        "Ленивое",
    ],
}


animal_genders = {
    # Мужской род
    "m": [
        "Аллигатор",
        "Антерес",
        "Армадилло",
        "Аурокс",
        "Барсук",
        "Бобёр",
        "Буйвол",
        "Хамелеон",
        "Гепард",
        "Динго",
        "Динозавр",
        "Дельфин",
        "Слон",
        "Хорёк",
        "Жираф",
        "Гофер",
        "Гризли",
        "Ёж",
        "Гиппо",
        "Ибис",
        "Ифрит",
        "Джекaл",
        "Кенгуру",
        "Кракен",
        "Лемур",
        "Леопард",
        "Лигер",
        "Лось",
        "Нарвал",
        "Орангутан",
        "Пингвин",
        "Утконос",
        "Питон",
        "Кролик",
        "Енот",
        "Носорог",
        "Тигр",
        "Морж",
        "Волк",
        "Волкособ",
        "Вомбат",
    ],
    # Женский род
    "f": [
        "Летучая мышь",
        "Капля",
        "Капибара",
        "Шиншилла",
        "Чупакабра",
        "Утка",
        "Лиса",
        "Гиена",
        "Игуана",
        "Коала",
        "Лама",
        "Мантa",
        "Миска",
        "Обезьяна",
        "Выдра",
        "Панда",
        "Овца",
        "Белка",
        "Черепаха",
    ],
    # Средний род (и неизменяемые)
    "n": ["Квага", "Шип", "Скунс"],
}


class UsersService(BaseService):
    def __init__(self, repository: UsersRepo, schema=UserRead):
        self.repository = repository
        self.schema_out = schema
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def is_admin(self, session: AsyncSession, user_id: int):
        await self.repository.is_admin(session=session, user_id=user_id)

    async def get_all_admins(self, session: AsyncSession):
        await self.repository.get_all_admins(session=session)

    def generate_random_names(self):
        animal = random.choice(animals)
        gender = "m"
        for g, animals_list in animal_genders.items():
            if animal in animals_list:
                gender = g
                break

        adjective = random.choice(adjectives[gender])
        return adjective, animal

    async def create_new_user(
        self, session: AsyncSession, email: EmailStr, password: str, auth_type: str
    ) -> UserRead:
        first_name, last_name = self.generate_random_names()
        user_create = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hash_password(password),
            auth_type="default",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        user = await users_service.add(session=session, values=user_create)
        logger.info(f"Create new user: {email} Auth_type: {auth_type} ")
        return user

    async def get_user_by_email(self, session: AsyncSession, email: EmailStr):
        return await self.repository.find_one_or_none(
            session=session, filters=UserFilter(email=email)
        )

    async def get_user_by_id(self, session: AsyncSession, id: int) -> UserRead:
        return await self.repository.find_one_or_none(
            session=session, filters=UserFilter(id=id)
        )

    async def set_user_is_verify(self, session: AsyncSession, email: EmailStr):
        return await self.repository.update(
            session=session,
            filters=UserFilter(email=email),
            values=UserFilter(is_verified=True),
        )

    async def reset_user_password(
        self, session: AsyncSession, email: EmailStr, new_password
    ):
        return await self.repository.update(
            session=session,
            filters=UserFilter(email=email),
            values=UserFilter(password=hash_password(new_password)),
        )


users_service: UsersService = UsersService(repository=users_repo)
