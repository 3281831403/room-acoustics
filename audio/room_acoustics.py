"""室内声学：门口过渡、墙体滤波与多源卷积：待实现的核心模块。"""

from __future__ import annotations


def door_crossfade(progress, width):
    """门口区域的平滑混响过渡。"""
    raise NotImplementedError

def wall_filter(distance, walls, absorption):
    """按墙体数量与吸声计算遮挡滤波。"""
    raise NotImplementedError

def source_buses(count):
    """为每个声源分配独立卷积总线。"""
    raise NotImplementedError

def align_clock(audio_time, main_time, latency):
    """对齐音频线程与主线程时钟。"""
    raise NotImplementedError

def cancel_job(job_room, current_room):
    """旧房间任务是否应取消。"""
    raise NotImplementedError

def resample_ir(ir_length, src_rate, dst_rate):
    """IR 重采样后的长度。"""
    raise NotImplementedError

def update_occlusion(last_update, now, interval):
    """动态遮挡是否到更新时间。"""
    raise NotImplementedError

def switch_room(door_progress):
    """开门动画是否完成并允许切房间。"""
    raise NotImplementedError

def hrtf_profile(device):
    """按输出设备选择空间音频配置。"""
    raise NotImplementedError

def normalize_overlap(energies):
    """重叠混响区域能量归一。"""
    raise NotImplementedError

def rt60(volume, surface, absorption):
    """Sabine 混响时间。"""
    raise NotImplementedError

def attenuation(distance, rolloff):
    """距离衰减。"""
    raise NotImplementedError

def door_amount(progress):
    """门开度到混响混合量。"""
    raise NotImplementedError

def resample_length(length, src_rate, dst_rate):
    """按采样率比例计算重采样长度。"""
    raise NotImplementedError

def tail_length(rt60, threshold_db):
    """达到阈值所需的混响尾音长度。"""
    raise NotImplementedError
