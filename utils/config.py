"""
Configuration management for the STTM impact analysis tool.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


@dataclass
class MatchingConfig:
    """Configuration for matching algorithms"""
    
    # Fuzzy matching thresholds
    tab_name_threshold: float = 0.8
    field_name_threshold: float = 0.7
    content_matching_threshold: float = 0.6
    
    # Case sensitivity settings
    case_sensitive_tab_matching: bool = False
    case_sensitive_field_matching: bool = False
    
    # Matching algorithms
    use_fuzzy_matching: bool = True
    use_keyword_extraction: bool = True
    use_partial_matching: bool = True


@dataclass
class ImpactScoringConfig:
    """Configuration for impact scoring algorithms"""
    
    # Impact weights for different change types
    deleted_mapping_weight: float = 10.0
    modified_mapping_weight: float = 5.0
    added_mapping_weight: float = 3.0
    
    # Field-specific weights
    sample_data_change_weight: float = 8.0
    canonical_name_change_weight: float = 6.0
    field_name_change_weight: float = 4.0
    
    # Confidence multipliers
    high_confidence_multiplier: float = 1.2
    medium_confidence_multiplier: float = 1.0
    low_confidence_multiplier: float = 0.8
    
    # Impact level thresholds
    high_impact_threshold: float = 8.0
    medium_impact_threshold: float = 4.0


@dataclass
class ParsingConfig:
    """Configuration for file parsing"""
    
    # Excel parsing settings
    skip_empty_rows: bool = True
    trim_whitespace: bool = True
    case_insensitive_columns: bool = True
    
    # ID pattern detection
    min_confidence_for_pattern: float = 0.7
    max_sample_ids_for_analysis: int = 50
    
    # Error handling
    continue_on_parsing_errors: bool = True
    log_parsing_warnings: bool = True


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    
    # Output formats
    generate_json: bool = True
    generate_html: bool = False
    generate_markdown: bool = False
    generate_excel: bool = False
    
    # Report content
    include_executive_summary: bool = True
    include_detailed_analysis: bool = True
    include_new_test_generation: bool = True
    include_gap_analysis: bool = True
    
    # Formatting
    max_description_length: int = 500
    show_confidence_scores: bool = True
    group_by_impact_level: bool = True


@dataclass
class STTMConfig:
    """Main configuration class for the STTM analysis tool"""
    
    matching: MatchingConfig = field(default_factory=MatchingConfig)
    impact_scoring: ImpactScoringConfig = field(default_factory=ImpactScoringConfig)
    parsing: ParsingConfig = field(default_factory=ParsingConfig)
    reporting: ReportConfig = field(default_factory=ReportConfig)
    
    # General settings
    log_level: str = "INFO"
    output_directory: str = "./output"
    temp_directory: str = "./temp"
    
    # Processing options
    parallel_processing: bool = False
    max_workers: int = 4
    
    def save_to_file(self, file_path: str):
        """Save configuration to JSON file"""
        config_dict = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'STTMConfig':
        """Load configuration from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'matching': {
                'tab_name_threshold': self.matching.tab_name_threshold,
                'field_name_threshold': self.matching.field_name_threshold,
                'content_matching_threshold': self.matching.content_matching_threshold,
                'case_sensitive_tab_matching': self.matching.case_sensitive_tab_matching,
                'case_sensitive_field_matching': self.matching.case_sensitive_field_matching,
                'use_fuzzy_matching': self.matching.use_fuzzy_matching,
                'use_keyword_extraction': self.matching.use_keyword_extraction,
                'use_partial_matching': self.matching.use_partial_matching
            },
            'impact_scoring': {
                'deleted_mapping_weight': self.impact_scoring.deleted_mapping_weight,
                'modified_mapping_weight': self.impact_scoring.modified_mapping_weight,
                'added_mapping_weight': self.impact_scoring.added_mapping_weight,
                'sample_data_change_weight': self.impact_scoring.sample_data_change_weight,
                'canonical_name_change_weight': self.impact_scoring.canonical_name_change_weight,
                'field_name_change_weight': self.impact_scoring.field_name_change_weight,
                'high_confidence_multiplier': self.impact_scoring.high_confidence_multiplier,
                'medium_confidence_multiplier': self.impact_scoring.medium_confidence_multiplier,
                'low_confidence_multiplier': self.impact_scoring.low_confidence_multiplier,
                'high_impact_threshold': self.impact_scoring.high_impact_threshold,
                'medium_impact_threshold': self.impact_scoring.medium_impact_threshold
            },
            'parsing': {
                'skip_empty_rows': self.parsing.skip_empty_rows,
                'trim_whitespace': self.parsing.trim_whitespace,
                'case_insensitive_columns': self.parsing.case_insensitive_columns,
                'min_confidence_for_pattern': self.parsing.min_confidence_for_pattern,
                'max_sample_ids_for_analysis': self.parsing.max_sample_ids_for_analysis,
                'continue_on_parsing_errors': self.parsing.continue_on_parsing_errors,
                'log_parsing_warnings': self.parsing.log_parsing_warnings
            },
            'reporting': {
                'generate_json': self.reporting.generate_json,
                'generate_html': self.reporting.generate_html,
                'generate_markdown': self.reporting.generate_markdown,
                'generate_excel': self.reporting.generate_excel,
                'include_executive_summary': self.reporting.include_executive_summary,
                'include_detailed_analysis': self.reporting.include_detailed_analysis,
                'include_new_test_generation': self.reporting.include_new_test_generation,
                'include_gap_analysis': self.reporting.include_gap_analysis,
                'max_description_length': self.reporting.max_description_length,
                'show_confidence_scores': self.reporting.show_confidence_scores,
                'group_by_impact_level': self.reporting.group_by_impact_level
            },
            'log_level': self.log_level,
            'output_directory': self.output_directory,
            'temp_directory': self.temp_directory,
            'parallel_processing': self.parallel_processing,
            'max_workers': self.max_workers
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'STTMConfig':
        """Create configuration from dictionary"""
        
        matching = MatchingConfig(**config_dict.get('matching', {}))
        impact_scoring = ImpactScoringConfig(**config_dict.get('impact_scoring', {}))
        parsing = ParsingConfig(**config_dict.get('parsing', {}))
        reporting = ReportConfig(**config_dict.get('reporting', {}))
        
        return cls(
            matching=matching,
            impact_scoring=impact_scoring,
            parsing=parsing,
            reporting=reporting,
            log_level=config_dict.get('log_level', 'INFO'),
            output_directory=config_dict.get('output_directory', './output'),
            temp_directory=config_dict.get('temp_directory', './temp'),
            parallel_processing=config_dict.get('parallel_processing', False),
            max_workers=config_dict.get('max_workers', 4)
        )


