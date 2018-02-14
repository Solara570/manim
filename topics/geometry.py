from helpers import *

from mobject import Mobject
from mobject.vectorized_mobject import VMobject, VGroup

class Arc(VMobject):
    CONFIG = {
        "radius"           : 1.0,
        "start_angle"      : 0,
        "num_anchors"      : 9,
        "anchors_span_full_range" : True,
    }
    def __init__(self, angle, **kwargs):
        self.angle = angle
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        anchors = np.array([
            np.cos(a)*RIGHT+np.sin(a)*UP
            for a in np.linspace(
                self.start_angle, 
                self.start_angle + self.angle, 
                self.num_anchors
            )
        ])
        #Figure out which control points will give the
        #Appropriate tangent lines to the circle
        d_theta = self.angle/(self.num_anchors-1.0)
        tangent_vectors = np.zeros(anchors.shape)
        tangent_vectors[:,1] = anchors[:,0]
        tangent_vectors[:,0] = -anchors[:,1]
        handles1 = anchors[:-1] + (d_theta/3)*tangent_vectors[:-1]
        handles2 = anchors[1:] - (d_theta/3)*tangent_vectors[1:]
        self.set_anchors_and_handles(
            anchors, handles1, handles2
        )
        self.scale(self.radius, about_point = ORIGIN)

    def add_tip(self, tip_length = 0.25, at_start = False, at_end = True):
        # clear out any old tips
        for submob in self.submobjects:
            if submob.mark_paths_closed == True: # is a tip
                self.remove(submob)

        #TODO, do this a better way
        p1 = p2 = p3 = p4 = None
        start_arrow = end_arrow = None
        if at_start:
            p1, p2 = self.points[-3:-1]
            # self.points[-2:] did overshoot
            start_arrow = Arrow(
                p1, 2*p2 - p1, 
                tip_length = tip_length,
                max_tip_length_to_length_ratio = 2.0
            )
            self.add(start_arrow.split()[-1]) # just the tip

        if at_end:
            p4, p3 = self.points[1:3]
            # self.points[:2] did overshoot
            end_arrow = Arrow(
                p3, 2*p4 - p3, 
                tip_length = tip_length,
                max_tip_length_to_length_ratio = 2.0
            )
            self.add(end_arrow.split()[-1])
        



        
        self.highlight(self.get_color())
        return self



    def get_arc_center(self):
        first_point = self.points[0]
        radial_unit_vector = np.array([np.cos(self.start_angle),np.sin(self.start_angle),0])
        arc_center = first_point - self.radius * radial_unit_vector
        return arc_center


    def move_arc_center_to(self,point):
        v = point - self.get_arc_center()
        self.shift(v)
        return self


    def stop_angle(self):
        return self.start_angle + self.angle

    def set_bound_angles(self,start=0,stop=np.pi):
        self.start_angle = start
        self.angle = stop - start
        
        return self

class Circle(Arc):
    CONFIG = {
        "color" : RED,
        "close_new_points" : True,
        "anchors_span_full_range" : False
    }
    def __init__(self, **kwargs):
        Arc.__init__(self, 2*np.pi, **kwargs)

    def surround(self, mobject, dim_to_match = 0, stretch = False, buffer_factor = 1.2):
        # Ignores dim_to_match and stretch; result will always be a circle
        # TODO: Perhaps create an ellipse class to handle singele-dimension stretching
        self.replace(mobject, dim_to_match, stretch)
        self.scale_to_fit_width(np.sqrt(mobject.get_width()**2 + mobject.get_height()**2))
        self.scale(buffer_factor)

class Dot(Circle):
    CONFIG = {
        "radius"       : 0.08,
        "stroke_width" : 0,
        "fill_opacity" : 1.0,
        "color" : WHITE
    }
    def __init__(self, point = ORIGIN, **kwargs):
        Circle.__init__(self, **kwargs)
        self.shift(point)
        self.init_colors()

class Ellipse(VMobject):
    CONFIG = {
        "width" : 2,
        "height" : 1
    }

    def generate_points(self):
        circle = Circle(radius = 1)
        circle = circle.stretch_to_fit_width(self.width)
        circle = circle.stretch_to_fit_height(self.height)
        self.points = circle.points

