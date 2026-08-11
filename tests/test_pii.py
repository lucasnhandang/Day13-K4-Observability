from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD: 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    out = scrub_text("Card: 1234-5678-9012-3456")
    assert "1234-5678-9012-3456" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport() -> None:
    out = scrub_text("Passport: B1234567")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT_VN" in out


def test_scrub_event_recursive() -> None:
    from app.logging_config import scrub_event

    event_dict = {
        "event": "user_action",
        "payload": {
            "email": "test@domain.com",
            "info": ["Call 0901234567", {"nested_cccd": "123456789012"}],
        },
    }
    result = scrub_event(None, "info", event_dict)
    assert "test@domain.com" not in str(result)
    assert "0901234567" not in str(result)
    assert "123456789012" not in str(result)
    assert "REDACTED_EMAIL" in result["payload"]["email"]
    assert "REDACTED_PHONE_VN" in result["payload"]["info"][0]
    assert "REDACTED_CCCD" in result["payload"]["info"][1]["nested_cccd"]

