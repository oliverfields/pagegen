#!/usr/bin/env python3

"""
Generate artifacts for theme in site/<env>:
- svg symbols file
- css
"""

from sys import path, argv
from string import Template
from json import load, dump
from rcssmin import cssmin
from colorsys import rgb_to_hls, hls_to_rgb
from pagegen.utility_no_deps import report_error, report_warning


def css_svg_data_url(symbol):
    svg_data = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{symbol["viewBox"]}"><path d="{symbol["paths"][0]}"></path></svg>'
    data_url = f'data:image/svg+xml,{svg_data}'
    data_url = f"url('{data_url}')"

    return data_url


def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return "{:02x}{:02x}{:02x}".format(r,g,b)


def rgb_to_hsl(r, g, b):
    # https://stackoverflow.com/questions/39118528/rgb-to-hsl-conversion

    # Make r, g, and b fractions of 1
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    # Find greatest and smallest channel values
    cmin = min(r,g,b)
    cmax = max(r,g,b)
    delta = cmax - cmin
    h = 0,
    s = 0,
    l = 0;

    # Calculate hue
    # No difference
    if delta == 0:
        h = 0
    # Red is max
    elif cmax == r:
        h = ((g - b) / delta) % 6
    # Green is max
    elif cmax == g:
        h = (b - r) / delta + 2
    # Blue is max
    else:
        h = (r - g) / delta + 4

    h = round(h * 60)

    # Make negative hues positive behind 360°
    if h < 0:
        h += 360

    # Calculate lightness
    l = (cmax + cmin) / 2

    # Calculate saturation
    #s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));
    s = 0 if delta == 0 else delta / (1 - abs(2 * l - 1))

    # Multiply l and s by 100
    s = round(s * 100, 1)
    l = round(l * 100, 1)

    return (h, s, l)


def hsl_to_rgb(h, s, l):
    # Normalize the input HSL values
    s /= 100
    l /= 100

    # Calculate the chroma (C)
    c = (1 - abs(2 * l - 1)) * s

    # Calculate the intermediate values x and m
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    # Initialize RGB values (before adding m)
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    # Add the m value to each RGB component
    r, g, b = (r + m), (g + m), (b + m)

    # Convert RGB to 0-255 scale and round to nearest integer
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)

    return (r, g, b)


def split_hsl_str(hsl_str):
    hsl = hsl_str.split(',')
    h = hsl[0]
    s = hsl[1]
    l = hsl[2]
    return (float(h), float(s), float(l))


def hsl_str_to_hex(hsl_str):
    h, s, l = split_hsl_str(hsl_str)
    r, g, b = hsl_to_rgb(h, s, l)

    return rgb_to_hex(r, g, b)


def hex_to_hsl(hex_str):
    # Remove any # prefix
    hex_str = hex_str.lstrip('#')
    r, g, b = hex_to_rgb(hex_str)
    h, s, l = rgb_to_hsl(r, g, b)

    return f'{h},{s},{l}'


def generate_css(template_path, target_path, symbols, colors_json_path):
    json_is_dirty = False

    with open(colors_json_path) as c_s:
        color_schemes = load(c_s)

    color_table = []
    # Work out hsl and hex values, hsl is primary source of truth
    for scheme_name, scheme in color_schemes.items():
        for color_name, color in scheme.items():
            if not 'hex' in color.keys() and not 'hsl' in color.keys():
                report_error(1, f'Error: No hsl or hex color for {scheme_name}.{color_name}')

            elif not 'hex' in color.keys():
                color['hex'] = hsl_str_to_hex(color['hsl'])
                json_is_dirty = True

            elif not 'hsl' in color.keys():
                color['hsl'] = hex_to_hsl(color['hex'])
                json_is_dirty = True
            else:
                # If both hsl and hex exist then ensure hex is same as hsl
                hex_from_hsl = hsl_str_to_hex(color['hsl'])
                if hex_from_hsl != color['hex']:
                    color['hex'] = hex_from_hsl
                    json_is_dirty = True

                    report_warning(f'Warning: Color #{color["hex"]} does not match hsl({color["hsl"]}) in {scheme_name}.{color_name}, setting hex to #{hex_from_hsl}')

    if json_is_dirty:
        dump(color_schemes, open(colors_json_path, 'w'), indent=2)
        report_warning(f'Updated {colors_json_path}')

    with open(template_path, 'r') as css_tpl:
        css_template = Template(css_tpl.read())

    css_substitution_rules = {}
    for scheme_name, scheme in color_schemes.items():
        for color_name, color in scheme.items():
           h, s, l = split_hsl_str(color['hsl'])
           css_substitution_rules[scheme_name + '_' + color_name.replace('-', '_')] = f'hsl({h},{s}%,{l}%)'

    css_substitution_rules['wave_line_svg_url'] = css_svg_data_url(symbols['wave-line'])

    css = css_template.substitute(css_substitution_rules)

    css = cssmin(css)

    with open(target_path, 'w') as css_target:
        css_target.write(css)


def generate_svg_symbols(symbols, target_path):

    svg = '<svg xmlns="http://www.w3.org/2000/svg">\n'
    for name, symbol in symbols.items():
        svg += f'<symbol id="{name}">\n<path d="{symbol["paths"][0]}" />\n</symbol>\n'
    svg += '</svg>'

    with open(target_path, 'w') as t:
        t.write(svg)


build_dir = path[0]
pagegen_target_dir = argv[1] + '/assets/theme'

with open(build_dir + '/symbols.json') as j:
    symbols = load(j)

generate_css(build_dir + '/css.template', pagegen_target_dir + '/site.css', symbols, build_dir + '/color_schemes.json')
generate_svg_symbols(symbols, pagegen_target_dir + '/symbols.svg')

