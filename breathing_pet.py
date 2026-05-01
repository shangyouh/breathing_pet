#!/usr/bin/env python3
"""
Breathing Pet — 桌面呼吸伴侣

一个安静的桌面呼吸动画宠物。放在屏幕角落，默默呼吸陪伴你工作。
- 吸气 2 秒 (ease-in) + 呼气 3 秒 (ease-out)，不对称自然呼吸节奏
- 三击进入呼吸训练模式：4-4-6-2 循环 × 6 轮
- 双击或右键菜单切换宠物
- 拖拽移动位置

用法：
    python breathing_pet.py

首次运行自动生成 config.json，编辑可自定义宠物列表、呼吸节奏、字体大小等。
"""

import tkinter as tk
from tkinter import Menu
import json
import os
import math
import random

# ================================================================
#  配置默认值
# ================================================================
DEFAULT_CONFIG = {
    "pet": {
        "skin_type": "emoji",
        "emoji_list": [
            "🐱", "🐶", "🐼", "🐨", "🦊", "🐰", "🐸",
            "🐙", "🐳", "🦄", "🐥", "🐷", "🐮", "🦉", "🐧"
        ],
        "skin_rotate_minutes": 30,
        "window_size": [120, 120],
        "emoji_font_size": 64,
        "breath_inhale_ms": 2000,
        "breath_exhale_ms": 3000,
        "pet_color": "纯白",
        "position": [100, 100]
    },
    "bubble": {
        "duration_seconds": 8,
        "font_size": 11,
        "max_width": 200
    }
}

# ================================================================
#  缓动函数
# ================================================================
def ease_in_out_quad(t):
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t

def ease_in_quad(t):
    return t * t

def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)

# ================================================================
#  呼吸训练阶段
# ================================================================
TRAINING_PHASES = [
    ('inhale', 4000, '吸 气', 1.0, 1.4, '#b3d9ff'),
    ('hold',   4000, '屏 息', 1.4, 1.4, '#b3d9ff'),
    ('exhale', 6000, '呼 气', 1.4, 1.0, None),
    ('pause',  2000, '暂 停', 1.0, 1.0, None),
]
TRAINING_CYCLES = 6
ANIM_FRAME_MS = 50
TRANSPARENT_COLOR = '#010101'

# 减压调色板
COLOR_PALETTE = {
    '纯白':      '#f5f5f5',
    '莫兰迪灰':  '#c2b9b0',
    '莫兰迪粉':  '#d4c4c0',
    '鼠尾草绿':  '#b5c4b1',
    '薰衣草紫':  '#c4c1d4',
    '雾蓝':      '#b8c5d6',
    '奶油黄':    '#e8dcc8',
    '淡灰绿':    '#c8d6c4',
}

# ================================================================
#  皮肤管理器
# ================================================================
class SkinManager:
    def __init__(self, config):
        self.config = config
        self.pet_cfg = config['pet']
        self.skin_type = self.pet_cfg.get('skin_type', 'emoji')
        self.emoji_list = self.pet_cfg.get('emoji_list', ['🐱'])
        self.rotate_minutes = self.pet_cfg.get('skin_rotate_minutes', 30)
        self._current_index = 0

    def skin_count(self):
        return len(self.emoji_list)

    def current_skin(self):
        return self.emoji_list[self._current_index % len(self.emoji_list)]

    def next_skin(self):
        self._current_index = (self._current_index + 1) % self.skin_count()
        return self.current_skin()

    def prev_skin(self):
        self._current_index = (self._current_index - 1) % self.skin_count()
        return self.current_skin()

    def random_skin(self):
        self._current_index = random.randint(0, self.skin_count() - 1)
        return self.current_skin()

    def get_rotate_interval_ms(self):
        return self.rotate_minutes * 60 * 1000


