"""
*
 *  Copyright AttuneOps HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  AttuneOps HQ Pty Ltd
 *
"""

import logging
from typing import Callable
from typing import List
from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from . import addStepDeclarative
from .step_tuple import StepFieldNeedingSubstitution
from .step_tuple import StepTupleTypeEnum
from ..parameter_tuple import parameterTypeCompatibleWith
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField
from ...StorageTuple import ItemStorageGroupEnum
from ...StorageTuple import StorageMemberTuple

logger = logging.getLogger(__name__)

StepProjectLinkContextGetterC: object = Callable[
    [str, str], ObjectStorageContext
]


@addTupleType
class ParameterMappingTuple(StorageMemberTuple):
    """Step Parameter Mapping Tuple

    Applies to: Project Link Step

    Mapping between a parameter in a linked project to a parameter or a literal
    text value in the linking project. At least one of `parentStaticTextValue` or
    `parentParameterKey` must be set.

    """

    __tupleType__ = "com.servertribe.attune.tuples.ParameterMappingTuple"

    # Literal value for text parameters
    parentStaticTextValue: Optional[str] = TupleField()

    # Key of the parameter or literal value in the linking project
    parentParameterKey: Optional[str] = TupleField()
    parentParameter: Optional[ParameterTuple] = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="parentParameterKey",
        cascadeOnDelete=False,
        cascadeOnUpdate=False,
    )

    # Key of the parameter in the "linked" to projects blueprint
    childProjectUuid: str = TupleField()
    childProjectVersion: Optional[str] = TupleField()
    childParameterUuid: str = TupleField()
    childParameterType: str = TupleField()

    @property
    def childProjectVersionWithDefault(self) -> str:
        return (
            self.childProjectVersion if self.childProjectVersion else "master"
        )

    # These two fields are for debugging / information purposes.
    # Do not rely on them.
    childProjectName: Optional[str] = TupleField()
    childParameterName: Optional[str] = TupleField()

    @property
    def isStaticTextSet(self) -> bool:
        return self.parentStaticTextValue is not None

    @property
    def isParentParameterSet(self) -> bool:
        return self.parentParameterKey is not None


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Project Link")
@addTupleType
class StepProjectLinkTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.PROJECT_LINK.value

    isBlueprint: Optional[bool] = TupleField(defaultValue=False)

    # The details of the project
    projectUuid: str = TupleField()
    cloneUrl: Optional[str] = TupleField()

    # This is either a branch name or tag name
    # In future it may support npm style tags
    projectVersion: str = TupleField()

    @property
    def projectVersionWithDefault(self) -> str:
        return self.projectVersion if self.projectVersion else "master"

    #: The UUID of the blueprint step
    blueprintUuid: str = TupleField()

    # These two fields are for debugging / information purposes.
    # Do not rely on them.
    projectName: Optional[str] = TupleField()
    blueprintName: Optional[str] = TupleField()

    parameterMap: List[ParameterMappingTuple] = TupleField([])

    storageParameters: list[ParameterTuple] = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="parameterMap",
        isList=True,
        cascadeOnDelete=True,
        cascadeOnUpdate=True,
        memberReferenceKeyFieldName="parentParameterKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [
            mapping.parentParameter
            for mapping in self.parameterMap
            if mapping.isParentParameterSet
        ]

    def scriptReferences(self) -> list[str]:
        return []

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        return []

    def verifyParameterMapping(
        self, contextGetter: StepProjectLinkContextGetterC
    ) -> list[int]:
        invalidIndices = set()

        for i, mapping in enumerate(self.parameterMap):

            if not mapping.isStaticTextSet:
                if not mapping.isParentParameterSet:
                    logger.error(
                        f"Project Link Step '{self.name}' / {self.externalUuid4}"
                        f" has a parameter mapping with no parent parameter"
                    )
                    invalidIndices.add(i)
                    continue

                if not self.storageContext.getItem(
                    ItemStorageGroupEnum.Parameter,
                    mapping.parentParameterKey,
                ):
                    logger.error(
                        f"Project Link Step '{self.name}' / {self.externalUuid4}"
                        f" references MISSING PARENT parameter"
                        f" key='{mapping.parentParameterKey}'"
                    )
                    invalidIndices.add(i)
                    continue

            def parentParamDesc():
                if mapping.isStaticTextSet is not None:
                    return f"static text '{mapping.parentStaticTextValue}'"
                else:
                    return (
                        f"parameter '{mapping.parentParameter.name}'"
                        f" of type {mapping.parentParameter.type}"
                    )

            if not (
                mapping.childProjectUuid
                and mapping.childProjectVersionWithDefault
            ):
                logger.error(
                    f"Project Link Step '{self.name}' / {self.externalUuid4}"
                    f" {parentParamDesc()}"
                    f" references MISSING CHILD parameter project"
                    f" {mapping.childProjectUuid}:"
                    f"{mapping.childProjectVersionWithDefault}' "
                )
                invalidIndices.add(i)
                continue

            try:
                childParamContext = contextGetter(
                    mapping.childProjectUuid,
                    mapping.childProjectVersionWithDefault,
                )
            except Exception as e:
                logger.error(
                    f"Project Link Step '{self.name}' / {self.externalUuid4}"
                    f" {parentParamDesc()}"
                    f" references ERRORED CHILD parameter project"
                    f" that can't load - Error: {e}"
                )
                invalidIndices.add(i)
                continue

            from attune_project_api.Exceptions import ItemNotFoundError

            try:
                childParam = childParamContext.getItemForExternalUuid(
                    ItemStorageGroupEnum.Parameter, mapping.childParameterUuid
                )

            except ItemNotFoundError:
                logger.error(
                    f"Project Link Step '{self.name}' / {self.externalUuid4}"
                    f" {parentParamDesc()}"
                    f" references MISSING CHILD parameter"
                    f" child parameter name"
                    f"='{mapping.childParameterName}' "
                    f" child parameter externalUuid4"
                    f"={mapping.childParameterUuid} "
                )
                invalidIndices.add(i)
                continue

            if (
                mapping.isParentParameterSet
                and mapping.parentParameter
                and mapping.parentParameter.type
                not in parameterTypeCompatibleWith.get(childParam.type, set())
            ):
                logger.error(
                    f"Project Link Step '{self.name}' / {self.externalUuid4}"
                    f" {parentParamDesc()}"
                    f" is not compatible with child parameter"
                    f" '{mapping.childParameterName}' of type"
                    f" {mapping.childParameterType}"
                )
                invalidIndices.add(i)
                continue

            if (
                mapping.isStaticTextSet
                and childParam.type != ParameterTuple.TEXT
            ):
                logger.error(
                    f"Project Link Step '{self.name}' / {self.externalUuid4}"
                    f" {parentParamDesc()}"
                    f" is not compatible with child parameter"
                    f" '{mapping.childParameterName}' of type"
                    f" {mapping.childParameterType}"
                    f" For static text mapping, it must be of type TEXT"
                )
                invalidIndices.add(i)
                continue

        return list(invalidIndices)
