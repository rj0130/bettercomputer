#!/usr/bin/env python3
"""Stdlib-only loader for the YAML subset used under phone/spec/.

phone/spec/device.yaml declares its own contract in its header comment: flat
maps and lists only, no anchors or aliases. This loader implements exactly
that subset — block mappings, block sequences (of scalars or mappings),
inline flow sequences (`[a, b, c]`), quoted and bare scalars, and comments —
and nothing else. It is not a general YAML parser; unsupported constructs
raise SpecLoadError rather than silently misparsing.
"""
import sys


class SpecLoadError(ValueError):
    pass


def _strip_comment(line):
    in_single = in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if i == 0 or line[i - 1] in " \t":
                return line[:i]
    return line


def _tokenize(text):
    """Return [(indent, content, lineno), ...] for every non-blank line."""
    tokens = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw:
            raise SpecLoadError(f"line {lineno}: tabs are not allowed")
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        tokens.append((indent, line.strip(), lineno))
    return tokens


def _parse_scalar(s):
    s = s.strip()
    if s == "" or s == "~" or s == "null":
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        return _parse_flow_list(s)
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _parse_flow_list(s):
    inner = s[1:-1].strip()
    if not inner:
        return []
    items = []
    in_single = in_double = False
    cur = ""
    for ch in inner:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if ch == "," and not in_single and not in_double:
            items.append(cur)
            cur = ""
            continue
        cur += ch
    items.append(cur)
    return [_parse_scalar(i) for i in items]


def _split_key_value(content, lineno):
    """Split 'key: value' on the first unquoted, un-bracketed colon."""
    in_single = in_double = False
    depth = 0
    for i, ch in enumerate(content):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch in "[{" and not in_single and not in_double:
            depth += 1
        elif ch in "]}" and not in_single and not in_double:
            depth -= 1
        elif ch == ":" and not in_single and not in_double and depth == 0:
            if i + 1 == len(content) or content[i + 1] == " ":
                return content[:i].strip(), content[i + 1 :].strip()
    raise SpecLoadError(f"line {lineno}: expected 'key: value', got {content!r}")


def _parse_mapping(tokens, pos, indent):
    result = {}
    while pos < len(tokens):
        cur_indent, content, lineno = tokens[pos]
        if cur_indent != indent or content.startswith("- "):
            break
        key, value_str = _split_key_value(content, lineno)
        if key in result:
            raise SpecLoadError(f"line {lineno}: duplicate key {key!r}")
        pos += 1
        if value_str == "":
            if pos < len(tokens) and tokens[pos][0] > indent:
                value, pos = _parse_block(tokens, pos, tokens[pos][0])
            else:
                value = None
            result[key] = value
        else:
            result[key] = _parse_scalar(value_str)
    return result, pos


def _parse_sequence(tokens, pos, indent):
    items = []
    while pos < len(tokens):
        cur_indent, content, lineno = tokens[pos]
        if cur_indent != indent or not content.startswith("- "):
            break
        rest = content[2:]
        pos += 1
        if rest == "":
            value, pos = _parse_block(tokens, pos, indent + 2)
            items.append(value)
            continue
        try:
            key, value_str = _split_key_value(rest, lineno)
        except SpecLoadError:
            # A bare scalar sequence item, e.g. "- USB3:1".
            items.append(_parse_scalar(rest))
            continue
        item = {key: (_parse_scalar(value_str) if value_str != "" else None)}
        if value_str == "":
            item[key], pos = _parse_block(tokens, pos, indent + 4)
        # Further keys of the same mapping item, aligned just past "- ".
        while pos < len(tokens) and tokens[pos][0] == indent + 2:
            k2, v2_str = _split_key_value(tokens[pos][1], tokens[pos][2])
            pos += 1
            if v2_str == "":
                value, pos = _parse_block(tokens, pos, indent + 4)
                item[k2] = value
            else:
                item[k2] = _parse_scalar(v2_str)
        items.append(item)
    return items, pos


def _parse_block(tokens, pos, indent):
    if pos >= len(tokens):
        return None, pos
    first_indent, first_content, lineno = tokens[pos]
    if first_indent != indent:
        raise SpecLoadError(f"line {lineno}: expected indent {indent}, got {first_indent}")
    if first_content.startswith("- "):
        return _parse_sequence(tokens, pos, indent)
    return _parse_mapping(tokens, pos, indent)


def loads(text):
    tokens = _tokenize(text)
    if not tokens:
        return {}
    value, pos = _parse_block(tokens, 0, tokens[0][0])
    if pos != len(tokens):
        _, _, lineno = tokens[pos]
        raise SpecLoadError(f"line {lineno}: unexpected content (bad indent or structure)")
    return value


def load(path):
    with open(path) as f:
        return loads(f.read())


if __name__ == "__main__":
    import json

    for path in sys.argv[1:] or ["phone/spec/device.yaml"]:
        print(json.dumps(load(path), indent=2))
