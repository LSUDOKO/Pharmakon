"""Pydantic models for LLM outputs and processed tables (see spec/04_ARCHITECTURE.md §3)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SubstanceType = Literal["plant", "mineral", "animal", "compound_preparation", "unknown"]
PlantPart = Literal[
    "root", "leaf", "seed", "fruit", "flower", "bark", "juice/sap", "resin/gum", "whole", "oil", "other"
]
Route = Literal["topical", "oral", "inhaled", "rectal/vaginal", "other"]
ClaimStatus = Literal["ok", "span_mismatch", "ambiguous", "archived"]
Pattern = Literal["persisted", "modified", "lost", "novel"]


class ExtractedClaim(BaseModel):
    """One therapeutic statement, as returned by the extractor (rule-based or LLM)."""

    substance_name_grc: str
    substance_type: SubstanceType = "unknown"
    plant_part: PlantPart | None = None
    preparation: str | None = None
    route: Route | None = None
    condition_text_grc: str
    condition_en: str | None = None
    evidence_span_grc: str
    uncertain_fields: list[str] = Field(default_factory=list)


class ClaimList(BaseModel):
    claims: list[ExtractedClaim] = Field(default_factory=list)


class ConditionProposal(BaseModel):
    """LLM proposal for condition mapping. Names only, never codes (generate-then-verify)."""

    canonical_names_en: list[str] = Field(default_factory=list, max_length=3)
    icpc2_chapter: str | None = None
    no_modern_equivalent: bool = False
    rationale: str = ""


class TraitRecord(BaseModel):
    habit: str | None = None
    height_class: str | None = None
    stem: str | None = None
    leaf: str | None = None
    flower_colour: str | None = None
    flower_shape: str | None = None
    fruit_seed: str | None = None
    root: str | None = None
    smell: str | None = None
    taste: str | None = None
    habitat: str | None = None


class Trait(BaseModel):
    """One morphological trait: controlled values plus the verbatim words that state it."""

    values: list[str] = Field(default_factory=list)
    span: str = ""


class MorphRecord(BaseModel):
    """Trait record for f1 (spec/06). Values come from ``identify.morphology.VOCAB``; null = not stated."""

    habit: Trait | None = None
    life_span: Trait | None = None
    height: Trait | None = None
    stem: Trait | None = None
    leaf_form: Trait | None = None
    leaf_surface: Trait | None = None
    flower_colour: Trait | None = None
    inflorescence: Trait | None = None
    fruit: Trait | None = None
    root: Trait | None = None
    spines: Trait | None = None
    smell: Trait | None = None
    taste: Trait | None = None
    habitat: Trait | None = None


class CandidateProbability(BaseModel):
    candidate: str
    p: float


class JudgeOutput(BaseModel):
    """LLM-judge baseline (spec/06 Option C): probabilities over the given candidates plus 'none'."""

    probabilities: list[CandidateProbability] = Field(default_factory=list)
    p_none_of_these: float = 0.0
    rationale: str = ""


class Claim(BaseModel):
    """Row of ``claims.parquet``."""

    claim_id: str
    passage_id: str
    work: str
    century_ce: int
    substance_name_grc: str
    substance_lemma: str
    substance_type: SubstanceType
    plant_part: PlantPart | None
    preparation: str | None
    route: Route | None
    condition_text_grc: str
    condition_en: str | None
    icpc2_chapter: str | None
    mesh_ids: list[str]
    evidence_span_grc: str
    span_verified: bool
    span_verified_loose: bool
    status: ClaimStatus
    extractor_version: str
    source_id: str
    retrieved_at: str
    method: str


class IdPosterior(BaseModel):
    cluster_id: str
    taxon_key: str
    p: float = Field(ge=0.0, le=1.0)
    p_lo: float = Field(ge=0.0, le=1.0)
    p_hi: float = Field(ge=0.0, le=1.0)
    model_version: str
    calibrated: bool
