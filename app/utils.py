# app/utils.py

from datetime import datetime, timedelta
import pytz
from app.config import Config

def get_current_holiday():
    now = datetime.now(pytz.timezone(Config.TIMEZONE))
    current_year = now.year

    for holiday in Config.HOLIDAYS:
        start_month, start_day = map(int, holiday['start_date'].split('-'))
        end_month, end_day = map(int, holiday['end_date'].split('-'))

        start_date = datetime(current_year, start_month, start_day, tzinfo=pytz.timezone(Config.TIMEZONE))
        end_date = datetime(current_year, end_month, end_day, tzinfo=pytz.timezone(Config.TIMEZONE))

        # Adjust for holidays that span over the year-end
        if end_date < start_date:
            end_date += timedelta(days=365)

        if start_date <= now <= end_date:
            return holiday

    return None
