# socialwork-telegram-analysis

Scripts and aggregated outputs for a computational text analysis of messages from an online social work community in Türkiye (2020–2026).

This repository is the replication package for the article. It contains every script used in the analysis, the aggregated outputs on which the reported figures rest, the codebook used for human coding, and the stop-word list. It does not contain the messages themselves; the reasons are set out below.

## The article

**Employment, Peer Support, and Advocacy in an Online Social Work Community: A Computational Text Analysis of 135,000 Messages from Türkiye**

***
## How the message counts fit together

Four different totals appear in the article, each belonging to a different stage of processing. They are not alternative counts of the same thing.

| Count | Stage | Used for |
|---:|---|---|
| 139,688 | All messages collected | Participation inequality, role typology |
| 135,062 | Messages carrying text | Advocacy repertoire |
| 131,466 | Text set after deduplication | Function classification, time series |
| 102,771 | Messages long enough for embedding | Topic model |

The response analysis uses 131,441 messages, 25 fewer than the deduplicated set, because messages posted in the final seven days of collection had limited opportunity to receive a reply and are excluded.

## Running the scripts

Python 3.10 or later. Install the dependencies with `pip install -r requirements.txt`. The topic model additionally requires `bertopic`, `sentence-transformers`, `umap-learn` and `hdbscan`, which are not in `requirements.txt` because the rest of the pipeline runs without them.

Copy `ayarlar_orn.env` to `ayarlar.env` and fill in the Telegram API credentials before running `01_veri_cek.py`. Every other script works from the files produced by the one before it.

### A note on folder names

The scripts read from and write to a folder named `loglar`, and the figures script writes to `sekiller`. For publication the outputs have been split into `logs` (reports and derived tables) and `tables` (the larger tabular outputs), and the codebook has been placed in `codebook`. **To run the scripts against these files, place the contents of `logs` and `tables` together in a single folder named `loglar` at the repository root.** The scripts are otherwise unchanged from the versions used in the analysis.

### Order

| Script | What it does |
|---|---|
| `01_veri_cek.py` | Collects messages from the group. Downloads no media. Pseudonymises senders at the moment of collection with HMAC-SHA256. |
| `02_temizle.py` | Builds the analysis tables from the raw export. Deletes no rows; flags service messages, bot posts, media-only posts and duplicates. |
| `03_ortak_metin.py` | Finds identical texts shared by different people, and hashtags. Identifies copy-and-paste campaign material. |
| `04_savunuculuk.py` | Measures the advocacy repertoire from three separate signals: hashtags, template texts shared by several people, and petition and campaign vocabulary. |
| `04b_kwic_yenile.py` | Regenerates the keyword-in-context field in the validation file. |
| `05_dogrulama_ornegi.py` | Draws the stratified sample used to validate the advocacy criterion, from flagged and unflagged messages alike. |
| `06_dogrulama_hesapla.py` | Computes precision, the miss rate, the Rogan–Gladen correction, and intercoder agreement for the advocacy coding. |
| `06a_kodlama_excel.py` | Converts a coding file into a spreadsheet with a drop-down code column. |
| `06b_islev_kappa.py` | Computes Cohen's kappa for the function dimension, under both the eight-category and the collapsed four-category scheme, and for the topic dimension. |
| `07_islev_konu_ornegi.py` | Draws the year-stratified sample of 600 messages for function and topic coding, and the subsample of 70 for the second coder. |
| `08_siniflandirici.py` | Trains the four-category function classifier and applies it to the deduplicated text set. |
| `09_talep_yanit.py` | Trains the binary information-request classifier, applies the Rogan–Gladen correction, and measures response behaviour. |
| `10_katilim_zaman.py` | Participation inequality, the Lorenz curve, cohorts and role typology; monthly volume, unusual months by modified Z-score, and disaster vocabulary. |
| `11_konu_modeli.py` | Topic discovery with BERTopic. |
| `12_sekiller.py` | Produces the figures at 300 dpi and as vector PDF. |
| `13_konu_ucgenleme.py` | Thematic group shares by year, and the comparison of the mobilisation series produced by the classifier against the one produced by the topic model. |

