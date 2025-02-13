from api_v1.users.schemas import User
from api_v1.users.crud import get_user
from sqlalchemy.ext.asyncio import AsyncSession


async def is_user_exist(user_id: int, session: AsyncSession):
    user = get_user(session=session, user_id=user_id)
