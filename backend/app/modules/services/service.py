from app.modules.services.schemas import ServicePublic


def get_public_services() -> list[ServicePublic]:
    return [
        ServicePublic(
            id=1,
            name="Haircut",
            description="Classic men's haircut",
            duration_minutes=30,
            price=25.00,
        ),
        ServicePublic(
            id=2,
            name="Beard Trim",
            description="Beard shaping and trimming",
            duration_minutes=20,
            price=15.00,
        ),
    ]