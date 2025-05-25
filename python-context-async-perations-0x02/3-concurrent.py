import asyncio
import aiosqlite

async def async_fetch_users():
    """Fetch all users from the database"""
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def async_fetch_older_users():
    """Fetch users older than 40 from the database"""
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    """Execute both queries concurrently using asyncio.gather"""
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    all_users, older_users = results
    print("All users:", all_users)
    print("Users older than 40:", older_users)

# Run the concurrent fetch
if __name__ == "__main__":
    asyncio.run(fetch_concurrently()) 