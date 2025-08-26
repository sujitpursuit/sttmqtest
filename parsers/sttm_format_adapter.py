"""
STTM Format Adapter - Isolates STTM format changes from the rest of the system.

This adapter pattern ensures that when STTM JSON format changes, only this 
adapter needs to be updated, not the core models or other components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from models.sttm_models import STTMDocument, STTMTab, STTMMapping, ChangeType, TabChangeCategory


@dataclass
class RawMappingData:
    """Raw mapping data extracted from any STTM format - format-agnostic"""
    source_field: str
    target_field: str
    canonical_name: Optional[str] = None
    sample_data: Optional[str] = None
    change_type: Optional[str] = None
    original_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    modified_fields: Optional[List[str]] = None


@dataclass
class RawTabData:
    """Raw tab data extracted from any STTM format - format-agnostic"""
    name: str
    change_type: str
    source_system: Optional[str] = None
    target_system: Optional[str] = None
    added_mappings: List[RawMappingData] = None
    deleted_mappings: List[RawMappingData] = None
    modified_mappings: List[RawMappingData] = None
    unchanged_mappings: List[RawMappingData] = None


class STTMFormatAdapter(ABC):
    """Abstract adapter for different STTM formats"""
    
    @abstractmethod
    def extract_raw_data(self, json_data: Dict[str, Any]) -> List[RawTabData]:
        """Extract format-agnostic raw data from STTM JSON"""
        pass
    
    @abstractmethod
    def get_format_version(self) -> str:
        """Get the format version this adapter handles"""
        pass
    
    @abstractmethod
    def validate_format(self, json_data: Dict[str, Any]) -> bool:
        """Validate if this adapter can handle the given format"""
        pass


class CurrentSTTMFormatAdapter(STTMFormatAdapter):
    """Adapter for the current STTM difference report format"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def get_format_version(self) -> str:
        return "Excel Comparison Tool v2.0"
    
    def validate_format(self, json_data: Dict[str, Any]) -> bool:
        """Validate the current format structure"""
        required_keys = ["report_metadata", "detailed_changes"]
        return all(key in json_data for key in required_keys)
    
    def extract_raw_data(self, json_data: Dict[str, Any]) -> List[RawTabData]:
        """Extract data from current STTM format"""
        
        raw_tabs = []
        
        # Extract changed tabs from current format
        detailed_changes = json_data.get("detailed_changes", {})
        changed_tabs = detailed_changes.get("changed_tabs", [])
        
        for tab_data in changed_tabs:
            raw_tab = self._extract_tab_data(tab_data, is_changed=True)
            raw_tabs.append(raw_tab)
        
        # Extract unchanged tabs if they exist
        unchanged_tabs = detailed_changes.get("unchanged_tabs", [])
        for tab_data in unchanged_tabs:
            raw_tab = self._extract_tab_data(tab_data, is_changed=False)
            raw_tabs.append(raw_tab)
        
        self.logger.debug(f"Extracted {len(raw_tabs)} tabs from current format")
        return raw_tabs
    
    def _extract_tab_data(self, tab_data: Dict[str, Any], is_changed: bool) -> RawTabData:
        """Extract tab data from current format"""
        
        raw_tab = RawTabData(
            name=tab_data.get("tab_name", "Unknown"),
            change_type=tab_data.get("change_type", "unchanged") if is_changed else "unchanged",
            source_system=tab_data.get("source_system"),
            target_system=tab_data.get("target_system")
        )
        
        # Extract mappings if available
        mappings_data = tab_data.get("mappings", {})
        
        # Extract added mappings
        raw_tab.added_mappings = self._extract_mappings(
            mappings_data.get("added_mappings", []), "added"
        )
        
        # Extract deleted mappings  
        raw_tab.deleted_mappings = self._extract_mappings(
            mappings_data.get("deleted_mappings", []), "deleted"
        )
        
        # Extract modified mappings
        raw_tab.modified_mappings = self._extract_modified_mappings(
            mappings_data.get("modified_mappings", [])
        )
        
        return raw_tab
    
    def _extract_mappings(self, mappings_data: List[Dict[str, Any]], 
                         change_type: str) -> List[RawMappingData]:
        """Extract mappings from current format"""
        
        raw_mappings = []
        
        for mapping_data in mappings_data:
            mapping_fields = mapping_data.get("mapping_fields", {})
            
            raw_mapping = RawMappingData(
                source_field=self._get_field_value(mapping_fields, ["Source Field", "source_field"]),
                target_field=self._get_field_value(mapping_fields, ["Target Field", "target_field"]),
                canonical_name=self._get_field_value(mapping_fields, [
                    "Source Canonical Name", "Target Canonical Name", "canonical_name"
                ]),
                sample_data=self._get_field_value(mapping_fields, [
                    "source_sample_data", "target_sample_data", "sample_data"
                ]),
                change_type=change_type
            )
            
            raw_mappings.append(raw_mapping)
        
        return raw_mappings
    
    def _extract_modified_mappings(self, mappings_data: List[Dict[str, Any]]) -> List[RawMappingData]:
        """Extract modified mappings from current format"""
        
        raw_mappings = []
        
        for mapping_data in mappings_data:
            mapping_fields = mapping_data.get("mapping_fields", {})
            field_changes = mapping_data.get("field_changes", {})
            
            raw_mapping = RawMappingData(
                source_field=self._get_field_value(mapping_fields, ["Source Field", "source_field"]),
                target_field=self._get_field_value(mapping_fields, ["Target Field", "target_field"]),
                canonical_name=self._get_field_value(mapping_fields, [
                    "Source Canonical Name", "Target Canonical Name", "canonical_name"
                ]),
                change_type="modified",
                modified_fields=list(field_changes.keys()),
                original_values={},
                new_values={}
            )
            
            # Extract change details
            for field, change_detail in field_changes.items():
                if isinstance(change_detail, dict):
                    raw_mapping.original_values[field] = change_detail.get("old_value")
                    raw_mapping.new_values[field] = change_detail.get("new_value")
                else:
                    raw_mapping.new_values[field] = change_detail
            
            # Set sample data from changes if available
            if "source_sample_data" in field_changes:
                sample_change = field_changes["source_sample_data"]
                if isinstance(sample_change, dict):
                    raw_mapping.sample_data = sample_change.get("new_value")
            
            raw_mappings.append(raw_mapping)
        
        return raw_mappings
    
    def _get_field_value(self, data: Dict[str, Any], possible_keys: List[str]) -> str:
        """Get field value trying multiple possible key names"""
        for key in possible_keys:
            if key in data and data[key]:
                return str(data[key])
        return ""


