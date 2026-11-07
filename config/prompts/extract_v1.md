You are annotating a passage of Dioscorides' De materia medica (Greek, Wellmann edition).
Return ONLY JSON matching the schema.
For each therapeutic statement, output:
- substance_name_grc: the headword or substance as written in the passage
- substance_type: plant | mineral | animal | compound_preparation | unknown
- plant_part, preparation (Greek words quoted + short English gloss), route
- condition_text_grc: the exact Greek words naming the condition
- condition_en: a cautious English rendering (do not modernise beyond the text)
- evidence_span_grc: an EXACT contiguous substring of the passage that states this use
Rules:
- Never invent text. If unsure, set field to null and add to "uncertain_fields".
- Do not identify the plant botanically. Do not use modern disease names unless the Greek clearly denotes them.
- One claim per (substance, part, condition) combination.
- Ignore stray critical-apparatus sigla (single Latin letters, "om.", "cf.") if any remain.