class AnnularSector(VMobject):
    CONFIG = {
        "inner_radius" : 1,
        "outer_radius" : 2,
        "angle" : TAU/4,
        "start_angle" : 0,
        "fill_opacity" : 1,
        "stroke_width" : 0,
        "color" : WHITE,
        "mark_paths_closed" : True,
    }
    def generate_points(self):
        arc1 = Arc(
            angle = self.angle,
            start_angle = self.start_angle,
            radius = self.inner_radius,
        )
        arc2 = Arc(
            angle = -1*self.angle,
            start_angle = self.start_angle+self.angle,
            radius = self.outer_radius,
        )
        a1_to_a2_points = np.array([
            interpolate(arc1.points[-1], arc2.points[0], alpha)
            for alpha in np.linspace(0, 1, 4)
        ])
        a2_to_a1_points = np.array([
            interpolate(arc2.points[-1], arc1.points[0], alpha)
            for alpha in np.linspace(0, 1, 4)
        ])
        self.points = np.array(arc1.points)
        self.add_control_points(a1_to_a2_points[1:])
        self.add_control_points(arc2.points[1:])
        self.add_control_points(a2_to_a1_points[1:])


    def get_arc_center(self):
        first_point = self.points[0]
        last_point = self.points[-2]
        v = last_point - first_point
        radial_unit_vector = v/np.linalg.norm(v)
        arc_center = first_point - self.inner_radius * radial_unit_vector
        return arc_center

    def move_arc_center_to(self,point):
        v = point - self.get_arc_center()
        self.shift(v)
        return self

class Sector(AnnularSector):
    CONFIG = {
        "outer_radius" : 1,
        "inner_radius" : 0
    }

    @property
    def radius(self):
        return self.outer_radius

    @radius.setter
    def radius(self,new_radius):
        self.outer_radius = new_radius

class Annulus(Circle):
    CONFIG = {
        "inner_radius": 1,
        "outer_radius": 2,
        "fill_opacity" : 1,
        "stroke_width" : 0,
        "color" : WHITE,
        "mark_paths_closed" : False,
        "propagate_style_to_family" : True
    }

    def generate_points(self):
        self.points = []
        self.radius = self.outer_radius
        outer_circle = Circle(radius = self.outer_radius)
        inner_circle = Circle(radius=self.inner_radius)
        inner_circle.flip()
        self.points = outer_circle.points
        self.add_subpath(inner_circle.points)

