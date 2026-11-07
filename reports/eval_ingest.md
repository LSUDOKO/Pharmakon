# Text ingestion

* Dioscorides (Wellmann, First1KGreek commit `da4b902db4989d63d45c87730911a91abb9ea19f`): **1500 passages**, 835 chapters; books present [1, 2, 3, 4, 5]; chapters per book {'1': 132, '2': 186, '3': 159, '4': 193, '5': 165}.
* Headword parsed for 97.6% of chapters; 285 chapters carry `RV:` synonym lists (2014 variants, flagged `synonym_list`).
* Residual-apparatus flag rate after stripping `<note>`/`<del>`: **1.2%** {'sigla': 8, 'editorial_brackets': 7, 'latin_run': 3}.
* 8 chapter divs reuse an earlier `@n` in the TEI (encoding errors); kept and disambiguated as `NdupK`. 207 chapter divs are wrongly nested in the TEI; nested text is excluded from the parent and parsed on its own (unit test).
* Galen *De simpl. med.* books 6–8: 478 passages, 476 drug entries (474 headings parsed).

**20-passage manual comparison with the Perseids reader: pending human check** (links are in the explorer, one per passage).
