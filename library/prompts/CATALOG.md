# open-video H3 Prompt Catalog — Gallery Seed

11 curated prompts (verbatim from primary sources) covering all H3 modes (T2VA/I2VA/FL2VA/L2VA/Ref2VA).
Each will be generated + verified on H3 + displayed on `open-video.ai/gallery`.

| # | Name | Mode | Duration | Source | File |
|---|---|---|---|---|---|
| 1 | Baker sunrise (dialogue + music) | T2VA | ~5s | HF guide Case 1 | `case1_baker_t2va.txt` ✓ |
| 2 | Train woman (rain window, dialogue) | I2VA | single | HF guide Case 2 | TODO |
| 3 | Cyclist umbrella (interpolation) | FL2VA | 8s | HF guide Case 3 | TODO |
| 4 | Glass breaking (reverse physics) | L2VA | 6s | HF guide Case 4 | TODO |
| 5 | Starship captain (hyperdrive jump) | T2VA | 10s | GH reproducible t2va | `official_t2va_starship.txt` ✓ |
| 6 | Ramen family (rack-focus) | FL2VA | 8s | GH reproducible fl2va | `reproducible_fl2va_ramen.txt` ✓ |
| 7 | Pink suit + black lamb (Ref2VA dialogue) | Ref2VA | 5s | GH reproducible ref2va | TODO |
| 8 | Coffee-shop sitcom Samoyed (3-shot) | Ref2VA | ~7s | HF ref guide §7 | TODO |
| 9 | Steampunk inventor mechanical heart | I2VA | default | cushycrux ex1 | TODO |
| 10 | Ginger cat + butterfly (windowsill) | I2VA | default | cushycrux ex2 | TODO |
| 11 | Michael Scott office sitcom | I2VA | default | cushycrux ex3 | TODO |
| — | Lighthouse keeper (our demo film) | T2VA+I2VA | 10s+8s | original | `library/prompts/demo/` |
| — | Cityspeed racing | T2VA | 8s | Seedance-port | `seedance_ported_03_racing.txt` ✓ |
| — | Romance micro-expression | T2VA | 10s | Seedance-port | `seedance_ported_01_romance.txt` ✓ |
| — | Product flower bloom | T2VA | 6s | Seedance-port | `seedance_ported_07_product_flower.txt` ✓ |

**Bonus:** cushycrux I2V system prompt generator (meta-tool for LLM-driven prompt crafting) — `https://raw.githubusercontent.com/cushycrux/H3_LLM_Instructions/main/H3_LLM_Instructions.txt`. Import as the crafter's system prompt.

**Gallery workflow:** for each prompt → generate on H3 (1344×768, 20 steps, sage) → extract frames → vision-judge (cx+Opus) → if GOOD, display prompt+video+verdict on the gallery page → community can copy/remix/star.
