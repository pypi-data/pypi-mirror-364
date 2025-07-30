from typing import Callable
from ..utils.matching_socre_basics import (
    get_source_list_to_target_list_matching_score,
)
from ..utils.string import (
    IGNORED_CHARS,
    get_string_common_prefix,
    normalize_string,
    split_string,
)


def get_elem_common_prefix_score(
    a: str,
    b: str,
    common_prefix_min_ratio: float = 0.8,
) -> float:
    common_prefix_len = get_string_common_prefix(a, b)
    if (common_prefix_len / min(len(a), len(b))) >= common_prefix_min_ratio:
        return 2 * common_prefix_len / (len(a) + len(b))
    return 0


def get_directional_similarity(
    s1: str,
    s2: str,
    get_part_weights: Callable[[str], dict[str, float]] | None = None,
    get_part_weight: Callable[[str], float] | None = None,
    weight_by_length: bool = True,
    normalize: bool = True,
    ignored_chars: list[str] | None = IGNORED_CHARS,
    separator: str = " ",
    common_prefix_min_ratio: float = 0.8,
) -> float:
    """
    Calculate directional similarity score from one string to another.
    Score is normalized between 0 (no common prefix) and 1 (identical).

    Args:
        s1: First string (the source string to match from)
        s2: Second string (the target string to match to)
        get_part_weights: Function to get the weight of each part of the string (normalized if `normalize` is True)
        get_part_weight: Function to get the weight of a part of the string (normalized if `normalize` is True)
        weight_by_length: Whether to weight the parts by their length
        normalize: Whether to normalize the strings before comparison
        ignored_chars: Characters to ignore when normalizing strings
        separator: Separator to split the strings into parts
        common_prefix_min_ratio: Minimum ratio of common prefix to consider a match

    Returns:
        float: Similarity score between 0 and 1
    """
    if normalize:
        s1 = normalize_string(s1, ignored_chars)
        s2 = normalize_string(s2, ignored_chars)

    if s1 == s2:
        return 1
    else:
        s1_substrings = split_string(s1, separator)
        if len(s1_substrings) == 0:
            return 0.0

        s2_substrings = split_string(s2, separator)
        if len(s2_substrings) == 0:
            return 0.0

        get_elem2_weight = get_part_weight
        if get_elem2_weight is None:
            if get_part_weights is not None:
                s2_weight_dict = get_part_weights(s2)
            elif weight_by_length:
                s2_weight_dict = {part: len(part) for part in s2_substrings}
            else:
                s2_weight_dict = {}

            get_elem2_weight = lambda x: s2_weight_dict.get(x, 1)

        return get_source_list_to_target_list_matching_score(
            source=s1_substrings,
            target=s2_substrings,
            get_elem_matching_score=lambda x, y: get_elem_common_prefix_score(
                x, y, common_prefix_min_ratio
            ),
            get_target_elem_weight=get_elem2_weight,
        )
