import os
import re
import pytest

def test_html_scrollspy_and_creator_structure():
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Scrollspy and separate app workspace verification
    assert 'id="landing-flow"' in html
    assert 'id="hero"' in html
    assert 'id="about"' in html
    assert 'id="creators"' in html
    assert 'id="app-workspace"' in html
    assert 'id="exit-app-btn"' in html

    # 2. Clean call to action (unified hero button and nav link; redundant launch buttons removed)
    assert 'id="big-center-play-btn"' in html
    assert 'id="nav-play-link"' in html
    assert 'id="story-play-btn"' not in html, "Redundant story play button should be removed"
    assert 'id="team-play-btn"' not in html, "Redundant team play button should be removed"

    # 3. Dedicated Creator Section for Akhil Kohli
    creators_match = re.search(r'<section id="creators"[\s\S]*?</section>', html)
    assert creators_match is not None
    creators_html = creators_match.group(0)

    # Must feature Akhil Kohli as Creator & Developer
    assert "Akhil Kohli" in creators_html
    assert "Creator & Developer" in creators_html

    # Check picture spot and bio section
    photo_slots = re.findall(r'class="[^"]*team-photo-container[^"]*"', creators_html)
    assert len(photo_slots) >= 1, "Expected at least 1 photo slot for Akhil"

    photo_badges = re.findall(r'class="photo-spot-badge"', creators_html)
    assert len(photo_badges) >= 1, "Expected photo badge"

    bios = re.findall(r'class="creator-bio"', creators_html)
    assert len(bios) >= 1, "Expected bio description"

    # 4. Guitar wood theme and tuning string elements
    assert 'class="intro-guitar-strings"' in html, "Expected guitar tuning strings in intro splash"
