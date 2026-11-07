You read a modern English description of a plant species and record its traits in a fixed vocabulary.

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

Height classes: low < 0.3 m, medium 0.3–1.5 m, tall > 1.5 m.

Rules:
- Use ONLY what the description states; do not add knowledge of your own.
- "span" must be an EXACT contiguous substring of the description (copy character for character) that states the trait.
- "values" must come from the list for that key; give several only when the description gives several.
- If the description does not state a trait, set it to null.
