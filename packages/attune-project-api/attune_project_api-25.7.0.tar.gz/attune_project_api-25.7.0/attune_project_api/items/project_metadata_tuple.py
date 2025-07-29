from typing import Optional

from attune_project_api import ObjectStorageContext
from attune_project_api import StorageTuple
from attune_project_api.StorageTuple import ItemStorageGroupEnum
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@ObjectStorageContext.registerItemClass
@addTupleType
class ProjectMetadataTuple(StorageTuple):
    __tupleType__ = "attune_auto_project.ProjectMetadataTuple"
    __allowsMultiple__ = False
    __group__ = ItemStorageGroupEnum.Project

    revision: Optional[str] = TupleField(defaultValue="16e34a42a9a1")
    comment: Optional[str] = TupleField()

    @property
    def uuid(self) -> str:
        return self.externalUuid4
