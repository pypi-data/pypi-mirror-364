
from typing import List, Optional
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms import ValidationError

# importa las entidades utilizadas aqui
from ..models import Entity1
from ..utils.mappers import Mapper
from ..utils.clean_dict_of_keys import clean_dict_of_keys
from ..domain.entities import Entity1Entity
from ..domain.exceptions import EntityNotFoundError


class Entity1Repository:
    """
    Repositorio para manejar la persistencia de datos de la entidad: entity1.
    
    Este repositorio incluye:
    - Validación de existencia de registros.
    - Control de unicidad.
    - Métodos básicos.
    """

    @staticmethod
    def get_all(filters: Optional[dict] = None) -> List[ Entity1Entity ]:
        """
        Obtiene todos los registros de la entidad.
        :return: Lista de registros de la entidad.
        """

        instance_list = Entity1.objects.all()    

        # Aplicar filtros si se proporcionan
        if filters:
            if "nombre" in filters and filters["nombre"] != "":
                instance_list = instance_list.filter(nombre__icontains=filters["nombre"])      
                
        # Tener en cuenta los campos reales que se necesitan en el listado
        instance_list = instance_list.only("id", "nombre", "created_at")

        # Convertir a entidades usando el Mapper genérico
        return [Mapper.model_to_entity(instance, Entity1Entity) for instance in instance_list]        


    @staticmethod
    def get_by_id(id) -> Optional[ Entity1Entity ]:
        """
        Obtiene un registro por su ID.
        
        :param id: ID del registro a recuperar.
        :return: El entidad encontrada o None si no existe.
        """

        try:
            instance = Entity1.objects.get(id=id)
            return Mapper.model_to_entity(instance, Entity1Entity)

        except Entity1.DoesNotExist:
            return None


    @staticmethod
    def exists_by_field(field_name, value) -> bool:
        """
        Verifica si existe un registro con un valor específico para un campo dado.

        :param field_name: Nombre del campo a buscar.
        :param value: Valor del campo a verificar.
        :return: True si existe un registro con el valor dado, False en caso contrario.
        """

        return Entity1.objects.filter(**{field_name: value}).exists()


    @staticmethod
    def count_all(filters: Optional[dict] = None) -> int:
        """
        Cuenta registros que cumplen con ciertas condiciones.

        :param conditions: Condiciones de filtro como clave-valor.
        :return: Número de registros que cumplen las condiciones.
        """

        instance_list = Entity1.objects.all()    

        # Aplicar filtros si se proporcionan
        if filters:
            if "nombre" in filters and filters["nombre"] != "":
                instance_list = instance_list.filter(nombre__icontains=filters["nombre"])            

        return instance_list.count()            


    @staticmethod
    def create(entity: Entity1Entity, external_id: Optional[int], adicionalData=None) -> Entity1Entity:
        """
        Crea un nuevo registro.

        :param entity: Entidad con los datos necesarios para crear el registro.
        :param external_id: ID del padre si es necesario (opcional).
        :param adicionalData: Datos adicionales a incluir en la creación.
        :return: La entidad creada.
        :raises ValueError: Si los datos no son válidos.
        """
        #convertir a dict
        data = entity.to_dict()        

        # Eliminar las claves 'id' y 'uuid' de la data
        data = clean_dict_of_keys(data, keys=['id', 'uuid'])   

        # Eliminar de la data las propiedades que requieren un tratamiento especial
        data = clean_dict_of_keys(data, keys=['external_id', 'adicionalData'])

        # Si se proporciona un ID de otra entidad, agregarlo al diccionario
        # django crea el campo 'external_id' automáticamente si la relación es ForeignKey => otherEntity
        if external_id is not None:
            data['external_id'] = external_id    

        # Crear el registro a partir de los campos presentes en la 'data'
        instance = Entity1(**data)

        # Si adicionalData, agregar datos adicionales
        if adicionalData:
            # Aquí puedes agregar lógica para manejar datos adicionales específicos
            # Por ejemplo, guardar una foto, un password, o cualquier otro campo especial
            pass

        # Validar y guardar
        try:
            instance.full_clean()  # Validaciones del modelo
            instance.save()

        except ValueError as e:
            raise ValueError(f"An error occurred while processing the value: {e}")
        
        return Mapper.model_to_entity(instance, Entity1Entity)


    @staticmethod
    def save(entity: Entity1Entity, adicionalData=None) -> Entity1Entity:
        """
        Guarda los cambios en una entidad existente.

        :param entity: Entidad con los datos a actualizar (debe traer el id en los campos).
        :return: La entidad guardada.
        :raises EntityNotFoundError: Si no existe el registro con el ID dado.
        :raises ValueError: Si los datos no son válidos.
        """

        try:
            # Recuperar el modelo existente basado en el ID de la entidad
            instance = Entity1.objects.get(id=entity.id)

            # Actualizar cada campo de la entidad en el modelo
            for key, value in entity.to_dict().items():
                if hasattr(instance, key):
                    if key != 'id' and key != 'uuid': # No actualizar campos especiales
                        # Los campos especiales son aquellos que nunca cambian como: id, uuid, created_at, updated_at, etc.
                        # o aquellos que tienen una forma especial de ser guardados como: photo, password, etc.
                        setattr(instance, key, value)

            # Si adicionalData, agregar datos adicionales
            if adicionalData:
                # Aquí puedes agregar lógica para manejar datos adicionales específicos
                # Por ejemplo, guardar una foto, un password, o cualquier otro campo especial
                pass

            # Validar y guardar
            instance.full_clean()  # Validaciones del modelo Django
            instance.save()
            
            # Convertir el modelo actualizado de vuelta a una entidad
            return Mapper.model_to_entity(instance, Entity1Entity)

        except Entity1.DoesNotExist:
            raise EntityNotFoundError(f"No entity1 found with ID {id}")

        except ValidationError as e:
            raise ValueError(f"Validation error occurred: {e.message_dict}")


    @staticmethod
    def delete(id) -> bool:
        """
        Elimina un registro por su ID.

        :param id: ID del registro a eliminar.
        :raises EntityNotFoundError: Si no existe el registro con el ID dado.
        """

        try:
            instance = Entity1.objects.get(id=id)
            instance.delete()
            return True

        except Entity1.DoesNotExist:
            raise EntityNotFoundError(f"No entity1 found with ID {id}")


