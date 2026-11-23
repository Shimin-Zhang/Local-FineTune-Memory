#!/bin/bash
# 20 famous film scenes, each built in a session: the model writes code, sees the result and a picture, and carries on
# until its context (32,768 tokens) is full. The untuned 27B first, then with run 3's two-pass adapter. Two sessions at
# a time on the GPU. A side whose server died is started again (finished sessions are kept) up to three times.
cd /home/shimin/agents/scrap/local-finetune-memory
V=results/finetune_v3/movies
P=blender_task/prompts_movies20.json
L=results/logs
side() {  # side <name> [adapter]
  for try in 1 2 3; do
    n=$(ls $V/$1/*/session.json 2>/dev/null | wc -l)
    [ "$n" -ge 20 ] && break
    echo "$1: start $try, $n of 20 sessions done $(date +%H:%M)"
    uv run python blender_task/agent_loop.py $P $V/$1 --ctx 32768 --parallel 2 ${2:+--lora $2} >> $L/movies_$1.log 2>&1
    sleep 10
  done
  echo "$1: $(ls $V/$1/*/session.json 2>/dev/null | wc -l) of 20 sessions $(date +%H:%M)"
}
side untuned
side tuned results/finetune_v3/run3/adapter-epoch2-f16.gguf
uv run python finetune/session_sheet.py $P $V/report --title "Famous film scenes, built over many runs until the context is full" \
    --side "Qwen3.8-27B, untuned=$V/untuned" --side "Qwen3.8-27B, fine-tuned (2 epochs)=$V/tuned" > $L/movies_sheet.log 2>&1
echo "ALL DONE $(date +%H:%M)"
