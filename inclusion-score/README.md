# Verification of inclusion scores based on chain data.

- I calculated the (span)inclusion score based on on-chain era reward points. Then compared to the ones reported by the 1kv backend. There are very big 
differences! **Which means many of us do not have the correct score, and thus are missing out on nominations.**

- You can see for yourself: https://github.com/MathCryptoDoc/dotsama-snippets/tree/main/inclusion-score/figs/kusama . Just find your stash.

- For example, one of my validators has [not been active for over 12 
days](https://kusama.subscan.io/validator/EARQCUK4Y3oN3LCuyjriBxPesNAuQWa7ifjsfNSU6srpFAq?tab=era). Its span inclusion score should clearly be 100 (28 eras 
= 4.6 days). Also the inclusion score (84 eras = 14 days) should be close to 100. From the figure, we see that 1kv does not have the correct score:
 
![figure](https://github.com/MathCryptoDoc/dotsama-snippets/blob/main/inclusion-score/figs/kusama/EARQCUK4Y3oN3LCuyjriBxPesNAuQWa7ifjsfNSU6srpFAq.png)

- Maybe there is an error in my calculations. The scores are calculated based on quantiles of everyone's inclusion. However, the scores were mostly correct 
until 9 Sept. So something must be right.
