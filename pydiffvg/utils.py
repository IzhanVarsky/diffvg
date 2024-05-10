import pydiffvg


def rescale_points(shapes, shape_groups, scale,
                   old_width=None, old_height=None):
    # Rescales the x,y points using scale.
    # Examples:
    # If scale is 1, then the original SVG will be returned
    # If scale is 0.5, then the points will be halved
    for shape in shapes:
        shape.stroke_width *= scale
        if isinstance(shape, pydiffvg.Rect):
            shape.p_max *= scale
            shape.p_min *= scale
        elif isinstance(shape, pydiffvg.Path) or isinstance(shape, pydiffvg.Polygon):
            shape.points *= scale
        elif isinstance(shape, pydiffvg.Circle) or isinstance(shape, pydiffvg.Ellipse):
            shape.radius *= scale
            shape.center *= scale
    for shape_group in shape_groups:
        if isinstance(shape_group.fill_color, pydiffvg.LinearGradient):
            shape_group.fill_color.begin *= scale
            shape_group.fill_color.end *= scale
        if isinstance(shape_group.fill_color, pydiffvg.RadialGradient):
            shape_group.fill_color.radius *= scale
            shape_group.fill_color.center *= scale
        if isinstance(shape_group.stroke_color, pydiffvg.LinearGradient):
            shape_group.stroke_color.begin *= scale
            shape_group.stroke_color.end *= scale
        if isinstance(shape_group.stroke_color, pydiffvg.RadialGradient):
            shape_group.stroke_color.radius *= scale
            shape_group.stroke_color.center *= scale
    if old_width is not None and old_height is not None:
        return old_width * scale, old_height * scale


def normalize_points(shapes, shape_groups, old_width, old_height):
    # Rescales points to [0, 1] range. (It is expected that max(points) < max(width, height)).
    scale = 1 / max(old_width, old_height)
    return rescale_points(shapes, shape_groups, scale, old_width, old_height)
