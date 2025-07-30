from typing import Callable
from ..utils.matching_socre_basics import (
    get_source_list_to_target_list_matching_score,
)
from ..utils.string import (
    get_string_common_prefix,
    normalize_string,
    IGNORED_CHARS,
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


def get_bert_score_similarity(
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
    Calculate similarity score based on whether one string starts with another.
    Score is normalized between 0 (no common prefix) and 1 (identical).

    Args:
        s1: First string
        s2: Second string
        get_part_weights: Function to get the weight of each part of the string
        get_part_weight: Function to get the weight of a part of the string
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

        get_elem1_weight = get_part_weight
        if get_elem1_weight is None:
            if get_part_weights is not None:
                s1_weight_dict = get_part_weights(s1)
            elif weight_by_length:
                s1_weight_dict = {part: len(part) for part in s1_substrings}
            else:
                s1_weight_dict = {}

            get_elem1_weight = lambda x: s1_weight_dict.get(x, 1)

        get_elem_matching_score = lambda x, y: get_elem_common_prefix_score(
            x, y, common_prefix_min_ratio
        )

        score_a = get_source_list_to_target_list_matching_score(
            source=s1_substrings,
            target=s2_substrings,
            get_elem_matching_score=get_elem_matching_score,
            get_target_elem_weight=get_elem2_weight,
        )
        score_b = get_source_list_to_target_list_matching_score(
            source=s2_substrings,
            target=s1_substrings,
            get_elem_matching_score=get_elem_matching_score,
            get_target_elem_weight=get_elem1_weight,
        )

        return (
            2 * score_a * score_b / (score_a + score_b)
            if score_a + score_b != 0
            else 0.0
        )
