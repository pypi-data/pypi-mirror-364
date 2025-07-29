from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from attune_project_api import ObjectStorageContext
from attune_project_api import ParameterTuple
from attune_project_api.items import NotZeroLenStr
from attune_project_api.items.step_tuples import addStepDeclarative
from attune_project_api.items.step_tuples import extractScriptReferences
from attune_project_api.items.step_tuples.step_ssh_tuple import StepSshTuple
from attune_project_api.items.step_tuples.step_tuple import (
    StepFieldNeedingSubstitution,
)
from attune_project_api.items.step_tuples.step_tuple import StepTupleTypeEnum


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Linux Script With Responses")
@addTupleType
class StepSshPromptedTuple(StepSshTuple):
    __tupleType__ = StepTupleTypeEnum.SSH_PROMPTED.value

    promptResponses: NotZeroLenStr = TupleField()

    def parameters(self) -> list["ParameterTuple"]:
        return StepSshTuple.parameters(self)

    def scriptReferences(self) -> list[str]:
        return StepSshTuple.scriptReferences(self) + extractScriptReferences(
            self.promptResponses
        )

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        results = StepSshTuple.fieldsNeedingSubstitutions(self)
        results.append(
            StepFieldNeedingSubstitution(
                fieldName="promptResponses",
                displayName="Prompt Responses",
                value=self.promptResponses,
                isScriptReference=False,
                order=len(results),
            )
        )
        return results
