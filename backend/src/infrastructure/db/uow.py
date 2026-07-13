from .session import AsyncSessionLocal
from .repositories import Repositories
class SqlAlchemyUnitOfWork:
    def __init__(self): self.session=None; self.repo=None
    async def __aenter__(self):
        self.session=AsyncSessionLocal(); self.repo=Repositories(self.session); return self
    async def __aexit__(self, exc_type, exc, tb):
        await (self.session.rollback() if exc else self.session.commit()); await self.session.close()
    async def commit(self): await self.session.commit()
    async def rollback(self): await self.session.rollback()
