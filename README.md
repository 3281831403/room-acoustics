# 室内声学：门口过渡、墙体滤波与多源卷积

开关门和切房间时混响突变：探针硬切、遮挡只看距离、多声源共卷积核、音频线程时钟漂移、异步尾音漏到新房间。本仓库固定声学状态与资源生命周期。

- 领域：游戏、图形与多媒体
- 子方向：音视频处理
- 语言/框架：Python 3, pytest
- 初始状态：15 个参数化用例全部失败

## 目录结构

```
README.md
conftest.py
.gitignore
audio/__init__.py
audio/room_acoustics.py
tests/test_room_acoustics.py
```

## 需要修复的 10 个问题

1. 门口位置用平滑过渡混合室内外混响，不按包围盒硬切
2. 遮挡滤波计入墙体数量与吸声，不再只按直线距离
3. 每个声源使用独立卷积核，保留方向感
4. 音频线程与主线程时钟对齐，尾音不被截断
5. 切场景时取消旧房间异步卷积任务
6. 采样率变化时重采样 IR，混响时间不缩短
7. 动态物体穿过房间时更新遮挡关系
8. 开门动画结束才切换混响参数
9. 耳机与扬声器使用不同 HRTF/立体声配置
10. 多个混响区域重叠时能量归一，响度不爆

## 15 条验收契约

    01. door crossfade — `door_crossfade`
    02. wall occlusion filter — `wall_filter`
    03. per source buses — `source_buses`
    04. audio clock alignment — `align_clock`
    05. cancel old room job — `cancel_job`
    06. ir resample — `resample_ir`
    07. dynamic occlusion update — `update_occlusion`
    08. switch after door animation — `switch_room`
    09. headphone hrtf — `hrtf_profile`
    10. overlap energy normalized — `normalize_overlap`
    11. sabine rt60 — `rt60`
    12. distance attenuation — `attenuation`
    13. door mix amount — `door_amount`
    14. resample length ratio — `resample_length`
    15. reverb tail length — `tail_length`

## 当前状态

`audio/room_acoustics.py` 只保留函数签名与文档字符串，所有函数体统一
`raise NotImplementedError`。`tests/test_room_acoustics.py` 使用一个
`@pytest.mark.parametrize` 装载 15 条契约，初始全部失败且没有 collection error。

```bash
python -m pytest -q
```

预期输出包含 `15 failed`。实现 `audio/room_acoustics.py` 后，15 条契约应全部通过。
