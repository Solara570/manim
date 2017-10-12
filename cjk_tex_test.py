#!/usr/bin/env python
#coding=utf-8

from helpers import *

from scene import Scene
from camera import Camera
from animation.simple_animations import Write
from animation.transform import Transform
from mobject.tex_mobject import TexMobject

class CJKTexMobject(TexMobject):
    CONFIG = {
    # Font: hwzs (HuaWenZhongSong)
        "template_tex_file" : "tex_cjk_template.tex",
        "encoding" : "GBK",
    }

class CJKTextMobject(CJKTexMobject):
    CONFIG = {
        "template_tex_file" : "text_cjk_template.tex",
    }

# Test passed
class CJKPackageTest(Scene):
    def construct(self):
        tex = CJKTexMobject("\\dfrac{\\text{中文}}{\\text{测试}}").shift(UP).scale(2)
        text = CJKTextMobject("中文测试").shift(DOWN).scale(2).highlight(BLUE)
        self.play(Write(tex))
        self.dither(0.5)
        self.play(Transform(tex, text))
        self.dither(0.5)

