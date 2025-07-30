from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from PySide6.QtCore import QRect, QPoint
from PySide6.QtWidgets import QWidget, QTabWidget, QSplitter


@dataclass
class CachedDropTarget:
    """Cached information about a potential drop target.
    Note: global_rect is calculated dynamically to avoid stale coordinates.
    """
    widget: QWidget
    target_type: str
    parent_container: Optional[QWidget] = None
    tab_index: int = -1
    z_order: int = 0
    
    @property
    def global_rect(self) -> QRect:
        """
        Dynamically calculates the global rectangle to avoid stale coordinates.
        The method of calculation depends on whether the widget is docked or floating.
        """
        if self.parent_container and hasattr(self.widget, 'content_container'):
            visible_part = self.widget.content_container
        else:
            visible_part = self.widget

        if not visible_part or not visible_part.isVisible():
            return QRect()

        try:
            if hasattr(visible_part, 'isValid') and callable(getattr(visible_part, 'isValid')):
                if not visible_part.isValid():
                    return QRect()

            global_pos = visible_part.mapToGlobal(QPoint(0, 0))
            size = visible_part.size()
            if (global_pos.x() < -50000 or global_pos.y() < -50000 or
                global_pos.x() > 50000 or global_pos.y() > 50000 or
                size.width() <= 0 or size.height() <= 0):
                return QRect()

            return QRect(global_pos, size)
        except:
            return QRect()


@dataclass
class CachedTabBarInfo:
    """Cached information about tab bars for fast hit-testing.
    Note: tab_bar_rect is calculated dynamically to avoid stale coordinates.
    """
    tab_widget: QTabWidget
    container: QWidget
    
    @property
    def tab_bar_rect(self) -> QRect:
        """
        Dynamically calculates the tab bar rectangle to avoid stale coordinates.
        """
        if not self.tab_widget or not self.tab_widget.isVisible():
            return QRect()
        tab_bar = self.tab_widget.tabBar()
        if not tab_bar or not tab_bar.isVisible():
            return QRect()
        try:
            if hasattr(tab_bar, 'isValid') and callable(getattr(tab_bar, 'isValid')):
                if not tab_bar.isValid():
                    return QRect()
            
            global_pos = tab_bar.mapToGlobal(QPoint(0, 0))
            size = tab_bar.size()
            if (global_pos.x() < -50000 or global_pos.y() < -50000 or 
                global_pos.x() > 50000 or global_pos.y() > 50000 or
                size.width() <= 0 or size.height() <= 0):
                return QRect()
                
            return QRect(global_pos, size)
        except:
            return QRect()


