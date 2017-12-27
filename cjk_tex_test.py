#!/usr/bin/env python
#coding=utf-8

from helpers import *

from scene import Scene
from camera import Camera
from animation.simple_animations import *
from animation.transform import *
from mobject.mobject import *
from mobject.tex_mobject import *

# Test passed
class CJKPackageTest(Scene):
    def construct(self):
        tex = TexMobject("\\dfrac{\\text{中文}}{\\text{测试}}").shift(UP).scale(2)
        text = TextMobject("中文测试").shift(DOWN).scale(2).highlight(BLUE)
        self.play(Write(tex))
        self.dither(0.5)
        self.play(Transform(tex, text), run_time = 2)
        self.dither(0.5)

if __name__ == '__main__':
    import os
    current_dir = os.getcwd()
    os.chdir(current_dir)
    os.system("python extract_scene.py -p cjk_tex_test.py CJKPackageTest")