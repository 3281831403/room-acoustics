"""室内声学：门口过渡、墙体滤波与多源卷积。

模块集中实现混响探针、遮挡滤波、卷积总线、时钟对齐、异步任务生命周期、
IR 重采样、动态遮挡、动画事件、输出设备配置与重叠能量归一等纯函数。
"""

from __future__ import annotations

# Sabine 公式的经验常数：RT60 = 0.161 * V / (S * alpha)。
_SABINE_CONSTANT = 0.161

# 门口过渡的归一化位置：0.5 表示门口中心，width 为过渡半宽。
_DOOR_CENTER = 0.5


def _clamp01(value):
    """把数值限制到 [0, 1]。"""
    return max(0.0, min(1.0, float(value)))


def _smoothstep(t):
    """经典 smoothstep：一阶导在两端为 0，避免混响参数硬切。"""
    t = _clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def door_crossfade(progress, width):
    """门口区域的平滑混响过渡。

    ``progress`` 是探针沿门口方向的归一化位置，``width`` 是过渡半宽。
    过渡以门口为中心（0.5）对称展开，在 ``[0.5 - width, 0.5 + width]``
    内用 smoothstep 从室外混响平滑混合到室内混响，避免包围盒硬切。
    """
    width = float(width)
    if width <= 0.0:
        # 没有过渡宽度时退化为硬切。
        return 1.0 if float(progress) >= _DOOR_CENTER else 0.0
    start = _DOOR_CENTER - width
    span = 2.0 * width
    return _smoothstep((float(progress) - start) / span)


def wall_filter(distance, walls, absorption):
    """按墙体数量与吸声计算遮挡滤波。

    每堵墙按 ``(1 - absorption)`` 的透过率衰减，再叠加直线距离衰减
    ``1 / (1 + distance)``。墙越多、吸声越强，透过的能量越少，因此隔着
    墙的声音不会比直线距离更近的声音更响。
    """
    distance = max(0.0, float(distance))
    walls = max(0, int(walls))
    absorption = _clamp01(absorption)

    transmission = (1.0 - absorption) ** walls
    distance_gain = 1.0 / (1.0 + distance)
    return distance_gain * transmission


def source_buses(count):
    """为每个声源分配独立卷积总线。

    返回 ``0 .. count-1`` 的总线编号；每个声源使用自己的卷积核，保留
    方向感，避免多声源共用一个卷积核。
    """
    return tuple(range(max(0, int(count))))


def align_clock(audio_time, main_time, latency):
    """对齐音频线程与主线程时钟。

    返回主线程时间与音频线程时间（含输出延迟）之差，用于补偿时钟漂移，
    防止混响尾音被提前截断。结果为正表示主线程领先。
    """
    return float(main_time) - float(audio_time) - float(latency)


def cancel_job(job_room, current_room):
    """旧房间任务是否应取消。

    当异步卷积任务所属房间与当前房间不一致时，必须取消，避免旧房间的
    混响尾音漏到新房间。
    """
    return job_room != current_room


def resample_ir(ir_length, src_rate, dst_rate):
    """IR 重采样后的长度（采样点数）。

    采样率变化时保持 IR 的物理时长不变，因此长度按 ``dst_rate / src_rate``
    等比缩放并四舍五入，避免混响时间随采样率切换而变短。
    """
    src_rate = float(src_rate)
    if src_rate <= 0.0:
        raise ValueError("src_rate must be positive")
    return int(round(float(ir_length) * float(dst_rate) / src_rate))


def update_occlusion(last_update, now, interval):
    """动态遮挡是否到更新时间。

    动态物体穿过房间时，遮挡关系需要按固定间隔重新计算；距上次更新
    达到 ``interval`` 时返回 ``True``。
    """
    return (float(now) - float(last_update)) >= float(interval)


def switch_room(door_progress):
    """开门动画是否完成并允许切房间。

    只有开门动画进度到达 1.0 后才切换混响参数，避免动画未结束就硬切。
    """
    return float(door_progress) >= 1.0


def hrtf_profile(device):
    """按输出设备选择空间音频配置。

    耳机使用双耳 HRTF；扬声器使用立体声下混配置，两者不共用参数。
    """
    name = str(device).strip().lower()
    if name in {"headphones", "headphone", "headset", "earphones", "earphone"}:
        return "hrtf-headphones"
    if name in {"speakers", "speaker", "stereo", "monitor"}:
        return "stereo-speakers"
    # 未知设备按扬声器处理，避免误用双耳 HRTF。
    return "stereo-speakers"


def normalize_overlap(energies):
    """重叠混响区域能量归一。

    多个混响区域重叠时按总能量归一化，使总响度保持为 1，避免简单相加
    导致响度爆掉。全零输入按均分处理。
    """
    values = [max(0.0, float(e)) for e in energies]
    total = sum(values)
    if total <= 0.0:
        if not values:
            return tuple()
        share = 1.0 / len(values)
        return tuple(share for _ in values)
    return tuple(value / total for value in values)


def rt60(volume, surface, absorption):
    """Sabine 混响时间。

    ``RT60 = 0.161 * V / (S * alpha)``，其中 V 为房间体积、S 为总表面积、
    alpha 为平均吸声系数。
    """
    volume = float(volume)
    surface = float(surface)
    absorption = float(absorption)
    if surface <= 0.0 or absorption <= 0.0:
        return 0.0
    return _SABINE_CONSTANT * volume / (surface * absorption)


def attenuation(distance, rolloff):
    """距离衰减。

    使用反距离模型 ``1 / (1 + distance * rolloff)``，距离为 0 时增益为 1。
    """
    distance = max(0.0, float(distance))
    rolloff = max(0.0, float(rolloff))
    return 1.0 / (1.0 + distance * rolloff)


def door_amount(progress):
    """门开度到混响混合量。

    门完全关闭（0.0）时室外混响为主，完全打开（1.0）时室内混响为主；
    线性映射并限制在 [0, 1]。
    """
    return _clamp01(progress)


def resample_length(length, src_rate, dst_rate):
    """按采样率比例计算重采样长度。"""
    return resample_ir(length, src_rate, dst_rate)


def tail_length(rt60, threshold_db):
    """达到阈值所需的混响尾音长度。

    ``RT60`` 是衰减 60 dB 所需时间，因此衰减到 ``threshold_db`` 的时间为
    ``rt60 * |threshold_db| / 60``。例如 -30 dB 对应 RT60 的一半。
    """
    rt60 = max(0.0, float(rt60))
    return rt60 * abs(float(threshold_db)) / 60.0
