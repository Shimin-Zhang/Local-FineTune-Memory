#!/bin/bash
# Run 3 test, to start after training has ended. Converts the two adapters for llama.cpp; writes scripts for the 100
# held-out scene requests with the untuned model and with each epoch's adapter, and for the earlier 50 requests (three
# seeds) with the 2-epoch adapter; runs everything in the sandbox; builds the sheets and numbers. One GPU job at a time.
cd /home/shimin/agents/scrap/local-finetune-memory
V=results/finetune_v3
P=blender_task/prompts_scenes100.json
L=results/logs
pgrep -f "train_qlora.py" >/dev/null && { echo "the trainer is still running; stopping"; exit 1; }
for e in 1 2; do
  [ -d $V/run3/epoch$e ] || { echo "no adapter for epoch $e; stopping"; exit 1; }
  [ -f $V/run3/adapter-epoch$e-f16.gguf ] || uv run python /home/shimin/ai/llama.cpp/convert_lora_to_gguf.py $V/run3/epoch$e \
      --base .models/Qwen3.8-27B --outfile $V/run3/adapter-epoch$e-f16.gguf --outtype f16 > $L/convert_run3_e$e.log 2>&1
  ls -la $V/run3/adapter-epoch$e-f16.gguf || { echo "no converted adapter for epoch $e; stopping"; exit 1; }
done

gen() {  # gen <prompts> <out dir> <seeds> [adapter]: write the scripts on the GPU, then run them on the CPU in the background
  local tag=$(echo ${2#$V/} | tr / _)
  echo "$tag: generating $(date +%H:%M)"
  uv run python blender_task/generate.py $1 $2 --conditions bare --seeds $3 --name-seeds --parallel 6 --max-tokens 4096 \
      ${4:+--lora $4} > $L/run3_${tag}_generate.log 2>&1
  until ! pgrep -f "llama-server.*--port 8099" >/dev/null; do sleep 5; done
  echo "$tag: $(ls $2/bare/*.py 2>/dev/null | wc -l) scripts written $(date +%H:%M)"
  (nice -n 5 uv run python blender_task/run_sandboxed.py $2/bare --own-view --workers 8 > $L/run3_${tag}_run.log 2>&1) &
}
gen $P $V/scenes/before 0
gen $P $V/scenes/epoch2 0 $V/run3/adapter-epoch2-f16.gguf
gen $P $V/scenes/epoch1 0 $V/run3/adapter-epoch1-f16.gguf
gen blender_task/prompts_eval50.json $V/eval50/epoch2 0,1,2 $V/run3/adapter-epoch2-f16.gguf
echo "GPU work done $(date +%H:%M); waiting for the sandbox runs"
wait

REF=$(python3 -c "print(','.join(f'results/synth_v1/test_b0{i}' for i in range(1, 6)))")
uv run python finetune/scene_sheet.py $P $V/scenes/report --title "Run 3, held-out scenes" \
    --side "Sonnet (the reference)=$REF" --side "27B untuned=$V/scenes/before/bare" \
    --side "27B tuned, 1 epoch=$V/scenes/epoch1/bare" --side "27B tuned, 2 epochs=$V/scenes/epoch2/bare" > $L/run3_scene_sheet.log 2>&1
uv run python finetune/eval_report.py $P $V/scenes/report_numbers --seeds 0 --title "Run 3, held-out scenes" \
    --a "Before (untuned 27B)=$V/scenes/before/bare" --b "Run 3, 2 epochs=$V/scenes/epoch2/bare" \
    --extra "Run 3, 1 epoch=$V/scenes/epoch1/bare" > $L/run3_scenes_report.log 2>&1
for s in before epoch1 epoch2; do                      # the dataset's own rules, applied to what each model wrote
  uv run python synth/check.py $V/scenes/$s/bare > $L/run3_check_$s.txt 2>/dev/null
  echo "dataset checker, $s: $(tail -1 $L/run3_check_$s.txt)"
done
# the untuned model's scripts for these 50 (seeds 0,1,2) were written before run 3 by the same generate.py settings
uv run python finetune/eval_report.py blender_task/prompts_eval50.json $V/eval50/report --title "Run 3 on 50 everyday requests" \
    --a "Before (untuned 27B)=$V/eval50/before/bare" --b "Run 3, 2 epochs=$V/eval50/epoch2/bare" > $L/run3_eval50_report.log 2>&1
echo "ALL DONE $(date +%H:%M)"
