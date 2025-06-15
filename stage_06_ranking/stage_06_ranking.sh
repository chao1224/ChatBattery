

python stage_06_ranking.py \
--metric=total_charge --top_k=29 \
--input_file=../stage_05_deduplication/output_materials.csv --output_file=output_01.txt \
--log_file=log_01.txt


python stage_06_ranking.py \
--metric=preparation_complexity --top_k=20 \
--input_file=output_01.txt --output_file=output_02.txt \
--log_file=log_02.txt



python stage_06_ranking.py \
--metric=voltage --top_k=3 \
--input_file=output_02.txt --output_file=output_03.txt \
--log_folder=log_03 \
--log_file=log_03.txt