## Where each reported result comes from

| Result in the article | File | Produced by |
|---|---|---|
| Intercoder agreement, advocacy coding (κ = 0.71, n = 58) | `logs/dogrulama_sonuc.json` | `06_dogrulama_hesapla.py` |
| Precision of the advocacy criterion, miss rate, corrected prevalence | `logs/dogrulama_sonuc.json` | `06_dogrulama_hesapla.py` |
| Intercoder agreement, function and topic (κ = 0.59, 0.67, 0.23) | `logs/islev_kappa.json` | `06b_islev_kappa.py` |
| Advocacy repertoire, raw prevalence, hashtag persistence | `logs/savunuculuk_ozet.json`, `tables/savunuculuk_aylik.csv`, `tables/kampanya_hashtagleri.csv` | `04_savunuculuk.py` |
| Four-category classifier, cross-validation and confusion matrix | `logs/siniflandirici_rapor.json` | `08_siniflandirici.py` |
| Function distribution by year | `logs/islev_dagilim.csv` | `08_siniflandirici.py` |
| Binary request classifier, sensitivity and specificity, Rogan–Gladen correction | `logs/talep_yanit_rapor.json` | `09_talep_yanit.py` |
| Response rates and response times | `logs/talep_yanit_rapor.json`, `tables/talep_yillik.csv` | `09_talep_yanit.py` |
| Participation inequality, Gini coefficient, role typology | `logs/katilim_rapor.json`, `tables/lorenz.csv`, `tables/roller.csv`, `tables/kohortlar.csv` | `10_katilim_zaman.py` |
| Monthly volume, unusual months, modified Z-scores | `logs/zaman_rapor.json`, `tables/aylik_seri.csv` | `10_katilim_zaman.py` |
| Disaster vocabulary in earthquake months | `logs/zaman_rapor.json`, `tables/afet_terimleri.csv` | `10_katilim_zaman.py` |
| Topic model, 36 topics and their terms | `logs/konu_rapor.json`, `logs/konu_ozet.csv` | `11_konu_modeli.py` |
| Assignment of topics to thematic groups | `logs/konu_etiketleri.csv` | `11_konu_modeli.py` |
| Topic shares by year | `logs/konu_yillik.csv` | `11_konu_modeli.py` |
| Thematic group shares by year, and the correspondence between the two mobilisation series | `logs/ucgenleme.json` | `13_konu_ucgenleme.py` |
| Codebook, including the collapsed four-category scheme | `codebook/` | — |
| Stop-word list | `codebook/durak_kelimeler.txt` | — |
| Marginal topic and function distributions of the two coders | `logs/konu_marjinal.json` | `06c_konu_marjinal.py` |

## What is not here, and why

**The messages.** Neither the raw export nor the cleaned text set is included. The group is a semi-public space whose members did not post with research in mind, and the ethics approval covers analysis rather than redistribution. Message text is therefore not published in any form, and no message is quoted verbatim in the article or in the codebook. The examples in the codebook are constructed for illustration.

**The coded sample.** The files under `veri/kodlama/` hold the text of the 600 sampled messages alongside their codes, and are withheld for the same reason. `06b_islev_kappa.py` and parts of `06_dogrulama_hesapla.py` therefore cannot be re-run from this repository, although their outputs are included in full and the confusion matrices they report can be checked by hand.

**Credentials.** `ayarlar.env` is not in the repository and is excluded by `.gitignore`. `ayarlar_orn.env` is an empty template.

**Senders.** No sender identifier appears anywhere in this repository. Senders were pseudonymised at the moment of collection with a keyed hash, and the key was not retained.

## Ethics

The study was approved by the Scientific Research and Publication Ethics Committee for Social Sciences and Humanities of xxxx University.

## Licence

The code is released under the licence in `LICENSE`. Please cite the article when using any part of this repository.
