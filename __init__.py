from pathlib import Path

class Hive:
    name: str
    path: Path
    source_folder: Path
    
    @classmethod
    def _parse_lines(cls, lines: list[str]):
        vals = []
        for i in lines:
            if len(i) == 0:
                continue
            
        return cls(*vals)
    
    @classmethod
    def _parse(cls, src: str):
        return _parse_lines([i.strip() for i in src.splitlines()])
    
    
    


