from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from sqlalchemy import select
from database import Base


FETCH_DEFAULT_TIMEOUT = 10
ONLINE_DEFAULT_TIMEOUT = 120


class Device(Base):
    __tablename__ = 'devices'
    __table_args__ = {'extend_existing': True}

    # Base fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    scenario = Column(String)
    # Timing
    fetch_timeout_sec = Column(Integer, default=FETCH_DEFAULT_TIMEOUT)
    online_timeout_sec = Column(Integer, default=ONLINE_DEFAULT_TIMEOUT)
    last_online_time = Column(DateTime, default=datetime.now() - timedelta(hours=1))
    # Behaviour flags
    set_settings = Column(Boolean, default=False)
    capture_request = Column(Boolean, default=False)

    readings = relationship("Reading", cascade="all,delete", backref="parent")

    def is_online(self) -> bool:
        from database import open_db_session
        with open_db_session() as session:
            stmt = select(Device).where(Device.id == self.id)
            device = session.scalars(stmt).one_or_none()
            if not device:
                return False
            seconds = device.online_timeout_sec

        return datetime.now() - self.last_online_time <= timedelta(seconds=seconds)


class Reading(Base):
    __tablename__ = "readings"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    reading = Column(String)
    time = Column(String)  # Format %d-%m-%Y_%H-%M-%S
