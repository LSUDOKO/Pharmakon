"""Conditional logit with an explicit "none of the candidates" (∅) alternative (spec/06 §3 Option A).

U(n, s) = wᵀ z(n, s);  U(n, ∅) = b;  P(· | n) = softmax over C_n ∪ {∅}.
Fitted by L2-regularised maximum likelihood (L-BFGS, analytic gradient). ~8 parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import minimize, minimize_scalar


@dataclass
class Unit:
    uid: str
    X: np.ndarray  # (n_candidates, k)
    y: np.ndarray  # target distribution over candidates + ∅ (length n+1), sums to 1
    taxa: list[str] = field(default_factory=list)


@dataclass
class CLogit:
    l2: float = 1.0
    w: np.ndarray | None = None
    b: float = 0.0
    mu: np.ndarray | None = None
    sd: np.ndarray | None = None
    T: float = 1.0

    def _z(self, X: np.ndarray) -> np.ndarray:
        assert self.mu is not None and self.sd is not None
        return (X - self.mu) / self.sd

    def utilities(self, X: np.ndarray) -> np.ndarray:
        assert self.w is not None
        return np.append(self._z(X) @ self.w, self.b)

    def predict(self, X: np.ndarray, temperature: float | None = None) -> np.ndarray:
        u = self.utilities(X) / (temperature if temperature is not None else self.T)
        u = u - u.max()
        e = np.exp(u)
        return e / e.sum()

    def contributions(self, X: np.ndarray) -> np.ndarray:
        assert self.w is not None
        return self._z(X) * self.w

    def fit(self, units: list[Unit]) -> CLogit:
        allX = np.vstack([u.X for u in units if len(u.X)])
        self.mu = allX.mean(axis=0)
        sd = allX.std(axis=0)
        self.sd = np.where(sd > 1e-9, sd, 1.0)
        k = allX.shape[1]
        # Flatten: every unit contributes its candidate rows + one ∅ row (zero features, flag 1).
        Z = np.vstack([np.vstack([self._z(u.X), np.zeros((1, k))]) for u in units])
        is_none = np.concatenate([np.append(np.zeros(len(u.X)), 1.0) for u in units])
        Y = np.concatenate([u.y for u in units])
        seg = np.concatenate([np.full(len(u.X) + 1, i) for i, u in enumerate(units)])
        starts = np.concatenate([[0], np.cumsum([len(u.X) + 1 for u in units])[:-1]])

        def nll(theta: np.ndarray) -> tuple[float, np.ndarray]:
            w, b = theta[:k], theta[k]
            util = Z @ w + b * is_none
            mx = np.maximum.reduceat(util, starts)[seg]
            e = np.exp(util - mx)
            p = e / np.add.reduceat(e, starts)[seg]
            loss = -float(Y @ np.log(p + 1e-12)) + self.l2 * float(w @ w)
            d = p - Y
            return loss, np.append(Z.T @ d + 2 * self.l2 * w, float(d @ is_none))

        res = minimize(nll, np.zeros(k + 1), jac=True, method="L-BFGS-B")
        self.w, self.b = res.x[:k], float(res.x[k])
        return self

    def fit_temperature(self, units: list[Unit], logits: list[np.ndarray]) -> float:
        """Temperature scaling on held-out utilities (fitted inside the training fold)."""

        def nll(T: float) -> float:
            tot = 0.0
            for u, lg in zip(units, logits, strict=True):
                z = lg / T
                z = z - z.max()
                p = np.exp(z) / np.exp(z).sum()
                tot -= float(u.y @ np.log(p + 1e-12))
            return tot

        r = minimize_scalar(nll, bounds=(0.25, 8.0), method="bounded")
        self.T = float(r.x)
        return self.T


# ---- metrics ---------------------------------------------------------------------------------


def unit_metrics(p: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Metrics for one name. ``y`` marks the expert-correct set (uniform over ties)."""
    correct = y > 0
    order = np.argsort(-p)
    ranks = np.where(correct[order])[0]
    first = int(ranks[0]) + 1 if len(ranks) else len(p) + 1
    target = correct.astype(float)
    return {
        "top1": float(correct[order[0]]),
        "top3": float(correct[order[:3]].any()),
        "rr": 1.0 / first,
        "logloss": float(-np.log(p[correct].sum() + 1e-12)),
        "brier": float(((p - target / max(target.sum(), 1)) ** 2).sum()),
        "conf": float(p.max()),
        "p_correct_set": float(p[correct].sum()),
    }


def ece(conf: np.ndarray, hit: np.ndarray, bins: int = 10) -> tuple[float, list[dict]]:
    edges = np.linspace(0, 1, bins + 1)
    tot, rows = 0.0, []
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        m = (conf > lo) & (conf <= hi) if lo > 0 else (conf >= lo) & (conf <= hi)
        if m.sum() == 0:
            continue
        acc, c = float(hit[m].mean()), float(conf[m].mean())
        tot += m.sum() / len(conf) * abs(acc - c)
        rows.append({"bin_lo": round(float(lo), 2), "bin_hi": round(float(hi), 2), "n": int(m.sum()), "mean_conf": c, "accuracy": acc})
    return float(tot), rows


def bootstrap_ci(values: np.ndarray, n: int = 1000, seed: int = 13, stat=np.mean) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(n, len(values)))
    s = np.array([stat(values[i]) for i in idx])
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))
