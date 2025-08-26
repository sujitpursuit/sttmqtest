"""
STTM (Source-to-Target Mapping) data models for representing parsed STTM difference data.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ChangeType(Enum):
    """Types of changes in STTM mappings"""
    ADDED = "added"
    DELETED = "deleted" 
    MODIFIED = "modified"


class TabChangeCategory(Enum):
    """Categories of changes at tab level"""
    MIXED = "mixed"
    MODIFICATIONS_ONLY = "modifications_only"
    ADDITIONS_ONLY = "additions_only"
    DELETIONS_ONLY = "deletions_only"
    UNCHANGED = "unchanged"


@dataclass
class STTMMapping:
    """Represents a single source-to-target mapping"""
    source_field: str
    target_field: str
    canonical_name: Optional[str] = None
    sample_data: Optional[str] = None
    change_type: Optional[ChangeType] = None
    
    # Additional metadata for modified mappings
    modified_fields: List[str] = field(default_factory=list)
    original_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.source_field} -> {self.target_field}"


@dataclass 
class STTMTab:
    """Represents a tab in the STTM document with its mappings and changes"""
    name: str
    change_category: TabChangeCategory
    
    # All mappings in the tab
    all_mappings: List[STTMMapping] = field(default_factory=list)
    
    # Categorized mappings by change type
    added_mappings: List[STTMMapping] = field(default_factory=list)
    deleted_mappings: List[STTMMapping] = field(default_factory=list)
    modified_mappings: List[STTMMapping] = field(default_factory=list)
    unchanged_mappings: List[STTMMapping] = field(default_factory=list)
    
    def get_total_changes(self) -> int:
        """Get total number of changes in this tab"""
        return len(self.added_mappings) + len(self.deleted_mappings) + len(self.modified_mappings)
    
    def has_changes(self) -> bool:
        """Check if this tab has any changes"""
        return self.get_total_changes() > 0
    
    def get_change_summary(self) -> str:
        """Get a summary of changes in this tab"""
        changes = []
        if self.added_mappings:
            changes.append(f"{len(self.added_mappings)} added")
        if self.deleted_mappings:
            changes.append(f"{len(self.deleted_mappings)} deleted")
        if self.modified_mappings:
            changes.append(f"{len(self.modified_mappings)} modified")
        
        return ", ".join(changes) if changes else "no changes"


@dataclass
class STTMDocument:
    """Represents the complete STTM difference document"""
    
    # Tabs categorized by change status
    changed_tabs: List[STTMTab] = field(default_factory=list)
    unchanged_tabs: List[STTMTab] = field(default_factory=list)
    
    # Metadata
    total_tabs: int = 0
    total_mappings: int = 0
    total_changes: int = 0
    
    def get_all_tabs(self) -> List[STTMTab]:
        """Get all tabs (changed and unchanged)"""
        return self.changed_tabs + self.unchanged_tabs
    
    def get_tab_by_name(self, tab_name: str) -> Optional[STTMTab]:
        """Find a tab by name (case-insensitive)"""
        for tab in self.get_all_tabs():
            if tab.name.lower() == tab_name.lower():
                return tab
        return None
    
    def get_tabs_with_changes(self) -> List[STTMTab]:
        """Get only tabs that have changes"""
        return [tab for tab in self.changed_tabs if tab.has_changes()]
    
    def get_all_changed_mappings(self) -> List[STTMMapping]:
        """Get all mappings that have changes across all tabs"""
        changed_mappings = []
        for tab in self.changed_tabs:
            changed_mappings.extend(tab.added_mappings)
            changed_mappings.extend(tab.deleted_mappings)
            changed_mappings.extend(tab.modified_mappings)
        return changed_mappings
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the STTM document"""
        return {
            "total_tabs": len(self.get_all_tabs()),
            "changed_tabs": len(self.changed_tabs),
            "unchanged_tabs": len(self.unchanged_tabs),
            "total_changes": sum(tab.get_total_changes() for tab in self.changed_tabs),
            "tabs_by_change_type": {
                "additions_only": len([t for t in self.changed_tabs if t.change_category == TabChangeCategory.ADDITIONS_ONLY]),
                "deletions_only": len([t for t in self.changed_tabs if t.change_category == TabChangeCategory.DELETIONS_ONLY]),
                "modifications_only": len([t for t in self.changed_tabs if t.change_category == TabChangeCategory.MODIFICATIONS_ONLY]),
                "mixed": len([t for t in self.changed_tabs if t.change_category == TabChangeCategory.MIXED])
            }
        }