class Line(VMobject):
    CONFIG = {
        "buff" : 0,
        "path_arc" : None, # angle of arc specified here
        "n_arc_anchors" : 10, #Only used if path_arc is not None
    }
    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        self.set_start_and_end(start, end)
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        if self.path_arc is None:
            self.set_points_as_corners([self.start, self.end])
        else:
            path_func = path_along_arc(self.path_arc)
            self.set_points_smoothly([
                path_func(self.start, self.end, alpha)
                for alpha in np.linspace(0, 1, self.n_arc_anchors)
            ])
        self.account_for_buff()

    def set_path_arc(self,new_value):
        self.path_arc = new_value
        self.generate_points()

    def account_for_buff(self):
        length = self.get_arc_length()
        if length < 2*self.buff or self.buff == 0:
            return
        buff_proportion = self.buff / length
        self.pointwise_become_partial(
            self, buff_proportion, 1 - buff_proportion
        )

    def set_start_and_end(self, start, end):
        start_to_end = self.pointify(end) - self.pointify(start)
        vect = np.zeros(len(start_to_end))
        longer_dim = np.argmax(map(abs, start_to_end))
        vect[longer_dim] = start_to_end[longer_dim]
        self.start, self.end = [
            arg.get_edge_center(unit*vect)
            if isinstance(arg, Mobject)
            else np.array(arg)
            for arg, unit in zip([start, end], [1, -1])
        ]

    def pointify(self, mob_or_point):
        if isinstance(mob_or_point, Mobject):
            return mob_or_point.get_center()
        return np.array(mob_or_point)

    def get_length(self):
        start, end = self.get_start_and_end()
        return np.linalg.norm(start - end)

    def get_arc_length(self):
        if self.path_arc:
            anchors = self.get_anchors()
            return sum([
                np.linalg.norm(a2-a1)
                for a1, a2 in zip(anchors, anchors[1:])
            ])
        else:
            return self.get_length()

    def get_start_and_end(self):
        return self.get_start(), self.get_end()

    def get_vector(self):
        return self.get_end() - self.get_start()

    def get_start(self):
        return np.array(self.points[0])

    def get_end(self):
        return np.array(self.points[-1])

    def get_slope(self):
        start, end = self.get_start_and_end()
        rise, run = [
            float(end[i] - start[i])
            for i in [1, 0]
        ]
        return np.inf if run == 0 else rise/run

    def get_angle(self):
        start, end = self.get_start_and_end()
        return angle_of_vector(end-start)

    # def put_start_and_end_on(self, new_start, new_end):
    #     self.set_start_and_end(new_start, new_end)
    #     self.buff = 0
    #     self.generate_points()

    def put_start_and_end_on(self, new_start, new_end):
        self.start = new_start
        self.end = new_end
        self.buff = 0
        self.generate_points()
        return

    def put_start_and_end_on_with_projection(self, new_start, new_end):
        target_vect = np.array(new_end) - np.array(new_start)
        curr_vect = self.get_vector()
        curr_norm = np.linalg.norm(curr_vect)
        if curr_norm == 0:
            self.put_start_and_end_on(new_start, new_end)
            return
        target_norm = np.linalg.norm(target_vect)
        if target_norm == 0:
            epsilon = 0.001
            self.scale(epsilon/curr_norm)
            self.move_to(new_start)
            return
        unit_target = target_vect / target_norm
        unit_curr = curr_vect / curr_norm
        normal = np.cross(unit_target, unit_curr)
        if np.linalg.norm(normal) == 0:
            if unit_curr[0] == 0 and unit_curr[1] == 0:
                normal = UP
            else:
                normal = OUT
        angle_diff = np.arccos(
            np.clip(np.dot(unit_target, unit_curr), -1, 1)
        )
        self.scale(target_norm/curr_norm)
        self.rotate(-angle_diff, normal)
        self.shift(new_start - self.get_start())
        return self

    def insert_n_anchor_points(self, n):
        if not self.path_arc:
            n_anchors = self.get_num_anchor_points()
            new_num_points = 3*(n_anchors + n)-2
            self.points = np.array([
                self.point_from_proportion(alpha)
                for alpha in np.linspace(0, 1, new_num_points)
            ])
        else:
            VMobject.insert_n_anchor_points(self, n)

class DashedLine(Line):
    CONFIG = {
        "dashed_segment_length" : 0.05
    }
    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs
        Line.__init__(self, *args, **kwargs)

    def generate_points(self):
        length = np.linalg.norm(self.end-self.start)
        num_interp_points = int(length/self.dashed_segment_length)
        points = [
            interpolate(self.start, self.end, alpha)
            for alpha in np.linspace(0, 1, num_interp_points)
        ]
        includes = it.cycle([True, False])
        self.submobjects = [
            Line(p1, p2, **self.init_kwargs)
            for p1, p2, include in zip(points, points[1:], includes)
            if include
        ]
        self.put_start_and_end_on_with_projection(self.start, self.end)
        return self

    def get_start(self):
        if len(self.points) > 0:
            return self[0].points[0]
        else:
            return self.start

    def get_end(self):
        if len(self) > 0:
            return self[-1].points[-1]
        else:
            return self.end

