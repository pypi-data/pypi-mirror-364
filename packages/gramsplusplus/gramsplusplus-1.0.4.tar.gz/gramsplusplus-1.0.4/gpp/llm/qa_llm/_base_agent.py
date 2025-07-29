from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated, Generic, TypeVar

import serde.json
from gpp.llm.qa_llm._input_table import InputTable
from gpp.llm.qa_llm._schema import Schema

R = TypeVar("R")


SourceColumn = Annotated[int, "Source Column Index"]
TargetColumn = Annotated[int, "Target Column Index"]
PropertyId = Annotated[str, "Property ID (e.g., P131)"]
ClassId = Annotated[str, "Class ID (e.g., Q5)"]

CPA = Annotated[
    list[tuple[SourceColumn, TargetColumn, PropertyId]], "Column Property Assignment"
]
CTA = Annotated[dict[SourceColumn, ClassId], "Column Type Assignment"]


class BaseAgent(Generic[R], ABC):

    @abstractmethod
    def query(
        self,
        table: InputTable,
        schema: Schema,
        entity_columns: list[int],
    ) -> R: ...

    @abstractmethod
    def extract(
        self,
        table: InputTable,
        entity_columns: list[int],
        schema: Schema,
        output: R,
        can_ask_for_correction: bool = False,
    ) -> tuple[CTA, CPA]: ...


class PrecomputeAgent(BaseAgent[dict]):
    def __init__(self, input_files: list[Path], outdir: Path):
        self.predictions = {}
        for input_file in input_files:
            for tbl_id, tbl_preds in serde.json.deser(input_file).items():
                tbl_preds["cta"] = {int(k): v for k, v in tbl_preds["cta"].items()}
                assert tbl_id not in self.predictions, (
                    f"Table ID {tbl_id} already exists in predictions. "
                    "Please ensure unique table IDs in the input files."
                )
                self.predictions[tbl_id] = tbl_preds

    def query(
        self,
        table: InputTable,
        schema: Schema,
        entity_columns: list[int],
    ) -> dict:
        return self.predictions[table.id]

    def extract(
        self,
        table: InputTable,
        entity_columns: list[int],
        schema: Schema,
        output: dict,
        can_ask_for_correction: bool = False,
    ) -> tuple[CTA, CPA]:
        cta = {}
        cpa = []
        for col in entity_columns:
            if col in output["cta"]:
                cta[col] = output["cta"][col]
            cpa.extend([x for x in output["cpa"] if x[0] == col])
        return cta, cpa
