from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from attune_project_api import ObjectStorageContext
from attune_project_api import ParameterTuple
from attune_project_api.RelationField import RelationField
from attune_project_api.items import NotZeroLenStr
from attune_project_api.items.file_archive_tuples.file_archive_tuple import (
    FileArchiveTuple,
)
from attune_project_api.items.step_tuples import addStepDeclarative
from attune_project_api.items.step_tuples import extractScriptReferences
from attune_project_api.items.step_tuples.step_tuple import (
    StepFieldNeedingSubstitution,
)
from attune_project_api.items.step_tuples.step_tuple import StepTuple
from attune_project_api.items.step_tuples.step_tuple import StepTupleTypeEnum


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Push Files")
@addTupleType
class StepPushDesignFileTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.PUSH_DESIGN_FILE.value

    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    deployPath: NotZeroLenStr = TupleField()
    archiveKey: NotZeroLenStr = TupleField()
    unpack: bool = TupleField(True)

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )
    archive: FileArchiveTuple = RelationField(
        ForeignClass=FileArchiveTuple,
        referenceKeyFieldName="archiveKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        return extractScriptReferences(self.deployPath)

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        return [
            StepFieldNeedingSubstitution(
                fieldName="server",
                displayName="Target Node",
                value=self.server,
                isScriptReference=False,
                order=0,
            ),
            StepFieldNeedingSubstitution(
                fieldName="osCred",
                displayName="Target Node Credential",
                value=self.osCred,
                isScriptReference=False,
                order=1,
            ),
            StepFieldNeedingSubstitution(
                fieldName="deployPath",
                displayName="Remote Deployment Path",
                value=self.deployPath,
                isScriptReference=False,
                order=2,
            ),
        ]