class Arrow(Line):
    CONFIG = {
        "color"      : YELLOW_C,
        "tip_length" : 0.25,
        "tip_width_to_length_ratio"  : 1,
        "max_tip_length_to_length_ratio" : 0.35,
        "max_stem_width_to_tip_width_ratio" : 0.3,
        "buff" : MED_SMALL_BUFF,
        "propagate_style_to_family" : False,
        "preserve_tip_size_when_scaling" : True,
        "normal_vector" : OUT,
        "use_rectangular_stem" : True,
        "rectangular_stem_width" : 0.05,
    }
    def __init__(self, *args, **kwargs):
        points = map(self.pointify, args)
        if len(args) == 1:
            args = (points[0]+UP+LEFT, points[0])
        Line.__init__(self, *args, **kwargs)
        self.init_tip()
        if self.use_rectangular_stem and not hasattr(self, "rect"):
            self.add_rectangular_stem()
        self.init_colors()

    def init_tip(self):
        self.tip = self.add_tip()

    def add_tip(self, add_at_end = True):
        tip = VMobject(
            close_new_points = True,
            mark_paths_closed = True,
            fill_color = self.color,
            fill_opacity = 1,
            stroke_color = self.color,
            stroke_width = 0,
        )
        self.set_tip_points(tip, add_at_end, preserve_normal = False)
        self.add(tip)
        return tip

    def add_rectangular_stem(self):
        self.rect = Rectangle(
            stroke_width = 0,
            fill_color = self.tip.get_fill_color(),
            fill_opacity = self.tip.get_fill_opacity()
        )
        self.add_to_back(self.rect)
        self.set_stroke(width = 0)
        self.set_rectangular_stem_points()

    def set_rectangular_stem_points(self):
        start, end = self.get_start_and_end()
        vect = end - start
        tip_base_points = self.tip.get_anchors()[1:]
        tip_base = center_of_mass(tip_base_points)
        tbp1, tbp2 = tip_base_points
        perp_vect = tbp2 - tbp1
        tip_base_width = np.linalg.norm(perp_vect)
        if tip_base_width > 0:
            perp_vect /= tip_base_width
        width = min(
            self.rectangular_stem_width,
            self.max_stem_width_to_tip_width_ratio*tip_base_width,
        )
        if hasattr(self, "second_tip"):
            start = center_of_mass(
                self.second_tip.get_anchors()[1:]
            )
        self.rect.set_points_as_corners([
            tip_base + perp_vect*width/2,
            start + perp_vect*width/2,
            start - perp_vect*width/2,
            tip_base - perp_vect*width/2,
        ])
        return self

    def set_tip_points(
        self, tip, 
        add_at_end = True, 
        tip_length = None,
        preserve_normal = True,
        ):
        if tip_length is None:
            tip_length = self.tip_length
        if preserve_normal:
            normal_vector = self.get_normal_vector()
        else:
            normal_vector = self.normal_vector
        line_length = np.linalg.norm(self.points[-1]-self.points[0])
        tip_length = min(
            tip_length, self.max_tip_length_to_length_ratio*line_length
        )

        indices = (-2, -1) if add_at_end else (1, 0)
        pre_end_point, end_point = [
            self.get_anchors()[index]
            for index in indices
        ]
        vect = end_point - pre_end_point
        perp_vect = np.cross(vect, normal_vector)
        for v in vect, perp_vect:
            if np.linalg.norm(v) == 0:
                v[0] = 1
            v *= tip_length/np.linalg.norm(v)
        ratio = self.tip_width_to_length_ratio
        tip.set_points_as_corners([
            end_point, 
            end_point-vect+perp_vect*ratio/2,
            end_point-vect-perp_vect*ratio/2,
        ])

        return self

    def get_normal_vector(self):
        p0, p1, p2 = self.tip.get_anchors()
        result = np.cross(p2 - p1, p1 - p0)
        norm = np.linalg.norm(result)
        if norm == 0:
            return self.normal_vector
        else:
            return result/norm

    def reset_normal_vector(self):
        self.normal_vector = self.get_normal_vector()
        return self

    def get_end(self):
        if hasattr(self, "tip"):
            return self.tip.get_anchors()[0]
        else:
            return Line.get_end(self)

    def get_tip(self):
        return self.tip

    def put_start_and_end_on(self, *args, **kwargs):
        Line.put_start_and_end_on(self, *args, **kwargs)
        self.set_tip_points(self.tip, preserve_normal = False)
        self.set_rectangular_stem_points()
        return self

    def scale(self, scale_factor, **kwargs):
        Line.scale(self, scale_factor, **kwargs)
        if self.preserve_tip_size_when_scaling:
            self.set_tip_points(self.tip)
        if self.use_rectangular_stem:
            self.set_rectangular_stem_points()
        return self

    def copy(self):
        return self.deepcopy()

class Vector(Arrow):
    CONFIG = {
        "color" : YELLOW,
        "buff"  : 0,
    }
    def __init__(self, direction, **kwargs):
        if len(direction) == 2:
            direction = np.append(np.array(direction), 0)
        Arrow.__init__(self, ORIGIN, direction, **kwargs)

class DoubleArrow(Arrow):
    def init_tip(self):
        self.tip = self.add_tip()
        self.second_tip = self.add_tip(add_at_end = False)

