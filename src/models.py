from typing import List
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select
from sqlalchemy import select


class Base(DeclarativeBase):
    """
    Base model class with common methods.
    """

    __abstract__ = True

    def __repr__(self):
        """
        Return a string representation of the model object.
        """
        return f"<{self.__class__.__name__}({', '.join(f'{col.name}={getattr(self, col.name)}' for col in self.__table__.columns)})>"

    def __str__(self):
        """
        Return a human-readable string representation of the model object.
        """
        return self.__repr__()

    def to_dict(self):
        """
        Convert the model object to a dictionary.
        :return: Dictionary representation of the model object.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class Version(Base):
    __tablename__ = "version"

    id = mapped_column(Integer, primary_key=True)
    created = mapped_column(DateTime, nullable=False)
    updated = mapped_column(DateTime, nullable=False)


class Instrument(Base):
    __tablename__ = "instruments"

    ticket = mapped_column(String(50), nullable=False, primary_key=True)
    has_ticks = mapped_column(Boolean, nullable=False)
    has_candles = mapped_column(Boolean, nullable=False)
    ticks: Mapped[List["FxTick"]] = relationship()

    def get(self, tickets=None):
        """
        Return instruments.
        :param tickets: list of instruments. None will return all the instruments in the database
        :return: list of instruments.

        """
        # lazy import to avoid circular dependency
        from src.database import DB

        db = DB()

        if tickets is None:
            stmt = select(Instrument)
        else:
            tickets = [x.upper() for x in tickets]
            stmt = select(Instrument).where(Instrument.ticket.in_(tickets))

        with db.session() as session:
            return session.execute(stmt).scalars().all()


class FxTick(Base):
    __tablename__ = "fx_tick"

    id = mapped_column(Integer, primary_key=True)
    ticket = mapped_column(ForeignKey("instruments.ticket"))
    dt = mapped_column(DateTime, nullable=False)
    bid = mapped_column(String(50), nullable=False)
    ask = mapped_column(String(50), nullable=False)

    def get_latest(self, ticket):
        # lazy import to avoid circular dependency
        from src.database import DB

        db = DB()
        stmt = (
            select(FxTick)
            .where(FxTick.ticket == ticket)
            .order_by(FxTick.dt.desc())
            .limit(1)
        )
        with db.session() as session:
            return session.execute(stmt).scalar()
