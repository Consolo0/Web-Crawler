
class DebugHTMLSaver:
    def __init__(self, debug_dir, visited_types_lock, debug_lock, sources_and_types_visited):
        self.debug_dir = debug_dir
        self.visited_types_lock = visited_types_lock
        self.debug_lock = debug_lock
        self.sources_and_types_visited = sources_and_types_visited
    
    def _save_debug_html_safe(self, source_id, html, page_type):
        """Thread-safe version of _save_debug_html with lock"""
        # Must use visited_types_lock, not debug_lock (consistent with main loop)
        with self.visited_types_lock:
            with self.debug_lock:  # Separate lock for file I/O
                self._save_debug_html(source_id, html, page_type)
            self.sources_and_types_visited.add((source_id, page_type))
    
    def _save_debug_html(self, source_id, html, page_type):
        filename = f"{source_id}_{page_type}.html"
        filepath = self.debug_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)