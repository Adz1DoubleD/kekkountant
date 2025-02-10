import mysql.connector
import os


class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT"),
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def check_is_fastest(self, time_to_check):
        try:
            self.connect()
            self.cursor.execute(
                "SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL"
            )
            fastest_time = self.cursor.fetchone()["MIN(time_taken)"]

            if isinstance(time_to_check, (int, float)) and isinstance(
                fastest_time, (int, float)
            ):
                return time_to_check < fastest_time

            return None
        except mysql.connector.Error:
            return None
        finally:
            self.close()

    def check_highest_streak(self):
        try:
            self.connect()
            self.cursor.execute(
                """
                SELECT name, streak FROM leaderboard
                WHERE streak = (SELECT MAX(streak) FROM leaderboard WHERE streak > 0)
                LIMIT 1
                """
            )
            result = self.cursor.fetchone()
            return result if result else None
        except mysql.connector.Error:
            return None
        finally:
            self.close()

    def get_fastest_time(self):
        try:
            self.connect()
            self.cursor.execute(
                """
                SELECT name, MIN(time_taken) FROM leaderboard
                WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
                """
            )
            result = self.cursor.fetchone()
            return result if result else ("No user", 0)
        except mysql.connector.Error:
            return ("No user", 0)
        finally:
            self.close()

    def get_by_name(self, name):
        try:
            self.connect()
            self.cursor.execute(
                "SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s",
                (name,),
            )
            result = self.cursor.fetchone()
            return result if result else (0, 0, 0)
        except mysql.connector.Error:
            return (0, 0, 0)
        finally:
            self.close()

    def get_leaderboard(self, limit=10):
        try:
            self.connect()
            self.cursor.execute(
                "SELECT name, clicks FROM leaderboard ORDER BY clicks DESC LIMIT %s",
                (limit,),
            )
            leaderboard_data = self.cursor.fetchall()
            leaderboard_text = "\n".join(
                [
                    f"{rank + 1} {row['name']}: {row['clicks']}"
                    for rank, row in enumerate(leaderboard_data)
                ]
            )
            return leaderboard_text
        except mysql.connector.Error:
            return "Error retrieving leaderboard data"
        finally:
            self.close()

    def get_total_clicks(self):
        try:
            self.connect()
            self.cursor.execute("SELECT SUM(clicks) FROM leaderboard")
            total_clicks = self.cursor.fetchone()["SUM(clicks)"]
            return total_clicks if total_clicks else 0
        except mysql.connector.Error:
            return 0
        finally:
            self.close()

    def reset_leaderboard(self):
        try:
            self.connect()
            self.cursor.execute("DELETE FROM leaderboard")
            self.connection.commit()
            return "Clicks leaderboard reset successfully"
        except mysql.connector.Error:
            return "Error resetting clicks"
        finally:
            self.close()

    async def update_clicks(self, name, time_taken):
        try:
            self.connect()
            self.cursor.execute(
                "SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s",
                (name,),
            )
            user_data = self.cursor.fetchone()

            if user_data is None:
                self.cursor.execute(
                    """
                    INSERT INTO leaderboard (name, clicks, time_taken, streak)
                    VALUES (%s, 1, %s, 1)
                    """,
                    (name, time_taken),
                )
            else:
                clicks, current_time_taken, current_streak = user_data.values()
                new_time = (
                    min(time_taken, current_time_taken)
                    if current_time_taken
                    else time_taken
                )

                self.cursor.execute(
                    """
                    UPDATE leaderboard
                    SET clicks = %s, time_taken = %s, streak = %s
                    WHERE name = %s
                    """,
                    (clicks + 1, new_time, current_streak + 1, name),
                )

            self.cursor.execute(
                "UPDATE leaderboard SET streak = 0 WHERE name <> %s", (name,)
            )

            self.connection.commit()
            return "Click updated successfully"
        except mysql.connector.Error as e:
            return f"Error updating clicks: {e}"
        finally:
            self.close()

    def set_click_time(self, value: int):
        try:
            self.connect()
            self.cursor.execute(
                "UPDATE settings SET value = %s WHERE setting_name = 'click_me'",
                (value,),
            )
            self.connection.commit()
            return "Completed"
        except mysql.connector.Error as e:
            return f"Error updating click_me: {e}"
        finally:
            self.close()

    def get_click_time(self):
        try:
            self.connect()
            self.cursor.execute(
                "SELECT value FROM settings WHERE setting_name = 'click_me'"
            )
            result = self.cursor.fetchone()
            return result["value"] if result else 0
        except mysql.connector.Error:
            return
