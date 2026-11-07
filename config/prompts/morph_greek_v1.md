You read one chapter of Dioscorides' De materia medica (Greek, Wellmann edition) and record what the TEXT says about the plant's appearance, so that it can later be compared with modern botanical descriptions.

Return ONLY a JSON object with these keys; each value is either null or {"values": [...], "span": "..."}:

- habit: herb, subshrub, shrub, tree, climber, aquatic, grass_like, fern, bulbous, succulent
- life_span: annual, biennial, perennial
- height: low, medium, tall
- stem: woody, herbaceous, hollow, angular, hairy, smooth, branched, unbranched, creeping
- leaf_form: entire, toothed, lobed, finely_divided, compound, linear_grasslike, needle_scale, absent, large, small
- leaf_surface: hairy, smooth, rough, fleshy, grey_silvery, dark_green, sticky
- flower_colour: white, yellow, red_pink, purple_blue, green, brown
- inflorescence: umbel, head_composite, spike, raceme_cluster, solitary, catkin
- fruit: berry_fleshy, pod_legume, capsule, nut_acorn, small_seeds, winged, burr_prickly, cone, pome_drupe
- root: bulb_tuber, thick_fleshy, fibrous, woody, long_taproot, aromatic_root
- spines: spiny, unarmed
- smell: aromatic, foul, pungent
- taste: bitter, sweet, pungent_sharp, astringent, sour, salty
- habitat: wet_marsh, rocky_mountain, coastal_sandy, cultivated_garden, woodland_shade, field_roadside, walls_ruins

Height classes: low < 0.3 m, medium 0.3–1.5 m, tall > 1.5 m (a πῆχυς is about 0.46 m, a σπιθαμή about 0.23 m, a δάκτυλος about 2 cm).

Rules:
- Use ONLY what this passage states. Do not use what you know about the plant or its modern identification; never guess a species.
- "span" must be an EXACT contiguous substring of the passage (copy it character for character, accents included) containing the words that state the trait.
- "values" must come from the list for that key; give several only if the text states several (e.g. two colours).
- Similes count when they describe the plant's own form (e.g. leaves "like the olive's" = entire, narrow).
- If the text does not describe a trait, set it to null. Many chapters describe only uses: then most keys are null.
- Ignore descriptions of other plants mentioned for comparison, of preparations, and of the remedy's effects.
