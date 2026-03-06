from config.database import SessionLocal
from sqlalchemy import text


class DelayService:

    @staticmethod
    def add_delay(train_id, station_id, delay_duration, reason):
        db = SessionLocal()
        try:
            sql = text("""
                INSERT INTO delay_records 
                (train_id, station_id, delay_duration, delay_reason)
                VALUES (:train_id, :station_id, :delay_duration, :reason)
            """)
            db.execute(sql, {
                "train_id": train_id,
                "station_id": station_id,
                "delay_duration": delay_duration,
                "reason": reason
            })
            db.commit()
            return True
        finally:
            db.close()