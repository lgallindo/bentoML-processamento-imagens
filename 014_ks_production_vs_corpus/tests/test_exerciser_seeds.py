from scripts.download_exerciser_samples import SEED_PREFIX, image_url
from scripts.download_samples import SEED_PREFIX as TRAIN_SEED_PREFIX


def test_exerciser_seed_prefix_differs_from_training() -> None:
    assert SEED_PREFIX == "bentoml-exer"
    assert TRAIN_SEED_PREFIX == "bentoml-edu"
    assert SEED_PREFIX != TRAIN_SEED_PREFIX
    assert "bentoml-exer-1" in image_url(1)
    assert "bentoml-edu" not in image_url(1)
