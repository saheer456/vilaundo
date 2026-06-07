import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# DATABASE_URL expected in env, e.g. postgresql+asyncpg://user:pass@host:5432/dbname
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL') or 'sqlite+aiosqlite:///./dev.db'

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    """Async session generator for FastAPI dependencies."""
    async with AsyncSessionLocal() as session:
        yield session
