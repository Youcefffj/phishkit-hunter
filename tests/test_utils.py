from pkhunter.utils import (
    clean_url_list,
    iter_targets,
    safe_filename,
    strip_trailing_file,
)


def test_iter_targets_without_walk():
    assert list(iter_targets("https://a.tld/x/", walk_parents=False)) == [
        "https://a.tld/x/"
    ]


def test_iter_targets_walks_up_to_host_root():
    result = list(iter_targets("https://a.tld/x/y/", walk_parents=True))
    assert result == [
        "https://a.tld/x/y/",
        "https://a.tld/x/",
        "https://a.tld/",
    ]


def test_iter_targets_stops_at_host_root():
    # Never loops forever, even on the bare host root.
    result = list(iter_targets("https://a.tld/", walk_parents=True))
    assert result == ["https://a.tld/"]


def test_safe_filename_removes_path_separators():
    name = safe_filename("https://a.tld/dir/FULLZ.html")
    assert "/" not in name and ":" not in name


def test_strip_trailing_file():
    assert strip_trailing_file("https://a.tld/dir/index.html") == "https://a.tld/dir/"
    assert strip_trailing_file("https://a.tld/dir") == "https://a.tld/dir/"


def test_clean_url_list_dedups_and_drops_parents():
    urls = [
        "https://a.tld/dir/page.html",
        "https://a.tld/dir/page.html",  # duplicate
        "https://a.tld/dir/deep/x.php",
    ]
    cleaned = clean_url_list(urls)
    # The shallow "/dir/" is a prefix of "/dir/deep/", so only the deep one stays.
    assert cleaned == ["https://a.tld/dir/deep/"]
