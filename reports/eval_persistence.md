# Persistence (DMM → Galen → John the Physician → modern Greek)

* Rows (name × Lardos use group): 1533 over 300 names with ≥1 verified candidate taxon.
* Pattern counts: {'lost': 499, 'novel': 387, 'modified': 261, 'persisted': 247, 'persisted_to_galen_only': 130, 'persisted_to_byzantine_only': 9}
* Dermatology (pilot): {'lost': 77, 'persisted': 74, 'persisted_to_galen_only': 51, 'novel': 20, 'modified': 13}
* Galen re-attests 0.371 of Dioscorides uses for the 146 linked names; John the Physician 0.3388 (46 linked names).
* Mean persistence score with / without Galen: 0.223 / 0.1676. Copy detection: Galen entries down-weighted to 0.5 when word-4-gram containment in the matched Dioscorides chapter > 0.15; Paul of Aegina not ingested.
* Modern records: 1226 from {'lardos': 919, 'eth_naegean': 241, 'eth_pelion': 66}.

## Permutation null

```json
{
 "observed_persisted_share": 0.4862,
 "null_mean": 0.4078,
 "null_95pct": 0.4331,
 "p_value": 0.001,
 "n_permutations": 1000,
 "n_rows": 508,
 "denominator": "DMM (name, use group) rows whose plant is attested in the modern record (E>=0.5)"
}
```
Interpretation: among Dioscorides uses whose plant appears in the modern record, the same use group recurs more often than when modern use labels are shuffled across records. Caveat: the Pelion study covers skin ailments only, which inflates DE attestation.

## Worked examples (dermatology, with verbatim Greek)

* **cl:dmm:2.126** — score 0.9802, E[modern] 0.9405, Galen True, JC True — `dmm:2.126.2`
  > δύναμιν δὲ ἔχει τὰ φύλλα στυπτικήν ξηραντικήν ὅθεν καταπλασσόμενα πρὸς πάντα τὰ κακοήθη καὶ ἐλεφαντιῶντας καὶ ῥευματικὰ καὶ ἀκάθαρτα ἕλκη ἁρμόζει.
* **cl:dmm:2.166** — score 0.977, E[modern] 0.931, Galen True, JC True — `dmm:2.166.1`
  > δύναμιν δὲ ἔχει ὁ καρπὸς χυλισθεὶς καὶ ἐγχυματισθεὶς μετ᾿ ἐλαίου εἰς τὸ οὖς ὠταλγίαν παύειν, εἰς δὲ τὰς ῥῖνας ἐντιθέμενος ἐν ἐρίῳ πώλυπας δαπανᾶν, καταχριόμενος δὲ στέλλειν καὶ καρκινώματα.
* **cl:dmm:3.4** — score 0.9741, E[modern] 0.9483, Galen True, JC None — `dmm:3.4.5`
  > ἀνάγει δὲ σκόλοπας, ἀκίδας ⟨καὶ⟩ λεπίδας ὀστῶν καταπλασσομένη ἀφίστησι καὶ σηπεδόνας περιχαράσσει καὶ τὰ ῥυπαρὰ περικαθαίρει ἕλκη καὶ τὰ κοῖλα πληροῖ σὺν ἴριδι καὶ μέλιτι·
* **cl:dmm:2.169** — score 0.9736, E[modern] 0.9209, Galen True, JC True — `dmm:2.169.1`
  > κινοῦσι δὲ καὶ οὔρησιν καὶ ἔμμηνα ποθεῖσαι, ἰῶνται καὶ πλευρᾶς ἀλγήματα καὶ βῆχας καὶ σπάσματα καὶ δήγματα δραχμῆς μιᾶς τὸ πλῆθος τῆς ῥίζης ἐν οἴνῳ πινομένης.
* **cl:dmm:4.68** — score 0.9626, E[modern] 0.9252, Galen None, JC True — `dmm:4.68.4`
  > πρός τε ὀφθαλμῶν φλεγμονὰς καὶ ποδῶν καὶ τὰς ἄλλας φλεγμονάς·
