from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker
from core.config import settings
from asyncio import current_task
from sqladmin import Admin

class DatabaseHelper:
 

    def __init__(self, url: str, echo: bool):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )
        self.admin: Admin = None

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session
    
    def create_admin(self, app, engine):
        if self.admin is None:
            return Admin(app=app, engine=engine)
        return self.admin

    def get_admin(self):
        return self.admin
        
    def add_admin_view(self, view):
        if self.admin is not None:
            self.admin.add_view(view=view)
        

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()





db_helper = DatabaseHelper(url=settings.db.DATABASE_URL_asyncpg, echo=False)
