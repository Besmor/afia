"""SQLAlchemy models for the Afia synthetic pharmacy ecosystem.

Design rationale in `docs/decisions/ADR-005-synthetic-ecosystem-data-model.md`.
"""
from __future__ import annotations

import enum
from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DigitalMaturity(str, enum.Enum):
    """Digital maturity tier observed in the Conakry scan (July 2026)."""
    NONE = "NONE"
    BASIC_WEBSITE = "BASIC_WEBSITE"
    ECOMMERCE_PARTIAL = "ECOMMERCE_PARTIAL"
    ECOMMERCE_FULL = "ECOMMERCE_FULL"
    API_LINKED = "API_LINKED"


class District(str, enum.Enum):
    """Conakry administrative communes."""
    KALOUM = "Kaloum"
    DIXINN = "Dixinn"
    RATOMA = "Ratoma"
    MATAM = "Matam"
    MATOTO = "Matoto"
    UNKNOWN = "Unknown"


class MedicationForm(str, enum.Enum):
    """Pharmaceutical dosage forms most relevant to community-pharmacy dispensing."""
    TABLET = "tablet"
    CAPSULE = "capsule"
    SYRUP = "syrup"
    INJECTION = "injection"
    OINTMENT = "ointment"
    DROPS = "drops"
    SUPPOSITORY = "suppository"
    SACHET = "sachet"


class Pharmacy(Base):
    """A pharmacy within the synthetic Conakry ecosystem.

    Grounded in the 15-pharmacy digital-maturity scan (June-July 2026):
    - `id` maps 1:1 to the anonymised scan records (Pharmacy_01..Pharmacy_15)
    - `district` preserves observed geographic distribution
    - `digital_maturity` preserves observed maturity distribution
    - `latitude`, `longitude`, `opening_hours` are synthetic (grounded in district centroids
      and published West African pharmacy operating norms; documented in
      data/synthetic/README.md).
    """
    __tablename__ = "pharmacies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[District] = mapped_column(Enum(District), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    digital_maturity: Mapped[DigitalMaturity] = mapped_column(
        Enum(DigitalMaturity), nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    opens_at: Mapped[time] = mapped_column(Time, nullable=False)
    closes_at: Mapped[time] = mapped_column(Time, nullable=False)
    open_on_sunday: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    stock_items: Mapped[list["StockItem"]] = relationship(
        back_populates="pharmacy", cascade="all, delete-orphan"
    )


class Medication(Base):
    """A medication in the catalogue. Seeded from the WHO Essential Medicines List (EML)."""
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inn: Mapped[str] = mapped_column(String(120), nullable=False, index=True)  # International Non-proprietary Name
    brand_names: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    form: Mapped[MedicationForm] = mapped_column(Enum(MedicationForm), nullable=False)
    strength: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "500 mg"
    therapeutic_class: Mapped[str] = mapped_column(String(80), nullable=False)
    is_who_essential: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    stock_items: Mapped[list["StockItem"]] = relationship(
        back_populates="medication", cascade="all, delete-orphan"
    )


class StockItem(Base):
    """Per-pharmacy per-medication stock and price.

    Synthetic: quantity and price drawn from calibrated distributions
    (documented in data/synthetic/README.md). Not every pharmacy stocks every
    medication (sparse join table).
    """
    __tablename__ = "stock_items"
    __table_args__ = (
        UniqueConstraint("pharmacy_id", "medication_id", name="uq_stock_pharmacy_med"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pharmacy_id: Mapped[str] = mapped_column(
        ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medication_id: Mapped[int] = mapped_column(
        ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price_gnf: Mapped[int] = mapped_column(Integer, nullable=False)  # Guinean Franc, integer
    last_verified_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    pharmacy: Mapped["Pharmacy"] = relationship(back_populates="stock_items")
    medication: Mapped["Medication"] = relationship(back_populates="stock_items")
