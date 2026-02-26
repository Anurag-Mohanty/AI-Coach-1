
import time
import functools
import asyncio
from typing import Dict, Optional
import streamlit as st
from contextlib import contextmanager
from datetime import datetime

class TimingStats:
    _stats = {}
    
    @classmethod
    def record(cls, category: str, duration: float, function_name: str):
        if category not in cls._stats:
            cls._stats[category] = []
        cls._stats[category].append({
            'function': function_name,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    @classmethod
    def get_stats(cls, category: Optional[str] = None) -> Dict:
        if category:
            return cls._stats.get(category, [])
        return cls._stats

@contextmanager
def track_time(category: str, display: bool = True):
    """Context manager to track execution time of a code block"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        TimingStats.record(category, duration, '')
        if display:
            try:
                import streamlit as st
                if st.runtime.exists():
                    st.write(f"⏱️ {category}: {duration:.2f}s")
                else:
                    print(f"⏱️ {category}: {duration:.2f}s")
            except:
                print(f"⏱️ {category}: {duration:.2f}s")

def timed_function(category: str, display: bool = True):
    """Decorator to track execution time of a function"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                TimingStats.record(category, duration, func.__name__)
                if display:
                    try:
                        import streamlit as st
                        if st.runtime.exists():
                            st.write(f"⏱️ {category} - {func.__name__}: {duration:.2f}s")
                        else:
                            print(f"⏱️ {category} - {func.__name__}: {duration:.2f}s")
                    except:
                        print(f"⏱️ {category} - {func.__name__}: {duration:.2f}s")
        return wrapper
    return decorator
