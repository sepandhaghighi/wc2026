# World Cup 2026 Benchmark Results

## 1. Group Stage

| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |
|-------|----------:|--------:|-----------:|----------:|---------:|----------:|
| meta/llama-4-scout-17b-16e-instruct | 0.694 | 0.125 | 0.896 | 1.181 | 0.5342 | 0.9023 |
| qwen/qwen3-30b-a3b-fp8 | 0.667 | 0.125 | 0.972 | 1.278 | 0.5195 | 0.8824 |
| openai/gpt-oss-20b | 0.653 | 0.111 | 0.938 | 1.264 | 0.5055 | 0.8491 |
| aisingapore/gemma-sea-lion-v4-27b-it | 0.625 | 0.125 | 0.903 | 1.222 | 0.5003 | 0.8480 |
| openai/gpt-oss-120b | 0.611 | 0.083 | 0.958 | 1.306 | 0.5227 | 0.8839 |
| mistralai/mistral-small-3.1-24b-instruct | 0.583 | 0.097 | 0.924 | 1.375 | 0.5385 | 0.9138 |
| meta/llama-3.1-8b-instruct-fast | 0.500 | 0.097 | 0.972 | 1.389 | 0.5397 | 0.9031 |
| meta/llama-3.2-3b-instruct | 0.292 | 0.125 | 1.049 | 1.625 | 0.5805 | 0.9611 |

## 2. Knockout Stage

| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |
|-------|----------:|--------:|-----------:|----------:|---------:|----------:|
| aisingapore/gemma-sea-lion-v4-27b-it | 0.871 | 0.226 | 0.710 | 0.774 | 0.3134 | 0.4958 |
| qwen/qwen3-30b-a3b-fp8 | 0.871 | 0.194 | 0.823 | 0.806 | 0.3303 | 0.5129 |
| openai/gpt-oss-120b | 0.839 | 0.194 | 0.758 | 0.935 | 0.3037 | 0.4751 |
| meta/llama-4-scout-17b-16e-instruct | 0.839 | 0.194 | 0.774 | 0.839 | 0.3545 | 0.5420 |
| openai/gpt-oss-20b | 0.839 | 0.129 | 0.742 | 1.032 | 0.3086 | 0.4781 |
| mistralai/mistral-small-3.1-24b-instruct | 0.806 | 0.290 | 0.694 | 0.742 | 0.3415 | 0.5255 |
| meta/llama-3.2-3b-instruct | 0.710 | 0.032 | 1.129 | 1.097 | 0.7385 | 2.0382 |
| meta/llama-3.1-8b-instruct-fast | 0.677 | 0.097 | 0.935 | 1.355 | 0.4392 | 1.6481 |

## 3. Overall

| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |
|-------|----------:|--------:|-----------:|----------:|---------:|----------:|
| meta/llama-4-scout-17b-16e-instruct | 0.738 | 0.146 | 0.859 | 1.078 | 0.4801 | 0.7938 |
| qwen/qwen3-30b-a3b-fp8 | 0.728 | 0.146 | 0.927 | 1.136 | 0.4626 | 0.7712 |
| openai/gpt-oss-20b | 0.709 | 0.117 | 0.879 | 1.194 | 0.4462 | 0.7375 |
| aisingapore/gemma-sea-lion-v4-27b-it | 0.699 | 0.155 | 0.845 | 1.087 | 0.4440 | 0.7420 |
| openai/gpt-oss-120b | 0.680 | 0.117 | 0.898 | 1.194 | 0.4568 | 0.7608 |
| mistralai/mistral-small-3.1-24b-instruct | 0.650 | 0.155 | 0.854 | 1.184 | 0.4792 | 0.7969 |
| meta/llama-3.1-8b-instruct-fast | 0.553 | 0.097 | 0.961 | 1.379 | 0.5095 | 1.1273 |
| meta/llama-3.2-3b-instruct | 0.417 | 0.097 | 1.073 | 1.466 | 0.6281 | 1.2853 |