class CubicBezier(VMobject):
    def __init__(self, points, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points(points)

class Polygon(VMobject):
    CONFIG = {
        "color" : GREEN_D,
        "mark_paths_closed" : True,
        "close_new_points" : True,
    }
    def __init__(self, *vertices, **kwargs):
        assert len(vertices) > 1
        digest_locals(self)
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        self.set_anchor_points(self.vertices, mode = "corners")

    def get_vertices(self):
        return self.get_anchors_and_handles()[0]

class RegularPolygon(Polygon):
    CONFIG = {
        "start_angle" : 0
    }
    def __init__(self, n = 3, **kwargs):
        digest_config(self, kwargs, locals())
        start_vect = rotate_vector(RIGHT, self.start_angle)
        vertices = compass_directions(n, start_vect)
        Polygon.__init__(self, *vertices, **kwargs)

class Rectangle(VMobject):
    CONFIG = {
        "color"  : WHITE,
        "height" : 2.0,
        "width"  : 4.0,
        "mark_paths_closed" : True,
        "close_new_points" : True,
    }
    def generate_points(self):
        y, x = self.height/2., self.width/2.
        self.set_anchor_points([
            x*LEFT+y*UP,
            x*RIGHT+y*UP,
            x*RIGHT+y*DOWN,
            x*LEFT+y*DOWN
        ], mode = "corners")

class Square(Rectangle):
    CONFIG = {
        "side_length" : 2.0,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Rectangle.__init__(
            self, 
            height = self.side_length,
            width = self.side_length,
            **kwargs
        )

class SurroundingRectangle(Rectangle):
    CONFIG = {
        "color" : YELLOW,
        "buff" : SMALL_BUFF,
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        kwargs["width"] = mobject.get_width() + 2*self.buff
        kwargs["height"] = mobject.get_height() + 2*self.buff
        Rectangle.__init__(self, **kwargs)
        self.move_to(mobject)

class BackgroundRectangle(SurroundingRectangle):
    CONFIG = {
        "color" : BLACK,
        "stroke_width" : 0,
        "fill_opacity" : 0.75,
        "buff" : 0
    }
    def __init__(self, mobject, **kwargs):
        SurroundingRectangle.__init__(self, mobject, **kwargs)
        self.original_fill_opacity = self.fill_opacity

    def pointwise_become_partial(self, mobject, a, b):
        self.set_fill(opacity = b*self.original_fill_opacity)
        return self

    def get_fill_color(self):
        return Color(self.color)

class FullScreenFadeRectangle(Rectangle):
    CONFIG = {
        "height" : 2*SPACE_HEIGHT,
        "width" : 2*SPACE_WIDTH,
        "stroke_width" : 0,
        "fill_color" : BLACK,
        "fill_opacity" : 0.7,
    }

class ScreenRectangle(Rectangle):
    CONFIG = {
        "width_to_height_ratio" : 16.0/9.0,
        "height" : 4,
    }
    def generate_points(self):
        self.width = self.width_to_height_ratio * self.height
        Rectangle.generate_points(self)

class PictureInPictureFrame(Rectangle):
    CONFIG = {
        "height" : 3,
        "aspect_ratio" : (16, 9)
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        height = self.height
        if "height" in kwargs:
            kwargs.pop("height")
        Rectangle.__init__(
            self,
            width = self.aspect_ratio[0],
            height = self.aspect_ratio[1],
            **kwargs
        )
        self.scale_to_fit_height(height)

class Cross(VGroup):
    CONFIG = {
        "stroke_color" : RED,
        "stroke_width" : 6,
    }
    def __init__(self, mobject, **kwargs):
        VGroup.__init__(self, 
            Line(UP+LEFT, DOWN+RIGHT),
            Line(UP+RIGHT, DOWN+LEFT),
        )
        self.replace(mobject, stretch = True)
        self.set_stroke(self.stroke_color, self.stroke_width)

class Grid(VMobject):
    CONFIG = {
        "height" : 6.0,
        "width"  : 6.0,
    }
    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width+x_step, x_step):
            self.add(Line(
                [x-self.width/2., -self.height/2., 0],
                [x-self.width/2., self.height/2., 0],
            ))
        for y in np.arange(0, self.height+y_step, y_step):
            self.add(Line(
                [-self.width/2., y-self.height/2., 0],
                [self.width/2., y-self.height/2., 0]
            ))



