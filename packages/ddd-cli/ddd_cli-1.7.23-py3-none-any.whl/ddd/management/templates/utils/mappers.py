# utils/mappers.py
from dataclasses import asdict, fields
from typing import Type, TypeVar, Any
from django.db import models
from datetime import datetime, date
import decimal
import uuid

T = TypeVar("T")

class Mapper:
    
    @staticmethod
    def model_to_entity(model_instance: models.Model, entity_class: Type[T]) -> T:
        """
        Convierte una instancia de modelo Django a una entidad basada solo en los campos de la entidad.

        Conversión según el tipo de propiedad de Django Model:
            CharField -> (str).
            TextField -> (str).
            IntegerField -> (int).
            FloatField -> (float)
            BooleanField -> (bool)
            DateField -> (datetime.date)
            DateTimeField -> (datetime.time)
            ForeignKey -> (int/str)
            ManyToManyField -> lista o Queryset de objetos
            DecimalField -> (decimal.Decimal)
            UUIDField -> uuid.UUID
            JSONField -> (dict o list)
            FileField o ImageField -> ruta de archivo(str)
            EmailField -> (str)
            SlugField -> (str)
            AutoField (ID auto-generado) -> (int)
        """

        if not model_instance:
            raise ValueError("Model instance cannot be None")

        entity_field_names = {f.name for f in fields(entity_class)}

        data = {}
        for field_name in entity_field_names:
            if not hasattr(model_instance, field_name):
                continue
            
            try:
                value = getattr(model_instance, field_name)
            except AttributeError:
                continue

            # Manejo especial para diferentes tipos de campo
            if isinstance(value, models.Manager):
                # Para relaciones ManyToMany o reverse FK
                value = list(value.values_list('pk', flat=True)) if value else []

            elif isinstance(value, uuid.UUID):
                # Dejar tal cual; que la entidad lo maneje
                pass

            elif isinstance(value, (datetime, date)):
                # Dejar tal cual; que la entidad lo maneje
                pass

            elif isinstance(value, decimal.Decimal):
                value = float(value)  # o dejar como Decimal si tu entidad lo acepta            

            elif isinstance(value, dict) or isinstance(value, list):
                # JSONField ya devuelve dict/list, dejar intacto
                pass

            elif hasattr(value, 'pk'):
                # Es una relación ForeignKey/OneToOne -> extraer ID
                value = value.pk if value else None

            # Añadir al diccionario solo si es válido
            data[field_name] = value

        return entity_class(**data)
    
    @staticmethod
    def entity_to_dict(entity_instance: Any) -> dict:
        """Convierte una entidad en un diccionario que contiene solo sus propios campos"""
        # Convertir la entidad a diccionario directamente con asdict (solo los campos de la entidad)
        return asdict(entity_instance)
    
    @staticmethod
    def model_to_dict(model_instance: models.Model) -> dict:
        """
        Convierte un modelo Django a diccionario usando sus campos reales.
        Alternativa segura a asdict().
        """
        data = {}
        for field in model_instance._meta.get_fields():
            try:
                value = getattr(model_instance, field.name)
                
                if isinstance(field, models.ManyToManyField):
                    data[field.name] = list(value.values_list('pk', flat=True))
                elif isinstance(field, models.ForeignKey) and value:
                    data[field.name] = value.pk
                elif isinstance(value, uuid.UUID):
                    data[field.name] = str(value)
                elif isinstance(value, (datetime, date)):
                    data[field.name] = value
                else:
                    data[field.name] = value
            except AttributeError:
                continue  # Algunos campos virtuales pueden no estar disponibles
        return data
    