def get_default_config() -> STTMConfig:
    """Get the default configuration"""
    return STTMConfig()


def load_config(config_file: Optional[str] = None) -> STTMConfig:
    """Load configuration from file or return default"""
    
    if config_file and Path(config_file).exists():
        try:
            return STTMConfig.load_from_file(config_file)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration")
    
    return get_default_config()


def save_default_config(output_file: str = "sttm_config.json"):
    """Save default configuration to file for customization"""
    config = get_default_config()
    config.save_to_file(output_file)
    print(f"Default configuration saved to: {output_file}")


# Predefined configuration presets
PRESET_CONFIGS = {
    "strict": STTMConfig(
        matching=MatchingConfig(
            tab_name_threshold=0.9,
            field_name_threshold=0.85,
            content_matching_threshold=0.8,
            case_sensitive_tab_matching=True
        ),
        impact_scoring=ImpactScoringConfig(
            high_impact_threshold=6.0,
            medium_impact_threshold=3.0
        )
    ),
    
    "lenient": STTMConfig(
        matching=MatchingConfig(
            tab_name_threshold=0.6,
            field_name_threshold=0.5,
            content_matching_threshold=0.4
        ),
        impact_scoring=ImpactScoringConfig(
            high_impact_threshold=10.0,
            medium_impact_threshold=6.0
        )
    ),
    
    "balanced": STTMConfig()  # Default is balanced
}


def get_preset_config(preset_name: str) -> STTMConfig:
    """Get a predefined configuration preset"""
    if preset_name in PRESET_CONFIGS:
        return PRESET_CONFIGS[preset_name]
    else:
        available_presets = list(PRESET_CONFIGS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available presets: {available_presets}")