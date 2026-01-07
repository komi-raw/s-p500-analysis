import re
from sqlalchemy import Column, Integer, DateTime, DECIMAL, BigInteger, String
from . import Base

class PriceBase(Base):
    __abstract__ = True

    companyId = Column(Integer, nullable=False)
    date      = Column(DateTime, nullable=False)
    open      = Column(DECIMAL(10, 4), nullable=False)
    low       = Column(DECIMAL(10, 4), nullable=False)
    high      = Column(DECIMAL(10, 4), nullable=False)
    close     = Column(DECIMAL(10, 4), nullable=False)
    volume    = Column(BigInteger, nullable=False)

    # IMPORTANT: ORM = il faut une PK
    __table_args__ = (
        # PK composite logique pour des prix
        # (si ta DB n'a pas de PK, l'ORM va te poser des problèmes)
        # PrimaryKeyConstraint("companyId", "date"),
        {"extend_existing": True},
    )

class CompanyData(Base):
    """
    Représente la table company_data
    """

    __tablename__ = "company_data"

    companyIdx = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        doc="Identifiant unique de l'entreprise"
    )

    code = Column(
        String(10),
        nullable=False,
        doc="Code de l'entreprise (ex: ticker boursier)"
    )

    name = Column(
        String(100),
        nullable=True,
        doc="Nom complet de l'entreprise"
    )

    def __init__(self, code: str, name: str | None = None):
        super().__init__()
        self.code = code
        self.name = name