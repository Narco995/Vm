import asyncio
import re
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from database.db_manager import DBManager
from bot.services.ai_service import AIService

logger = logging.getLogger(__name__)


class AutomationService:
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
        self.ai = AIService()
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.start()
        await self._restore_automations()

    async def _restore_automations(self):
        automations = await self.db.get_all_active_automations()
        for auto_id, user_id, name, task, schedule in automations:
            try:
                trigger = self._parse_schedule(schedule)
                if trigger:
                    self.scheduler.add_job(
                        self._run_automation,
                        trigger=trigger,
                        args=[user_id, task],
                        id=f"auto_{auto_id}",
                        replace_existing=True
                    )
            except Exception as e:
                logger.error(f"Failed to restore automation {auto_id}: {e}")

    def _parse_schedule(self, schedule: str):
        schedule = schedule.lower().strip()

        if "every day" in schedule or "daily" in schedule:
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', schedule)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                period = time_match.group(3)
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0
                return CronTrigger(hour=hour, minute=minute)
            return CronTrigger(hour=9, minute=0)

        if "every hour" in schedule or "hourly" in schedule:
            return IntervalTrigger(hours=1)

        if "every" in schedule:
            num_match = re.search(r'every\s+(\d+)\s+(minute|hour|day)', schedule)
            if num_match:
                n = int(num_match.group(1))
                unit = num_match.group(2)
                if unit == "minute":
                    return IntervalTrigger(minutes=n)
                elif unit == "hour":
                    return IntervalTrigger(hours=n)
                elif unit == "day":
                    return IntervalTrigger(days=n)

        return IntervalTrigger(hours=24)

    async def _run_automation(self, user_id: int, task: str):
        try:
            result = await self.ai.chat(
                [{"role": "user", "content": task}],
                style="structured"
            )
            await self.bot.send_message(
                chat_id=user_id,
                text=f"⚙️ **Automation Run**\n\n{result}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Automation error for user {user_id}: {e}")

    async def add_automation(self, user_id: int, name: str, task: str, schedule: str) -> bool:
        auto_id = await self.db.add_automation(user_id, name, task, schedule)
        try:
            trigger = self._parse_schedule(schedule)
            if trigger:
                self.scheduler.add_job(
                    self._run_automation,
                    trigger=trigger,
                    args=[user_id, task],
                    id=f"auto_{auto_id}",
                    replace_existing=True
                )
                return True
        except Exception as e:
            logger.error(f"Failed to add automation: {e}")
        return False
