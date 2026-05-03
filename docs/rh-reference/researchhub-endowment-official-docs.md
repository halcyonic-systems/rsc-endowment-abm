# ResearchHub Endowment — Official Documentation

*Source: https://docs.researchhub.com/researchhub/product-features/fund/researchhub-endowment*
*Captured: 2026-04-11*

---

### Summary

ResearchHub Endowment distributes *Funding Credits* to ResearchCoin (RSC) holders. Funding Credits track the price of RSC but can ***only*** be used to fund research—the more RSC you hold, the more science you fund.

No action required: RSC held in a ResearchHub account automatically earns Funding Credits.

### How It Works

1. **Hold ResearchCoin** — Deposit RSC into your ResearchHub account. Principal is revocable.
2. **Earn Credits Automatically** — The RSC you hold earns yield as Funding Credits. Credits are distributed daily.
3. **Fund Science** — Donate the Funding Credits you earned to fund preregistered research proposals.

> **Frictionless UX:** RSC in a ResearchHub account automatically earns Funding Credits. No action, no lockups, no gas fees.

### Practical Example: $1M Endowment

**Traditional grant:** You give $1M once. It funds research. Then it's gone.

**ResearchHub Endowment:**

1. Deposit $1M in ResearchCoin.
2. Year 1: Fund ~$236K of research (at 30% participation scenario).
3. Year 10: Funded ~$1.8M total in cumulative research funding.
4. **Principal: Still yours.**

*Note: Example assumes the USD value of RSC remains unchanged.*

> **One-time capital → Perpetual funding.** This transforms a one-time gift into a perpetual funding vehicle.

### Where Does Yield Come From?

Your yield is determined by the following formula:

**Your Yield = RSC Emissions × (Your Held RSC / Total Held RSC on Platform)**

#### RSC Emissions

The protocol emits new RSC at a decaying rate on an annual basis. Starting at 9.5M RSC in Year 1, emissions halve every 64 years. The emission formula is:

**E(t) = 9,500,000 / 2^(t/64)**

| Time | Annual RSC Emission |
|---|---|
| Year 1 (t=0) | 9,500,000 RSC |
| Year 5 (t=4) | 9,097,231 RSC |
| Year 10 (t=9) | 8,525,000 RSC |
| Year 25 (t=24) | 7,325,501 RSC |

#### Self-Balancing Market Dynamics

The rate of Funding Credit yield depends on the proportion of total circulating supply held within ResearchHub at any given time. When more RSC is held on the platform, the annual return rate decreases. When less RSC is held, yields are higher.

### Yield Across Participation Scenarios

Annual return varies with network participation. Yields are represented as a return rate on the principal per year.

| % Supply Held | Year 1 Yield | Year 5 Yield | Year 25 Yield | Benchmark |
|---|---|---|---|---|
| 15% | 47.2% | 35.4% | 14.5% | Low participation |
| **30%** | **23.6%** | **17.7%** | **7.3%** | **Estimated average** |
| 70% | 10.1% | 7.6% | 3.1% | High participation |

### Credit Distribution Cadence

Funding Credits are distributed on a daily basis. Each day, a proportional share of the annual emission is calculated and credited to all eligible RSC holders based on their balance at the time of distribution.

This daily cadence ensures a smooth, predictable flow of Funding Credits and allows holders to begin funding research almost immediately after depositing RSC.

#### Detailed Example (30% Participation)

**Year 1**

| Participant | RSC Held | Annual Return | Annual Credits |
|---|---|---|---|
| Institution A | 10.0M | 23.6% | 2,360,412 RSC |
| All Other Holders | 30.2M | 23.6% | 7,139,588 RSC |
| **Total Pool** | **40.2M** | | **9,500,000 RSC** |

**Year 25**

| Participant | RSC Held | Annual Return | Annual Credits |
|---|---|---|---|
| Institution A | 10.0M | 7.3% | 726,686 RSC |
| All Other Holders | 90.8M | 7.3% | 6,598,816 RSC |
| **Total Pool** | **100.8M** | | **7,325,501 RSC** |

### Technical Parameters

| Parameter | Value |
|---|---|
| Emission formula | E(t) = 9,500,000 / 2^(t/64) |
| Year 0 emission | 9,500,000 RSC |
| Year 10 emission | ~8,525,000 RSC |
| Halving period | 64 years |
| Reward type | Non-transferable Funding Credits |
| Distribution cadence | Daily |

### Deposit Details

- Supports Base and Ethereum
- Use Base for lower fees
- Only send RSC tokens to deposit address
- Allow 10-20 minutes for processing

---

### Additional context (confirmed independently, not from docs)

- **Researchers receive USD payouts**, not RSC (confirmed with RH leadership 2026-04-10)
- Credits are non-transferable — no sell pressure from yield
- Net effect on liquid RSC supply is deflationary (credits never re-enter circulation as tradeable tokens)
