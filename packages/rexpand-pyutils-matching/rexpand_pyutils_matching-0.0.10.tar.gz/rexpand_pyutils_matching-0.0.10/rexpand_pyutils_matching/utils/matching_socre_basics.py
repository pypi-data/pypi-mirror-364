from typing import Callable


def get_source_list_to_target_list_matching_score(
    source: list[str],
    target: list[str],
    get_elem_matching_score: Callable[[str, str], float],
    get_target_elem_weight: Callable[[str], float],
) -> float:
    """
    Calculate the matching score from `source` to `target`, i.e., how many elements in `target` are matched from `source`.

    Args:
        source: List of elements
        target: List of elements
        get_elem_matching_score: Function to get the matching score from element in `source` to element in `target`
        get_target_elem_weight: Function to get the weight of an element in `target`

    Returns:
        float: Matching score from `source` to `target`
    """
    target_score = 0  # How much `target` is matched from `source`
    calculated_total_weight = 0  # Total weight of `target`
    source_set = set(source)
    for target_elem in target:
        # `target_elem` is fully matched from `source`
        if target_elem in source_set:
            target_elem_score = 1

        # Otherwise, find the best match for `target_elem` from `source`
        else:
            target_elem_score = 0
            for source_elem in source_set:
                target_elem_score = max(
                    target_elem_score,
                    get_elem_matching_score(
                        source_elem,
                        target_elem,
                    ),
                )

        paritial_weight_target_elem = get_target_elem_weight(target_elem)
        calculated_total_weight += paritial_weight_target_elem
        target_score += target_elem_score * paritial_weight_target_elem

    return target_score / (calculated_total_weight or 1)
