## [ChatBattery] Expert-Guided LLM Reasoning for Battery Discovery: From AI-Driven Hypothesis to Synthesis and Characterization

Authors: Shengchao Liu<sup>\*</sup>, Hannan Xu<sup>\*</sup>, Yan Ai<sup>\*</sup>, Huanxin Li<sup>+</sup>, Yoshua Bengio<sup>+</sup>, Harry Guo<sup>+</sup>


### 1 Environment Setup
```
conda create -n ChatBattery python=3.9
conda activate ChatBattery

pip install pandas
pip install openai==0.28
pip install Levenshtein
pip install pymatgen==2024.4.13
pip install ase
pip install -e .

pip install scikit-learn
pip install xgboost
pip install mp-api==0.41.2
pip install Flask
```


### 2 Data Preprocess

Download the datasets from ICSD. In our case, we download all the chemical formula including Lithium.

Then run `python preprocess.py`, and output is a CSV file.


### 3 Run Scripts

First export the open AI, `export OPENAI_API_KEY=xxxxx`.

#### 3.1 Exploration Phase

For stage 1 to 4, run this CMD
```bash
python main.py
```

##### 3.2 Exploitation Phase

- Stage 5, first please get prepared the input file
```bash
cd step_05_deduplication
python step_05_deduplication.py --input_file=xxx
```

- Stage 6, then run the following CMD
```bash
cd step_06_ranking
bash step_06_ranking.sh
```