class HitTestCache:
    """High-performance caching system for drag operation hit-testing.
    
    Dramatically reduces CPU usage during drag operations by caching
    widget geometries and drop target information.
    """
    
    def __init__(self):
        self._drop_targets: List[CachedDropTarget] = []
        self._tab_bars: List[CachedTabBarInfo] = []
        self._window_rects: Dict[QWidget, QRect] = {}
        self._cache_valid = False
        self._last_mouse_pos: Optional[QPoint] = None
        self._last_hit_result: Optional[Tuple[QWidget, str]] = None
        self._in_drag_operation = False
        
    def invalidate(self):
        """
        Invalidates the cache, forcing a rebuild on next hit test.
        Call this when the layout changes.
        """
        self._cache_valid = False
        self._drop_targets.clear()
        self._tab_bars.clear()
        self._window_rects.clear()
        self._last_mouse_pos = None
        self._last_hit_result = None
        self._in_drag_operation = False
        
    def build_cache(self, window_stack: List[QWidget], dock_containers: List[QWidget]):
        """
        Builds the cache by analyzing all visible windows and containers.
        
        Args:
            window_stack: List of top-level windows (in stacking order, last = topmost)
            dock_containers: List of dock container widgets
        """
        if self._cache_valid:
            return
            
        self._drop_targets.clear()
        self._tab_bars.clear()
        self._window_rects.clear()
        
        for z_index, window in enumerate(window_stack):
            if window and window.isVisible():
                global_pos = window.mapToGlobal(QPoint(0, 0))
                global_rect = QRect(global_pos, window.size())
                
                if (global_pos.x() < -50000 or global_pos.y() < -50000 or 
                    global_pos.x() > 50000 or global_pos.y() > 50000 or
                    window.size().width() <= 0 or window.size().height() <= 0):
                    continue
                    
                self._window_rects[window] = (global_rect, z_index)
        
        for container in dock_containers:
            if container and container.isVisible():
                container_z_order = 0
                for window, (rect, z_index) in self._window_rects.items():
                    if window is container or (hasattr(window, 'dock_area') and window.dock_area is container):
                        container_z_order = z_index
                        break
                self._cache_container_targets(container, container_z_order)
        
        for z_index, window in enumerate(window_stack):
            if window and window.isVisible():
                from ..widgets.dock_panel import DockPanel
                if isinstance(window, DockPanel) and not window.parent_container:
                    self._drop_targets.append(CachedDropTarget(
                        widget=window,
                        target_type='widget',
                        z_order=z_index
                    ))
                
        self._cache_valid = True
        
    def _cache_container_targets(self, container, z_order=0):
        if container and container.isVisible():
            self._drop_targets.append(CachedDropTarget(
                widget=container,
                target_type='container',
                z_order=z_order
            ))
        
        if hasattr(container, 'splitter') and container.splitter:
            self._cache_traversal_targets(container, container.splitter, z_order)
                
    def _cache_traversal_targets(self, container, current_widget, z_order=0):
        if not current_widget or not current_widget.isVisible():
            return

        if isinstance(current_widget, QTabWidget):
            current_tab_content = current_widget.currentWidget()
            if current_tab_content:
                dockable_widget = current_tab_content.property("dockable_widget")
                if dockable_widget:
                    self._drop_targets.append(CachedDropTarget(
                        widget=dockable_widget,
                        target_type='widget',
                        parent_container=container,
                        z_order=z_order
                    ))

            tab_bar = current_widget.tabBar()
            if tab_bar and tab_bar.isVisible():
                immediate_parent_container = current_widget.parentWidget()
                if immediate_parent_container:
                    self._tab_bars.append(CachedTabBarInfo(
                        tab_widget=current_widget,
                        container=immediate_parent_container
                    ))

        elif isinstance(current_widget, QSplitter):
            for i in range(current_widget.count()):
                child_widget = current_widget.widget(i)
                self._cache_traversal_targets(container, child_widget, z_order)
                
                        
    def find_window_at_position(self, global_pos: QPoint, excluded_widget=None) -> Optional[QWidget]:
        """
        Fast lookup of top-level window at position using cached rectangles.
        Respects z-order by checking windows from top to bottom.
        """
        candidates = []
        for window, (rect, z_index) in self._window_rects.items():
            if window is excluded_widget or not window.isVisible():
                continue
            if rect.contains(global_pos):
                candidates.append((window, z_index))
        
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
        return None
        
    def find_drop_target_at_position(self, global_pos: QPoint, excluded_widget=None) -> Optional[CachedDropTarget]:
        """
        Fast lookup of drop target at position using cached data.
        Returns the target with highest z-order, then most specific (smallest area).
        Excludes the specified widget to prevent self-docking.
        """
        if (self._last_mouse_pos and self._last_hit_result and 
            self._positions_close(global_pos, self._last_mouse_pos)):
            widget, target_type = self._last_hit_result
            if excluded_widget and widget is excluded_widget:
                pass
            else:
                for target in self._drop_targets:
                    if target.widget is widget and target.target_type == target_type:
                        return target
                    
        matching_targets = []
        for target in self._drop_targets:
            if target.global_rect.contains(global_pos):
                if excluded_widget and target.widget is excluded_widget:
                    continue
                matching_targets.append(target)
                
        if matching_targets:
            def target_priority(t):
                type_priority = {'widget': 2, 'tab_widget': 1, 'container': 0}[t.target_type]
                return (type_priority, t.z_order, -t.global_rect.width() * t.global_rect.height())
            
            best_target = max(matching_targets, key=target_priority)
            
            self._last_mouse_pos = global_pos
            self._last_hit_result = (best_target.widget, best_target.target_type)
            
            return best_target
            
        return None
        
    def find_tab_bar_at_position(self, global_pos: QPoint) -> Optional[CachedTabBarInfo]:
        """
        Fast lookup of tab bar at position for tab insertion operations.
        """
        for tab_bar_info in self._tab_bars:
            if tab_bar_info.tab_bar_rect.contains(global_pos):
                return tab_bar_info
        return None
        
    def _positions_close(self, pos1: QPoint, pos2: QPoint, threshold: int = 3) -> bool:
        """
        Checks if two positions are close enough to reuse cached results.
        """
        dx = abs(pos1.x() - pos2.x())
        dy = abs(pos1.y() - pos2.y())
        return dx <= threshold and dy <= threshold
        
    def is_cache_valid(self) -> bool:
        """
        Returns whether the cache is currently valid.
        """
        return self._cache_valid
        
    def set_drag_operation_state(self, in_drag: bool):
        self._in_drag_operation = in_drag
        if not in_drag:
            self._last_mouse_pos = None
            self._last_hit_result = None
            
    def update_window_coordinates(self, window: QWidget) -> bool:
        if not self._cache_valid or not window:
            return False
            
        if not self._in_drag_operation:
            return False
            
        if window in self._window_rects:
            old_rect, z_index = self._window_rects[window]
            
            try:
                global_pos = window.mapToGlobal(QPoint(0, 0))
                new_rect = QRect(global_pos, window.size())
                
                if (global_pos.x() < -50000 or global_pos.y() < -50000 or 
                    global_pos.x() > 50000 or global_pos.y() > 50000 or
                    window.size().width() <= 0 or window.size().height() <= 0):
                    return False
                    
                self._window_rects[window] = (new_rect, z_index)
                
                if old_rect != new_rect:
                    self._last_mouse_pos = None
                    self._last_hit_result = None
                    
                return True
            except:
                return False
                
        return False