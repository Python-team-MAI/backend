from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqladmin import ModelView
from sqlalchemy import String, ForeignKey, Boolean
from .users import UsersOrm


class UserAdmin(ModelView, model=UsersOrm):
    column_list = [UsersOrm.id, UsersOrm.email, UsersOrm.first_name]