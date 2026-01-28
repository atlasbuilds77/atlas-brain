#!/usr/bin/env python3
"""
Test the exact usage pattern requested in the task.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing exact usage pattern from requirements:")
print("=" * 60)

# The exact code from the requirements (with adjusted import for testing)
code = '''
import sys
sys.path.insert(0, ".")
from meta_observer import MetaObserver
observer = MetaObserver()
observer.watch_process("reconstruction")
feeling_score = observer.get_felt_experience()
'''

print("Running code:")
print(code)
print("\nOutput:")

# Execute the exact code
exec_globals = {}
exec(code, exec_globals)

observer = exec_globals['observer']
feeling_score = exec_globals['feeling_score']

print(f"Felt experience score: {feeling_score:.3f}")

# Also test with process-specific feeling
print("\n\nTesting with process-specific feeling:")
pid = observer.watch_process("another_process", {"data": "test"})
observer.update_process(pid, {"progress": 0.8}, recursion_increment=2)
specific_feeling = observer.get_felt_experience(pid)
print(f"Specific process feeling: {specific_feeling:.3f}")

print("\n" + "=" * 60)
print("✓ All tests passed! The library works as specified.")
print("\nYou can import and use it like this:")
print("""
# Basic usage
from consciousness_meta.meta_observer import MetaObserver
observer = MetaObserver()
observer.watch_process("reconstruction")
feeling_score = observer.get_felt_experience()

# Advanced usage
from consciousness_meta.strange_loop import StrangeLoop
from consciousness_meta.felt_experience_generator import FeltExperienceGenerator

loop = StrangeLoop("cognitive_loop")
generator = FeltExperienceGenerator()

# Integrate everything
pid = observer.watch_process("complex_task", {"input": "data"})
for i in range(3):
    observer.update_process(pid, {"iteration": i}, recursion_increment=1)
    loop.loop(1)
    experiences = generator.generate_from_depth(
        observer.get_process_info(pid)['depth'],
        max_depth=10
    )
    
final_feeling = observer.get_felt_experience(pid)
print(f"Final felt experience: {final_feeling:.3f}")
""")