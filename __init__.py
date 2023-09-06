from pathlib import Path

def _process_lines(src: str):
    lines: list[str] = []
    
    i = 0
    l = src.splitlines()
    ll = len(l)
    
    cur_stack: str = ''
    stacking: bool = False
    
    while i < ll:
        v = l[i].strip()
        
        if len(v) == 0:
            stacking = False
            lines.append(cur_stack)
            continue
        
        if '#' in v and len(v := v[v.find('#'):].strip()) == 0:
            stacking = False
            lines.append(cur_stack)
            continue
        
        if stacking:
            stacking = v[-1] == '\\'
            cur_stack += v[:-1] if stacking else v
            if not stacking:
                lines.append(cur_stack)
        
        if v[-1] == '\\':
            cur_stack = v[:-1]
            stacking = True
            continue
        
        
        lines.append(v)
        i += 1
    
    # if a stack isn't finished
    if stacking:
        lines.append(cur_stack)
    
    
    return lines

class Hive:
    name: str
    path: Path
    source_folder: Path
    
    # TODO: Add commands support!!!
    @classmethod
    def _parse_lines(cls, lines: list[str]):
        vals = {}
        for i in lines:
            if '=' in i:
                vals[i[:i.find('=')]] = i[i.find('='):]
            else:
                vals[i] = None
        return cls(**vals)
    
    @classmethod
    def _parse(cls, src: str):
        return _parse_lines(_process_lines(src))
    
def run(hive):
    ...