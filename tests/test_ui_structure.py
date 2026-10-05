import os
import re
import pytest

def test_html_scrollspy_and_team_cards():
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

    # 2. Play buttons that bring user to the actual app
    assert 'id="big-center-play-btn"' in html
    assert 'id="story-play-btn"' in html
    assert 'id="team-play-btn"' in html
    assert 'id="nav-play-link"' in html

    # 3. Only 4 cards in creators section
    creators_match = re.search(r'<section id="creators"[\s\S]*?</section>', html)
    assert creators_match is not None
    creators_html = creators_match.group(0)

    card_matches = re.findall(r'<div class="creator-card">', creators_html)
    assert len(card_matches) == 4, f"Expected exactly 4 cards, found {len(card_matches)}"

    # 4. Each required position and person
    expected_members = [
        ("Julian Vance", "Founding Engineer"),
        ("Elena Rostova", "Founding Designer"),
        ("Marcus Chen", "Operations & Strategy"),
        ("Maya Patel", "Community Outreach")
    ]

    for name, pos in expected_members:
        assert name in creators_html, f"Missing member: {name}"
        assert pos in creators_html, f"Missing position: {pos}"

    # 5. Check picture spot and story description on all cards
    photo_slots = re.findall(r'class="team-photo-container"', creators_html)
    assert len(photo_slots) == 4, f"Expected 4 photo slots, found {len(photo_slots)}"

    photo_badges = re.findall(r'class="photo-spot-badge"', creators_html)
    assert len(photo_badges) == 4, f"Expected 4 photo badges, found {len(photo_badges)}"

    bios = re.findall(r'class="creator-bio"', creators_html)
    assert len(bios) == 4, f"Expected 4 bios, found {len(bios)}"
