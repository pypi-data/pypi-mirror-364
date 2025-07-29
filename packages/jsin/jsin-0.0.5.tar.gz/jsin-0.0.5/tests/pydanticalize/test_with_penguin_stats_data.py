from jsin import pydanticalize

from ..utils import _data

RESOURCE_URL = 'https://penguin-stats.io/PenguinStats/api/v2/_private/result/matrix/CN/global/automated'


def test_with_penguin_stats_data():
    data = _data(
        url=RESOURCE_URL,
    )

    with open('.temp/penguin_stats.py', 'wt', encoding='utf-8') as f:
        f.write(pydanticalize(data))