class LegacySTTMFormatAdapter(STTMFormatAdapter):
    """Adapter for potential legacy STTM format (example for extensibility)"""
    
    def get_format_version(self) -> str:
        return "Legacy STTM v1.0"
    
    def validate_format(self, json_data: Dict[str, Any]) -> bool:
        """Validate legacy format - example structure"""
        return "changed_tabs" in json_data and "unchanged_tabs" in json_data
    
    def extract_raw_data(self, json_data: Dict[str, Any]) -> List[RawTabData]:
        """Extract data from legacy format - example implementation"""
        # This would be implemented when we encounter legacy format
        raw_tabs = []
        
        # Example: Legacy format might have different structure
        changed_tabs = json_data.get("changed_tabs", {})
        for tab_name, tab_data in changed_tabs.items():
            raw_tab = RawTabData(
                name=tab_name,
                change_type=tab_data.get("type", "unknown")
            )
            # ... extract mappings based on legacy structure
            raw_tabs.append(raw_tab)
        
        return raw_tabs


class STTMFormatAdapterFactory:
    """Factory to create the appropriate format adapter"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._adapters = [
            CurrentSTTMFormatAdapter(logger),
            LegacySTTMFormatAdapter(),
            # Add more adapters here as new formats are encountered
        ]
    
    def get_adapter(self, json_data: Dict[str, Any]) -> STTMFormatAdapter:
        """Get the appropriate adapter for the given JSON data"""
        
        for adapter in self._adapters:
            if adapter.validate_format(json_data):
                self.logger.info(f"Using adapter for format: {adapter.get_format_version()}")
                return adapter
        
        # Default to current format adapter
        self.logger.warning("No specific adapter found, using current format adapter")
        return self._adapters[0]
    
    def register_adapter(self, adapter: STTMFormatAdapter):
        """Register a new format adapter"""
        self._adapters.insert(0, adapter)  # Insert at beginning for priority


class STTMDataConverter:
    """Converts format-agnostic raw data to domain models"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def convert_to_document(self, raw_tabs: List[RawTabData]) -> STTMDocument:
        """Convert raw tab data to STTMDocument"""
        
        document = STTMDocument()
        
        for raw_tab in raw_tabs:
            tab = self._convert_to_tab(raw_tab)
            
            if raw_tab.change_type == "unchanged":
                document.unchanged_tabs.append(tab)
            else:
                document.changed_tabs.append(tab)
        
        self._update_document_stats(document)
        return document
    
    def _convert_to_tab(self, raw_tab: RawTabData) -> STTMTab:
        """Convert raw tab data to STTMTab"""
        
        # Map change type
        change_category_map = {
            "mixed": TabChangeCategory.MIXED,
            "modifications_only": TabChangeCategory.MODIFICATIONS_ONLY,
            "additions_only": TabChangeCategory.ADDITIONS_ONLY,
            "deletions_only": TabChangeCategory.DELETIONS_ONLY,
            "unchanged": TabChangeCategory.UNCHANGED
        }
        
        change_category = change_category_map.get(raw_tab.change_type, TabChangeCategory.UNCHANGED)
        
        tab = STTMTab(name=raw_tab.name, change_category=change_category)
        
        # Convert mappings
        if raw_tab.added_mappings:
            tab.added_mappings = [self._convert_to_mapping(rm, ChangeType.ADDED) 
                                 for rm in raw_tab.added_mappings]
        
        if raw_tab.deleted_mappings:
            tab.deleted_mappings = [self._convert_to_mapping(rm, ChangeType.DELETED) 
                                   for rm in raw_tab.deleted_mappings]
        
        if raw_tab.modified_mappings:
            tab.modified_mappings = [self._convert_to_modified_mapping(rm) 
                                    for rm in raw_tab.modified_mappings]
        
        # Combine all mappings
        tab.all_mappings = (
            tab.added_mappings + tab.deleted_mappings + 
            tab.modified_mappings + tab.unchanged_mappings
        )
        
        return tab
    
    def _convert_to_mapping(self, raw_mapping: RawMappingData, 
                           change_type: ChangeType) -> STTMMapping:
        """Convert raw mapping to STTMMapping"""
        
        return STTMMapping(
            source_field=raw_mapping.source_field,
            target_field=raw_mapping.target_field,
            canonical_name=raw_mapping.canonical_name,
            sample_data=raw_mapping.sample_data,
            change_type=change_type
        )
    
    def _convert_to_modified_mapping(self, raw_mapping: RawMappingData) -> STTMMapping:
        """Convert raw modified mapping to STTMMapping"""
        
        mapping = STTMMapping(
            source_field=raw_mapping.source_field,
            target_field=raw_mapping.target_field,
            canonical_name=raw_mapping.canonical_name,
            sample_data=raw_mapping.sample_data,
            change_type=ChangeType.MODIFIED
        )
        
        if raw_mapping.modified_fields:
            mapping.modified_fields = raw_mapping.modified_fields
        if raw_mapping.original_values:
            mapping.original_values = raw_mapping.original_values
        if raw_mapping.new_values:
            mapping.new_values = raw_mapping.new_values
        
        return mapping
    
    def _update_document_stats(self, document: STTMDocument):
        """Update document-level statistics"""
        all_tabs = document.get_all_tabs()
        
        document.total_tabs = len(all_tabs)
        document.total_mappings = sum(len(tab.all_mappings) for tab in all_tabs)
        document.total_changes = sum(tab.get_total_changes() for tab in document.changed_tabs)