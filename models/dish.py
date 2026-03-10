from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from metrics.db import Base

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    category = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    available = Column(Boolean, default=True)

    # los va a agregar el dueño mas tarde? quizas en una implementacion futura
    tags = Column(JSON, nullable=True)



    #por ahora que queden null pero mas tarde los quiero implementar.
    # metadatos de importación IA
    # extraction confidence es un numero entre 0,1 que indica que tan segura estaba la IA antes de llenar todos los parametros del plato
    extraction_confidence = Column(Float, nullable=True)
    # exctraction source pueden ser 4, ai_import(lo hizo la ia), manual (lo creo el dueño), modified, file import
    extraction_source = Column(String, nullable=True)
