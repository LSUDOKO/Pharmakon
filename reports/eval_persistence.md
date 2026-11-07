# Persistence (DMM → Galen → John the Physician → modern Greek)

* Rows (name × Lardos use group): 1295 over 268 names with ≥1 verified candidate taxon.
* Pattern counts: {'novel': 396, 'lost': 375, 'modified': 211, 'persisted': 203, 'persisted_to_galen_only': 101, 'persisted_to_byzantine_only': 9}
* Dermatology (pilot): {'persisted': 67, 'lost': 65, 'persisted_to_galen_only': 43, 'novel': 23, 'modified': 11, 'persisted_to_byzantine_only': 1}
* Galen re-attests 0.3858 of Dioscorides uses for the 138 linked names; John the Physician 0.3618 (45 linked names).
* Mean persistence score with / without Galen: 0.232 / 0.1764. Copy detection: Galen entries down-weighted to 0.5 when word-4-gram containment in the matched Dioscorides chapter > 0.15; Paul of Aegina not ingested.
* Modern records: 1226 from {'lardos': 919, 'eth_naegean': 241, 'eth_pelion': 66}.

## Permutation null

```json
{
 "observed_persisted_share": 0.4903,
 "null_mean": 0.405,
 "null_95pct": 0.4324,
 "p_value": 0.001,
 "n_permutations": 1000,
 "n_rows": 414,
 "denominator": "DMM (name, use group) rows whose plant is attested in the modern record (E>=0.5)"
}
```
Interpretation: among Dioscorides uses whose plant appears in the modern record, the same use group recurs more often than when modern use labels are shuffled across records. Caveat: the Pelion study covers skin ailments only, which inflates DE attestation.

## Worked examples (dermatology, with verbatim Greek)

* **cl:dmm:2.126** — score 0.9811, E[modern] 0.9433, Galen True, JC True — `dmm:2.126.2`
  > δύναμιν δὲ ἔχει τὰ φύλλα στυπτικήν ξηραντικήν ὅθεν καταπλασσόμενα πρὸς πάντα τὰ κακοήθη καὶ ἐλεφαντιῶντας καὶ ῥευματικὰ καὶ ἀκάθαρτα ἕλκη ἁρμόζει.
* **cl:dmm:3.4** — score 0.9773, E[modern] 0.9546, Galen True, JC None — `dmm:3.4.5`
  > ἀνάγει δὲ σκόλοπας, ἀκίδας ⟨καὶ⟩ λεπίδας ὀστῶν καταπλασσομένη ἀφίστησι καὶ σηπεδόνας περιχαράσσει καὶ τὰ ῥυπαρὰ περικαθαίρει ἕλκη καὶ τὰ κοῖλα πληροῖ σὺν ἴριδι καὶ μέλιτι·
* **cl:dmm:2.166** — score 0.9773, E[modern] 0.932, Galen True, JC True — `dmm:2.166.1`
  > δύναμιν δὲ ἔχει ὁ καρπὸς χυλισθεὶς καὶ ἐγχυματισθεὶς μετ᾿ ἐλαίου εἰς τὸ οὖς ὠταλγίαν παύειν, εἰς δὲ τὰς ῥῖνας ἐντιθέμενος ἐν ἐρίῳ πώλυπας δαπανᾶν, καταχριόμενος δὲ στέλλειν καὶ καρκινώματα.
* **cl:dmm:2.169** — score 0.9751, E[modern] 0.9252, Galen True, JC True — `dmm:2.169.1`
  > κινοῦσι δὲ καὶ οὔρησιν καὶ ἔμμηνα ποθεῖσαι, ἰῶνται καὶ πλευρᾶς ἀλγήματα καὶ βῆχας καὶ σπάσματα καὶ δήγματα δραχμῆς μιᾶς τὸ πλῆθος τῆς ῥίζης ἐν οἴνῳ πινομένης.
* **cl:dmm:2.176** — score 0.9569, E[modern] 0.9138, Galen True, JC None — `dmm:2.176.2`
  > καὶ μασηθεῖσα δὲ ἡ ῥίζα ἄγει φλέγμα, ἑψηθεῖσα δὲ ἐν γλυκεῖ καὶ καταπλασσομένη ὀφθαλμῶν φλεγμονὰς ἰᾶται καὶ τὰς ἐν ὀφθαλμοῖς οὐλὰς ἀποσμᾷ·
