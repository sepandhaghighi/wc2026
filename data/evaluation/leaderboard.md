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
| aisingapore/gemma-sea-lion-v4-27b-it | 0.844 | 0.219 | 0.719 | 0.812 | 0.3246 | 0.5074 |
| qwen/qwen3-30b-a3b-fp8 | 0.844 | 0.188 | 0.812 | 0.812 | 0.3389 | 0.5218 |
| openai/gpt-oss-120b | 0.812 | 0.188 | 0.766 | 0.969 | 0.3131 | 0.4852 |
| meta/llama-4-scout-17b-16e-instruct | 0.812 | 0.188 | 0.781 | 0.875 | 0.3644 | 0.5521 |
| openai/gpt-oss-20b | 0.812 | 0.125 | 0.750 | 1.062 | 0.3178 | 0.4881 |
| mistralai/mistral-small-3.1-24b-instruct | 0.781 | 0.281 | 0.703 | 0.781 | 0.3572 | 0.5418 |
| meta/llama-3.2-3b-instruct | 0.688 | 0.031 | 1.125 | 1.125 | 0.7155 | 1.9745 |
| meta/llama-3.1-8b-instruct-fast | 0.656 | 0.094 | 0.938 | 1.375 | 0.4880 | 2.6759 |

## 3. Overall

| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |
|-------|----------:|--------:|-----------:|----------:|---------:|----------:|
| meta/llama-4-scout-17b-16e-instruct | 0.731 | 0.144 | 0.861 | 1.087 | 0.4819 | 0.7945 |
| qwen/qwen3-30b-a3b-fp8 | 0.721 | 0.144 | 0.923 | 1.135 | 0.4639 | 0.7714 |
| openai/gpt-oss-20b | 0.702 | 0.115 | 0.880 | 1.202 | 0.4477 | 0.7381 |
| aisingapore/gemma-sea-lion-v4-27b-it | 0.692 | 0.154 | 0.846 | 1.096 | 0.4462 | 0.7432 |
| openai/gpt-oss-120b | 0.673 | 0.115 | 0.899 | 1.202 | 0.4582 | 0.7612 |
| mistralai/mistral-small-3.1-24b-instruct | 0.644 | 0.154 | 0.856 | 1.192 | 0.4828 | 0.7993 |
| meta/llama-3.1-8b-instruct-fast | 0.548 | 0.096 | 0.962 | 1.385 | 0.5238 | 1.4486 |
| meta/llama-3.2-3b-instruct | 0.413 | 0.096 | 1.072 | 1.471 | 0.6220 | 1.2729 |
