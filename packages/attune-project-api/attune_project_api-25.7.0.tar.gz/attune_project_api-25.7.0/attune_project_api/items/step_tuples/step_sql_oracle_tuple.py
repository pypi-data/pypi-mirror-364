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

from typing import Optional

from attune_project_api.items import NotZeroLenStr
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from . import addStepDeclarative
from . import extractScriptReferences
from .step_tuple import StepFieldNeedingSubstitution
from .step_tuple import StepTuple
from .step_tuple import StepTupleTypeEnum
from ... import ParameterTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Linux Oracle SQL")
@addTupleType
class StepSqlOracleTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.SQL_ORACLE.value

    sql: NotZeroLenStr = TupleField()
    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    sqlCredKey: NotZeroLenStr = TupleField()
    plsql: bool = TupleField(defaultValue=False)
    commit: bool = TupleField(defaultValue=True)
    acceptOraErrors: Optional[str] = TupleField()

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )
    sqlCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="sqlCredKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred, self.sqlCred]

    def scriptReferences(self) -> list[str]:
        return extractScriptReferences(self.sql)

    def fieldsNeedingSubstitutions(
        self,
    ) -> list[StepFieldNeedingSubstitution]:
        return [
            StepFieldNeedingSubstitution(
                fieldName="server",
                displayName="Target SSH Node",
                value=self.server,
                isScriptReference=False,
                order=0,
            ),
            StepFieldNeedingSubstitution(
                fieldName="osCred",
                displayName="SSH Credential",
                value=self.osCred,
                isScriptReference=False,
                order=1,
            ),
            StepFieldNeedingSubstitution(
                fieldName="sqlCred",
                displayName="Oracle SQL Credential",
                value=self.sqlCred,
                isScriptReference=False,
                order=2,
            ),
            StepFieldNeedingSubstitution(
                fieldName="sql",
                displayName="SQL / PLSql",
                value=self.sql,
                isScriptReference=True,
                order=3,
            ),
        ]
