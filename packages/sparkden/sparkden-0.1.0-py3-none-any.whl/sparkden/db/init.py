from advanced_alchemy.base import metadata_registry
from bcrypt import gensalt, hashpw
from sparkden.shared.pg import get_engine, get_session_maker
from sqlalchemy import exists, select
from sqlalchemy.exc import OperationalError

from .schema import User, UserRole


async def init_db() -> None:
    await seed_db()


async def seed_db() -> None:
    async with get_engine().begin() as conn:
        try:
            await conn.run_sync(metadata_registry.get().create_all)
        except OperationalError as exc:
            print(f"Could not create target metadata.  Reason: {exc}")

    async with get_session_maker().begin() as db_session:
        statement = select(exists().where(User.id.is_not(None)))
        result = await db_session.execute(statement)
        if not result.scalar():
            try:
                for index, user in enumerate(users):
                    is_admin = index in [0, 1]
                    db_session.add(
                        User(
                            name=user,
                            username=f"test{index + 1}",
                            password=hashpw("password123".encode(), gensalt()),
                            extra_info={"college": "计算机学院"},
                            role=UserRole.ADMIN if is_admin else UserRole.USER,
                        )
                    )
                # 事务会在 begin() 上下文管理器退出时自动提交
                print(f"Successfully seeded {len(users)} users")
            except Exception as exc:
                print(f"Error seeding users: {exc}")
                raise


users = [
    "张三",
    "李四",
    "王五",
    "赵六",
    "孙七",
    "周八",
    "吴九",
    "郑十",
    "John Smith",
    "Alice Brown",
]
