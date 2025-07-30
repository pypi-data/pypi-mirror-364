import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from loguru import logger as log


@dataclass
class Caller:
    depth: int
    filename: str
    name: str
    function: str
    line: int
    is_frozen: bool
    is_init: bool
    code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Caller':
        """Create Caller from dictionary (supports **dict unpacking)"""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)  # type: ignore
import inspect
from pathlib import Path
from loguru import logger as log

def get_import_chain(verbose: bool = False) -> dict | list:
    """Get the full import chain for debugging"""
    stack = inspect.stack()
    chain = []

    for i, frame_info in enumerate(stack[1:], 1):
        filepath = Path(frame_info.filename)

        frame_data = {
            'depth': i,
            'filename': frame_info.filename,
            'name': filepath.name,
            'function': frame_info.function,
            'line': frame_info.lineno,
            'is_frozen': frame_info.filename.startswith('<frozen'),
            'is_init': filepath.name == '__init__.py',
            'is_module_level': frame_info.function == '<module>',
            'code': frame_info.code_context[0].strip() if frame_info.code_context else None
        }

        chain.append(frame_data)

        # Skip frozen imports and __init__.py files
        if frame_data['is_frozen'] or frame_data['is_init']:
            status = "SKIP"
        else:
            status = "TARGET"

        if verbose:
            log.debug(
                f"Frame {i}: [{status}] {frame_data['name']}:{frame_data['line']} "
                f"in {frame_data['function']} (module_level: {frame_data['is_module_level']})"
            )

        # Return the first valid target frame
        if status == "TARGET":
            return frame_data

    log.warning("Could not find the correct chain, returning full stack.")
    return chain

def get_caller(verbose: bool = False) -> dict:
    """Get the calling module/file information"""
    result = get_import_chain(verbose=verbose)

    # If we got a single frame dict, return it
    if isinstance(result, dict):
        return result

    # If we got the full chain, find the first non-skipped frame
    for frame in result:
        if not (frame['is_frozen'] or frame['is_init']):
            return frame

    # Fallback to the last frame if nothing else works
    log.warning("No valid caller found, using last frame")
    return result[-1] if result else {
        'filename': '<unknown>',
        'name': '<unknown>',
        'function': '<unknown>',
        'line': 0
    }

# Test the function
if __name__ == "__main__":
    def test_from_function():
        """Test calling from within a function"""
        log.info("Testing from function:")
        caller = get_caller(verbose=True)
        log.info(f"Caller: {caller['name']}:{caller['line']} in {caller['function']}")

    # Test from module level
    log.info("Testing from module level:")
    module_caller = get_caller(verbose=True)
    log.info(f"Module caller: {module_caller['name']}:{module_caller['line']} in {module_caller['function']}")

    # Test from function
    test_from_function()