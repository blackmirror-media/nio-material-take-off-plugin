"""
Pydantic models mirroring the CompleteModel JSON emitted by
`mto build-model`. The .NET side serializes record-struct members with
PascalCase names; the Python models use idiomatic snake_case attributes
with aliases so both sides validate the same payload.

Validation errors surface with full field paths — much better than a
KeyError mid-render.
"""

from __future__ import annotations

from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

T = TypeVar("T")


def _none_to_empty(v: Any) -> Any:
    return [] if v is None else v


# A list field that tolerates a JSON null in place of an empty list — the
# .NET serializer sometimes emits null for empty collections.
def NoneTolerantList(item_type: type[T]) -> Any:  # noqa: N802
    return Annotated[list[item_type], BeforeValidator(_none_to_empty)]


class _Model(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        frozen=True,
    )


class Project(_Model):
    name: str | None = Field(default=None, alias="Name")
    description: str | None = Field(default=None, alias="Description")
    buildings: NoneTolerantList(str) = Field(default_factory=list, alias="Buildings")
    organisation: str | None = Field(default=None, alias="Organisation")


class Volume(_Model):
    name: str | None = Field(default=None, alias="Name")
    unit: str | None = Field(default=None, alias="Unit")
    value: float = Field(alias="Value")
    definition: str | None = Field(default=None, alias="Definition")


class Area(_Model):
    name: str | None = Field(default=None, alias="Name")
    unit: str | None = Field(default=None, alias="Unit")
    value: float = Field(alias="Value")


class Weight(_Model):
    name: str | None = Field(default=None, alias="Name")
    unit: str | None = Field(default=None, alias="Unit")
    value: float = Field(alias="Value")


class Lengths(_Model):
    width: float | None = Field(default=None, alias="Width")
    length: float | None = Field(default=None, alias="Length")
    depth: float | None = Field(default=None, alias="Depth")
    unit: str = Field(default="", alias="Unit")


class Quantities(_Model):
    number_of_pieces: float | None = Field(default=None, alias="NumberOfPieces")
    volumes: NoneTolerantList(Volume) = Field(default_factory=list, alias="Volumes")
    areas: NoneTolerantList(Area) = Field(default_factory=list, alias="Areas")
    weights: NoneTolerantList(Weight) = Field(default_factory=list, alias="Weights")
    lengths: Lengths | None = Field(default=None, alias="Lengths")


class MaterialQuantities(_Model):
    reference_quantity: float = Field(alias="ReferenceQuantity")
    reference_unit: str = Field(alias="ReferenceUnit")
    bulk_density: float | None = Field(default=None, alias="BulkDensity")
    areal_density: float | None = Field(default=None, alias="ArealDensity")
    density: float | None = Field(default=None, alias="Density")
    layer_thickness: float | None = Field(default=None, alias="LayerThickness")
    coverage: float | None = Field(default=None, alias="Coverage")
    linear_density: float | None = Field(default=None, alias="LinearDensity")
    unit_weight: float | None = Field(default=None, alias="UnitWeight")


class MaterialOkobaudat(_Model):
    uuid: str = Field(alias="Uuid")
    name: str = Field(alias="Name")
    category: str = Field(alias="Category")
    embodied_carbon: float = Field(alias="EmbodiedCarbon")
    whole_life_carbon: float = Field(alias="WholeLifeCarbon")
    carbon_unit: str = Field(alias="CarbonUnit")
    conformity: str = Field(alias="Conformity")
    country_code: str = Field(alias="CountryCode")
    url: str = Field(alias="Url")
    quantities: MaterialQuantities = Field(alias="Quantities")
    calculation_basis: str = Field(alias="CalculationBasis")


class Lca(_Model):
    reference_quantity: str | None = Field(default=None, alias="ReferenceQuantity")
    embodied_carbon: float | None = Field(default=None, alias="EmbodiedCarbon")
    whole_life_carbon: float | None = Field(default=None, alias="WholeLifeCarbon")


class Material(_Model):
    name: str = Field(alias="Name")
    description: str | None = Field(default=None, alias="Description")
    parent_name: str | None = Field(default=None, alias="ParentName")
    category: str | None = Field(default=None, alias="Category")
    fraction_of_total: float | None = Field(default=None, alias="FractionOfTotal")
    representation_type: str = Field(alias="RepresentationType")
    quantities: Quantities | None = Field(default=None, alias="Quantities")
    okobaudat: MaterialOkobaudat | None = Field(default=None, alias="Okobaudat")
    lca: list[Lca] | None = Field(default=None, alias="Lca")


class Element(_Model):
    guid: str = Field(alias="Guid")
    name: str | None = Field(default=None, alias="Name")
    type: str | None = Field(default=None, alias="Type")
    quantities: Quantities = Field(alias="Quantities")
    materials: NoneTolerantList(Material) = Field(
        default_factory=list, alias="Materials"
    )


class MaterialGroup(_Model):
    name: str = Field(alias="Name")
    category: str = Field(default="", alias="Category")
    okobaudat: MaterialOkobaudat | None = Field(default=None, alias="Okobaudat")
    aggregated_quantities: Quantities | None = Field(
        default=None, alias="AggregatedQuantities"
    )
    aggregated_lca: list[Lca] | None = Field(default=None, alias="AggregatedLca")


class Warning(_Model):
    code: str = Field(alias="Code")
    level: str = Field(alias="Level")
    message: str = Field(alias="Message")
    context: dict[str, Any] | None = Field(default=None, alias="Context")


class MaterialMatch(_Model):
    ifc_material_name: str = Field(alias="IfcMaterialName")
    okobaudat: MaterialOkobaudat | None = Field(default=None, alias="Okobaudat")
    confidence: str | None = Field(default=None, alias="Confidence")
    rationale: str | None = Field(default=None, alias="Rationale")


class CompleteModel(_Model):
    project: Project = Field(alias="Project")
    elements: NoneTolerantList(Element) = Field(default_factory=list, alias="Elements")
    material_groups: NoneTolerantList(MaterialGroup) = Field(
        default_factory=list, alias="MaterialGroups"
    )
    warnings: NoneTolerantList(Warning) = Field(default_factory=list, alias="Warnings")
    match_decisions: NoneTolerantList(MaterialMatch) = Field(
        default_factory=list, alias="MatchDecisions"
    )