'''
En Django ORM los campos de relación se definen como ForeignKey, ManyToManyField o OneToOneField.
Para la traduccion de relaciones entre entidades, se pueden utilizar los siguientes campos:

- `external_id`: 
    Para relaciones de clave externa (ForeignKey) o uno a uno (OneToOneField)
        ej: external = models.ForeignKey(OtherEntity, on_delete=models.CASCADE, related_name='related_entities')
        o    ej: external = models.OneToOneField(OtherEntity, on_delete=models.CASCADE, related_name='related_entity')
            
    el model de Django crea automáticamente el campo `external_id` este campo es accesible como un atributo de la entidad.

- `external_uuid`: Para relaciones basadas en un UUID adicional aparte del ID.
        ej: external = models.UUIDField(default=uuid.uuid4, editable=False)
     es necesario definir en el model de Django una propiedad 'external_uuid' que retorne el UUID relacionado.
    @property
    def external_uuid(self):
        return str(self.external.uuid) if self.external else None

- `externals`: Para relaciones de muchos a muchos (ManyToManyField).
    Para relaciones de muchos a muchos:
        ej: externals = models.ManyToManyField(OtherEntity, related_name='related_entities')
    el model de Django crea automáticamente el campo `externals` este campo es accesible como un atributo de la entidad.
    este campo es una lista de instancias de la entidad relacionada 
    Para obtenerlos se puede con el uso de un mapper se puede convertir a una lista de ids:
        externals = list(instance.externals.values_list('id', flat=True))
    para asignarlos se puede hacer algo como:
        instance.externals.set([other_entity1, other_entity2, ...])
        o se puede usar directamente una lista de IDs:
        instance.externals.set([1, 2, 3])  # Asignar IDs de otras entidades relacionadas

- `externals_uuids`: Para relaciones de muchos a muchos basadas en UUID adicional aparte del ID.
        ej: externals = models.ManyToManyField(OtherEntity, related_name='related_entities')
    es necesario definir en el model de Django una propiedad 'external_uuids' que retorne una lista de UUIDs relacionados.
    @property
    def externals_uuids(self):
        return list(self.externals.values_list('uuid', flat=True))
'''
