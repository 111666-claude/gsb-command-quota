# command-quota

指挥配额：从标准输入读 JSONL 指令，逐条给保留或丢弃的判定。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m quota < events.jsonl
python3 -m quota --sample=window|overlay|dup|work
```

事件字段：`ts`（毫秒）、`commander`、`unit`、`event_id`。

## 口径

- **窗口**：只看最近 1000 毫秒内的指令，更早的不再占用配额。
- **总配额**：同一指挥官在窗口内最多保留 10 条。
- **单位配额**：同一指挥官同一兵种在窗口内最多保留 3 条。
- **覆盖层**：兵种为 `scout` 的关键单位不受单位配额限制，但仍受总配额限制。
- **幂等**：同一个 `event_id` 只处理一次，重复出现判为 `duplicate`。

## 不变量

- 每条事件给出一条判定，`keep` 加 `drop` 等于输入条数。
- 窗口内保留数不超过总配额；除关键兵种外不超过单位配额。
- `scanned` 不随事件数平方级放大：两千条事件的 `scanned` 不超过 9000。

## 输出契约

每条事件打印一行 JSON：`event_id`、`decision`（`keep` / `drop`）、`reason`（`quota` / `duplicate`，保留时为 null）、`scanned`。
`--sample=work` 只打印 `{"events": N, "scanned": N}`。
