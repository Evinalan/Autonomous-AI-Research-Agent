
import pytest

from src.comparison.research_comparator import (
    compare_research_topics
)


def test_empty_topic_a():

    with pytest.raises(ValueError):

        compare_research_topics(
            topic_a="",
            topic_b="Deep Learning"
        )


def test_empty_topic_b():

    with pytest.raises(ValueError):

        compare_research_topics(
            topic_a="Machine Learning",
            topic_b=""
        )


def test_same_topics():

    with pytest.raises(ValueError):

        compare_research_topics(
            topic_a="Deep Learning",
            topic_b="Deep Learning"
        )
