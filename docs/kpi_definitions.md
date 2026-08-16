# KPI definition sheet

| KPI | Controlled benchmark definition | Direction | Target | Important limitation |
|---|---|---:|---:|---|
| Auto-match rate | Auto-matched valid payments / valid payment records | Higher | 78% | Duplicate records excluded from denominator |
| Manual-review rate | Payment records in manual review / all payment records | Lower | 22% | Includes detected duplicates because a steward must review them |
| Unapplied cash | Sum of valid payment residuals translated to USD | Lower | $125,000 | Overpayment residuals remain unapplied by design |
| DSO | Ending AR / synthetic benchmark-period credit sales × 90 days | Lower | 48 days | A controlled implementation indicator, not published customer DSO |
| CEI | (Beginning AR + credit sales − ending AR) / (Beginning AR + credit sales − current AR) | Higher | 82% | Capped to 0–100%; depends on synthetic aging mix |
| Past-due AR | Past-due ending AR / ending AR | Lower | 30% | Uses configured as-of date and canonical due dates |
| Processing time | Auto and manual record counts × configured handling minutes | Lower | 25 hours | Modeled effort, not stopwatch observation |

Targets are configuration inputs. A missed target is retained on the dashboard and affects go-live readiness; it is not rewritten after seeing the output.

