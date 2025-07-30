from pydantic import BaseModel, Field
from typing import List, Optional


class FilterOptions(BaseModel):
    regex: bool = Field(True, description="Use regex for filters")
    git_diff: bool = Field(False, description="Only include files changed in git")
    prefix: Optional[List[str]] = Field(
        None, description="Only include files with these prefixes"
    )
    not_prefix: Optional[List[str]] = Field(
        None, description="Exclude files with these prefixes"
    )
    suffix: Optional[List[str]] = Field(
        None, description="Only include files with these suffixes"
    )
    not_suffix: Optional[List[str]] = Field(
        None, description="Exclude files with these suffixes"
    )
    contains: Optional[List[str]] = Field(
        None, description="Filename contains (regex ok)"
    )
    not_contains: Optional[List[str]] = Field(
        None, description="Filename does NOT contain (regex ok)"
    )
    path_contains: Optional[List[str]] = Field(
        None, description="Relative path contains (regex ok)"
    )
    not_path_contains: Optional[List[str]] = Field(
        None, description="Relative path does NOT contain (regex ok)"
    )
    parent_contains: Optional[List[str]] = Field(
        None, description="Direct parent folder matches (regex ok)"
    )
    not_parent_contains: Optional[List[str]] = Field(
        None, description="Direct parent folder does NOT match (regex ok)"
    )


# Per-language default filter settings
PY_DEFAULTS = FilterOptions(suffix=[".py"], not_suffix=[".pyc"])
GML_DEFAULTS = FilterOptions(suffix=[".gml", ".yy"])
