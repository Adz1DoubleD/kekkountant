import aiomysql
import os


class DBManager:
    def __init__(self):
        self.pool = None
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = int(os.getenv("DB_PORT"))

    async def _get_pool(self):
        if self.pool is None:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.database,
                port=self.port,
                autocommit=True,
                cursorclass=aiomysql.DictCursor,
            )
        return self.pool

    async def _execute_query(
        self, query, params=None, fetch_one=False, fetch_all=False
    ):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                if fetch_one:
                    return await cur.fetchone()
                if fetch_all:
                    return await cur.fetchall()
                return None

    async def check_is_fastest(self, time_to_check):
        try:
            result = await self._execute_query(
                "SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL",
                fetch_one=True,
            )
            fastest_time = result["MIN(time_taken)"]
            return time_to_check < fastest_time if fastest_time else None
        except Exception:
            return None

    async def check_highest_streak(self):
        try:
            result = await self._execute_query(
                """
                SELECT name, streak FROM leaderboard
                WHERE streak = (SELECT MAX(streak) FROM leaderboard WHERE streak > 0)
                LIMIT 1
                """,
                fetch_one=True,
            )
            return result["name"], result["streak"] if result else ("No user", 0)
        except Exception:
            return ("No user", 0)

    async def get_fastest_time(self):
        try:
            result = await self._execute_query(
                """
                SELECT name, MIN(time_taken) FROM leaderboard
                WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
                """,
                fetch_one=True,
            )
            return result["name"], result["MIN(time_taken)"] if result else (
                "No user",
                0,
            )
        except Exception:
            return ("No user", 0)

    async def get_by_name(self, name):
        try:
            result = await self._execute_query(
                "SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s",
                (name,),
                fetch_one=True,
            )
            return result if result else {"clicks": 0, "time_taken": 0, "streak": 0}
        except Exception:
            return {"clicks": 0, "time_taken": 0, "streak": 0}

    async def get_leaderboard(self, limit=10):
        try:
            results = await self._execute_query(
                "SELECT name, clicks FROM leaderboard ORDER BY clicks DESC LIMIT %s",
                (limit,),
                fetch_all=True,
            )
            return "\n".join(
                f"{rank + 1} {row['name']}: {row['clicks']}"
                for rank, row in enumerate(results)
            )
        except Exception:
            return "Error retrieving leaderboard data"

    async def get_total_clicks(self):
        try:
            result = await self._execute_query(
                "SELECT SUM(clicks) FROM leaderboard",
                fetch_one=True,
            )
            return result["SUM(clicks)"] if result["SUM(clicks)"] else 0
        except Exception:
            return 0

    async def reset_leaderboard(self):
        try:
            await self._execute_query("DELETE FROM leaderboard")
            return "Clicks leaderboard reset successfully"
        except Exception:
            return "Error resetting clicks"

    async def update_clicks(self, name, time_taken):
        try:
            user_data = await self._execute_query(
                "SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s",
                (name,),
                fetch_one=True,
            )

            if not user_data:
                await self._execute_query(
                    """
                    INSERT INTO leaderboard (name, clicks, time_taken, streak)
                    VALUES (%s, 1, %s, 1)
                    """,
                    (name, time_taken),
                )
            else:
                clicks = user_data["clicks"]
                current_time_taken = user_data["time_taken"]
                current_streak = user_data["streak"]
                new_time = (
                    min(time_taken, current_time_taken)
                    if current_time_taken
                    else time_taken
                )

                await self._execute_query(
                    """
                    UPDATE leaderboard
                    SET clicks = %s, time_taken = %s, streak = %s
                    WHERE name = %s
                    """,
                    (clicks + 1, new_time, current_streak + 1, name),
                )

            await self._execute_query(
                "UPDATE leaderboard SET streak = 0 WHERE name <> %s",
                (name,),
            )

            return "Click updated successfully"
        except Exception as e:
            return f"Error updating clicks: {e}"
