from factory import Faker, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from src.core.models import User, Post


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None

    name = Faker("name")


class PostFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session = None

    title = Faker("sentence", nb_words=5, variable_nb_words=True)
    user = SubFactory(UserFactory)


ALL_FACTORIES = [UserFactory, PostFactory]
