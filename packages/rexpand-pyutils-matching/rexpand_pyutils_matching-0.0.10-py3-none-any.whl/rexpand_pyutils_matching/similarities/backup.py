from typing import Callable
from rexpand_pyutils_matching.utils.matching_socre_basics import (
    get_source_list_to_target_list_matching_score,
)
from rexpand_pyutils_matching.utils.string import (
    IGNORED_CHARS,
    get_string_common_prefix,
    normalize_string,
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
        s1_substrings = [part.strip() for part in s1.split(separator) if part.strip()]
        if len(s1_substrings) == 0:
            return 0.0

        s2_substrings = [part.strip() for part in s2.split(separator) if part.strip()]
        if len(s2_substrings) == 0:
            return 0.0

        # Initialize s1_weight_dict, s1_total_weight, s2_weight_dict, s2_total_weight
        if get_part_weights is not None:
            s1_weight_dict = get_part_weights(s1)
            s1_total_weight = sum(s1_weight_dict.values())

            s2_weight_dict = get_part_weights(s2)
            s2_total_weight = sum(s2_weight_dict.values())
        elif weight_by_length:
            s1_weight_dict = {}
            s1_total_weight = 0
            for part in s1_substrings:
                length = len(part)
                s1_weight_dict[part] = length
                s1_total_weight += length

            s2_weight_dict = {}
            s2_total_weight = 0
            for part in s2_substrings:
                length = len(part)
                s2_weight_dict[part] = length
                s2_total_weight += length
        else:
            s1_weight_dict = {part: 1 for part in s1_substrings}
            s1_total_weight = len(s1_substrings)

            s2_weight_dict = {part: 1 for part in s2_substrings}
            s2_total_weight = len(s2_substrings)

        score_a = get_source_list_to_target_list_matching_score(
            source=s1_substrings,
            target=s2_substrings,
            get_elem_matching_score=get_elem_common_prefix_score,
            get_target_elem_weight=lambda x: s2_weight_dict.get(normalize_string(x), 1),
        )
        score_b = get_source_list_to_target_list_matching_score(
            source=s2_substrings,
            target=s1_substrings,
            get_elem_matching_score=get_elem_common_prefix_score,
            get_target_elem_weight=lambda x: s1_weight_dict.get(normalize_string(x), 1),
        )

        return score_a, score_b

        # print(score_a, score_b)

        # weighted_partial_score_a = score_a * len(s1) / (len(s1) + len(s2))
        # weighted_partial_score_b = score_b * len(s2) / (len(s2) + len(s1))

        # return weighted_partial_score_a + weighted_partial_score_b