# ================================================================
#  宠物窗口
# ================================================================
class BreathingPet:
    def __init__(self, config):
        self.config = config
        self.skin_manager = SkinManager(config)
        self.config_path = None  # set by main()

        self.root = tk.Tk()
        self.root.title('Breathing Pet')

        w, h = config['pet']['window_size']
        x, y = config['pet'].get('position', [100, 100])
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=TRANSPARENT_COLOR)
        self.root.wm_attributes('-transparentcolor', TRANSPARENT_COLOR)

        self.pet_label = tk.Label(
            self.root, bg=TRANSPARENT_COLOR,
            fg=self._get_color_hex(),
            font=('Segoe UI Emoji', config['pet']['emoji_font_size']),
            cursor='fleur'
        )
        self.pet_label.pack(expand=True, fill='both')

        self._drag_x = 0
        self._drag_y = 0
        self.pet_label.bind('<Button-1>', self._on_click)
        self.pet_label.bind('<B1-Motion>', self._on_drag_move)
        self.pet_label.bind('<Button-3>', self._show_menu)

        self.bubble = None
        self.bubble_timer = None

        # 呼吸动画状态
        self._breath_base_size = config['pet']['emoji_font_size']
        self._breath_phase = 'inhale'
        self._breath_elapsed = 0
        self._breath_timer = None
        self._normal_color = self._get_color_hex()

        # 多击
        self._click_count = 0
        self._click_timer = None

        # 呼吸训练
        self._training = False
        self._training_cycle = 0
        self._training_phase_idx = 0
        self._training_elapsed = 0
        self._training_guide = None

        self._build_menu()

    # ---- 配置持久化 ----
    def save_position(self):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.config['pet']['position'] = [x, y]
        if self.config_path:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

    def update_display(self, emoji_char=None):
        if emoji_char is None:
            emoji_char = self.skin_manager.current_skin()
        self.pet_label.configure(text=emoji_char)

    def _get_color_hex(self):
        """从配置读取颜色名，返回 hex 值"""
        name = self.config['pet'].get('pet_color', '纯白')
        return COLOR_PALETTE.get(name, '#f5f5f5')

    def _set_color(self, name):
        """切换宠物颜色"""
        hex_color = COLOR_PALETTE.get(name, '#f5f5f5')
        self.config['pet']['pet_color'] = name
        self._normal_color = hex_color
        if not self._training:
            self.pet_label.configure(fg=hex_color)
        self.save_position()  # 顺便保存配置

    # ---- 拖拽 & 多击 ----
    def _on_click(self, event):
        self._drag_x, self._drag_y = event.x, event.y
        self._click_count += 1
        if self._click_timer:
            self.root.after_cancel(self._click_timer)
        self._click_timer = self.root.after(500, self._process_multi_click)

    def _on_drag_move(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f'+{x}+{y}')

    def _process_multi_click(self):
        if self._click_count >= 3:
            self._stop_training() if self._training else self._start_training()
        elif self._click_count == 2:
            self.skin_manager.next_skin()
            self.update_display()
        self._click_count = 0

    # ---- 气泡 ----
    def _show_bubble(self, message):
        self._hide_bubble()
        bc = self.config['bubble']
        self.bubble = tk.Toplevel(self.root)
        self.bubble.overrideredirect(True)
        self.bubble.attributes('-topmost', True)
        self.bubble.configure(bg='white')
        bx = self.root.winfo_x() + self.root.winfo_width() + 5
        by = self.root.winfo_y() - 10
        self.bubble.geometry(f'+{bx}+{by}')
        frame = tk.Frame(self.bubble, bg='#fff9c4',
                         highlightbackground='#f9a825', highlightthickness=2, bd=0)
        frame.pack()
        lbl = tk.Label(frame, text=message, bg='#fff9c4', fg='#333333',
                       font=('Microsoft YaHei', bc['font_size']),
                       wraplength=bc.get('max_width', 200),
                       justify='left', padx=10, pady=8)
        lbl.pack()
        lbl.bind('<Button-1>', lambda e: self._hide_bubble())
        frame.bind('<Button-1>', lambda e: self._hide_bubble())
        self.bubble_timer = self.root.after(bc['duration_seconds'] * 1000, self._hide_bubble)

    def _hide_bubble(self):
        if self.bubble:
            self.bubble.destroy()
            self.bubble = None
        if self.bubble_timer:
            self.root.after_cancel(self.bubble_timer)
            self.bubble_timer = None

    # ---- 右键菜单 ----
    def _build_menu(self):
        self.menu = Menu(self.root, tearoff=0)
        sm = Menu(self.menu, tearoff=0)
        sm.add_command(label='下一个宠物', command=lambda: (self.skin_manager.next_skin(), self.update_display()))
        sm.add_command(label='随机宠物', command=lambda: (self.skin_manager.random_skin(), self.update_display()))
        self.menu.add_cascade(label='🐾 换宠物', menu=sm)

        # 颜色子菜单
        cm = Menu(self.menu, tearoff=0)
        current_color = self.config['pet'].get('pet_color', '纯白')
        for cname in COLOR_PALETTE:
            label = f'● {cname}' if cname == current_color else f'  {cname}'
            cm.add_command(label=label, command=lambda n=cname: self._set_color(n))
        self.menu.add_cascade(label='🎨 换颜色', menu=cm)

        self.menu.add_separator()
        self.menu.add_command(label='❌ 退出', command=self._quit)

    def _show_menu(self, event):
        self._build_menu()
        self.menu.tk_popup(event.x_root, event.y_root)

    def _quit(self):
        self.save_position()
        self.root.destroy()

    # ---- 呼吸训练 ----
    def _start_training(self):
        self._training = True
        self._training_cycle = 0
        self._training_phase_idx = 0
        self._training_elapsed = 0
        self._show_training_guide()
        self._update_training_guide()
        self._show_bubble('开始呼吸训练，跟我一起呼吸')

    def _stop_training(self):
        self._training = False
        self._hide_training_guide()
        self.pet_label.configure(fg=self._normal_color,
                                 font=('Segoe UI Emoji', self._breath_base_size))
        self._show_bubble('训练已结束')

    def _finish_training(self):
        self._training = False
        self._hide_training_guide()
        self.pet_label.configure(fg=self._normal_color,
                                 font=('Segoe UI Emoji', self._breath_base_size))
        self._show_bubble('完成 ✨')

    def _show_training_guide(self):
        if self._training_guide:
            return
        self._training_guide = tk.Toplevel(self.root)
        self._training_guide.overrideredirect(True)
        self._training_guide.attributes('-topmost', True)
        self._training_guide.configure(bg='#2d2d2d')
        gx = self.root.winfo_x() + 10
        gy = self.root.winfo_y() + self.root.winfo_height() // 2 - 30
        self._training_guide.geometry(f'+{gx}+{gy}')
        self._training_guide_label = tk.Label(
            self._training_guide, text='', bg='#2d2d2d', fg='#b3d9ff',
            font=('Microsoft YaHei', 10, 'bold'),
            justify='left', padx=8, pady=4
        )
        self._training_guide_label.pack()

    def _hide_training_guide(self):
        if self._training_guide:
            self._training_guide.destroy()
            self._training_guide = None

    def _update_training_guide(self):
        if not self._training_guide:
            return
        label = TRAINING_PHASES[self._training_phase_idx][2]
        remaining = TRAINING_CYCLES - self._training_cycle
        self._training_guide_label.configure(text=f'{label}\n剩余 {remaining} 轮')

    # ---- 动画循环 ----
    def _animation_tick(self):
        if self._training:
            self._training_tick()
        else:
            self._normal_breathe_tick()
        self._breath_timer = self.root.after(ANIM_FRAME_MS, self._animation_tick)

    def _normal_breathe_tick(self):
        """吸气 2s (ease-in 100%→120%) + 呼气 3s (ease-out 120%→100%)"""
        inhale_ms = self.config['pet'].get('breath_inhale_ms', 2000)
        exhale_ms = self.config['pet'].get('breath_exhale_ms', 3000)
        duration = inhale_ms if self._breath_phase == 'inhale' else exhale_ms
        self._breath_elapsed += ANIM_FRAME_MS
        if self._breath_elapsed >= duration:
            self._breath_elapsed -= duration
            self._breath_phase = 'exhale' if self._breath_phase == 'inhale' else 'inhale'
            duration = inhale_ms if self._breath_phase == 'inhale' else exhale_ms
        t = self._breath_elapsed / duration
        if self._breath_phase == 'inhale':
            scale = 1.0 + 0.2 * ease_in_quad(t)
        else:
            scale = 1.2 - 0.2 * ease_out_quad(t)
        new_size = max(1, int(self._breath_base_size * scale))
        self.pet_label.configure(font=('Segoe UI Emoji', new_size))

    def _training_tick(self):
        """4-4-6-2 呼吸训练"""
        phase = TRAINING_PHASES[self._training_phase_idx]
        _, duration, _, start_scale, end_scale, fg_color = phase
        self._training_elapsed += ANIM_FRAME_MS
        if self._training_elapsed >= duration:
            self._training_elapsed -= duration
            self._training_phase_idx += 1
            if self._training_phase_idx >= len(TRAINING_PHASES):
                self._training_phase_idx = 0
                self._training_cycle += 1
                if self._training_cycle >= TRAINING_CYCLES:
                    self._finish_training()
                    return
            self._update_training_guide()
            phase = TRAINING_PHASES[self._training_phase_idx]
            _, duration, _, start_scale, end_scale, fg_color = phase
        t = self._training_elapsed / duration
        scale = start_scale + (end_scale - start_scale) * ease_in_out_quad(t)
        new_size = max(1, int(self._breath_base_size * scale))
        self.pet_label.configure(font=('Segoe UI Emoji', new_size))
        self.pet_label.configure(fg=fg_color if fg_color else self._normal_color)

    # ---- 启动 ----
    def run(self):
        self.update_display()
        # 皮肤轮换
        def rotate():
            self.skin_manager.next_skin()
            self.update_display()
            self.root.after(self.skin_manager.get_rotate_interval_ms(), rotate)
        self.root.after(self.skin_manager.get_rotate_interval_ms(), rotate)
        # 呼吸动画
        self._breath_timer = self.root.after(ANIM_FRAME_MS, self._animation_tick)
        self.root.mainloop()


# ================================================================
#  入口
# ================================================================
def main():
    import sys

    # 找或创建 config.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print('Breathing Pet 启动中...')
        print(f'   config.json 已加载')
    else:
        config = DEFAULT_CONFIG
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print('Breathing Pet 首次启动')
        print(f'   已生成 config.json，可编辑后重启自定义')

    print(f'   宠物数量: {len(config["pet"]["emoji_list"])}')
    print(f'   呼吸节奏: 吸气 {config["pet"]["breath_inhale_ms"]/1000}s / 呼气 {config["pet"]["breath_exhale_ms"]/1000}s')
    print(f'   宠物颜色: {config["pet"].get("pet_color", "纯白")}')
    print(f'   右键打开菜单 | 双击换宠物 | 三击呼吸训练')
    print()

    pet = BreathingPet(config)
    pet.config_path = config_path
    pet.run()


if __name__ == '__main__':
    main()
