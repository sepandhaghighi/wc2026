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
| aisingapore/gemma-sea-lion-v4-27b-it | 0.900 | 0.233 | 0.617 | 0.700 | 0.3037 | 0.4857 |
| qwen/qwen3-30b-a3b-fp8 | 0.900 | 0.200 | 0.700 | 0.733 | 0.3233 | 0.5055 |
| openai/gpt-oss-120b | 0.867 | 0.200 | 0.667 | 0.867 | 0.2951 | 0.4658 |
| meta/llama-4-scout-17b-16e-instruct | 0.867 | 0.200 | 0.683 | 0.767 | 0.3439 | 0.5311 |
| openai/gpt-oss-20b | 0.867 | 0.133 | 0.650 | 0.967 | 0.2964 | 0.4652 |
| mistralai/mistral-small-3.1-24b-instruct | 0.833 | 0.300 | 0.583 | 0.700 | 0.3327 | 0.5164 |
| meta/llama-3.1-8b-instruct-fast | 0.700 | 0.100 | 0.850 | 1.300 | 0.4282 | 1.6708 |
| meta/llama-3.2-3b-instruct | 0.700 | 0.033 | 1.017 | 1.100 | 0.7150 | 2.0429 |

## 3. Overall

| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |
|-------|----------:|--------:|-----------:|----------:|---------:|----------:|
| meta/llama-4-scout-17b-16e-instruct | 0.745 | 0.147 | 0.833 | 1.059 | 0.4782 | 0.7931 |
| qwen/qwen3-30b-a3b-fp8 | 0.735 | 0.147 | 0.892 | 1.118 | 0.4618 | 0.7715 |
| openai/gpt-oss-20b | 0.716 | 0.118 | 0.853 | 1.176 | 0.4440 | 0.7362 |
| aisingapore/gemma-sea-lion-v4-27b-it | 0.706 | 0.157 | 0.819 | 1.069 | 0.4425 | 0.7415 |
| openai/gpt-oss-120b | 0.686 | 0.118 | 0.873 | 1.176 | 0.4557 | 0.7609 |
| mistralai/mistral-small-3.1-24b-instruct | 0.657 | 0.157 | 0.824 | 1.176 | 0.4780 | 0.7969 |
| meta/llama-3.1-8b-instruct-fast | 0.559 | 0.098 | 0.936 | 1.363 | 0.5069 | 1.1289 |
| meta/llama-3.2-3b-instruct | 0.412 | 0.098 | 1.039 | 1.471 | 0.6201 | 1.2793 |
