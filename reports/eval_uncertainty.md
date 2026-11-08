# Does identification uncertainty change the ranking? (RQ4)

* Unsupported candidate pairs ranked: 1781.
* Kendall τ between P(species)-weighted ranking and top-1-identity ranking: **0.4986**.
* Top-20 leads that change when only the top-1 identity is used: **5**.
* Top-20 leads resting on P(species) < 0.5: 2.
* Top-20 with a known-toxicity flag: 7; with a closed compound→target→disease path: 16.

Closed compound→target→disease paths: 385 taxon–condition pairs have a path (120-taxon linking cap, all use groups); 385 of them fall in the 400-pair skin pilot; 288 of 1781 leads carry one. Path strength is shown with each lead but is not a ranking input (only dated compound counts enter the model), so path-bearing leads need not rank high.

Full table: `leads_top50.md`.
