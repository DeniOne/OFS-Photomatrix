from app.db.base import Base  # noqa

# Импортируем все модели, чтобы Alembic мог их увидеть
from app.models.user import User  # noqa
from app.models.organization import Organization  # noqa
from app.models.division import Division  # noqa
from app.models.section import Section  # noqa
from app.models.position import Position  # noqa
from app.models.staff import Staff  # noqa
from app.models.staff_position import StaffPosition  # noqa
from app.models.staff_organization import StaffOrganization  # noqa
from app.models.function import Function  # noqa
from app.models.functional_assignment import FunctionalAssignment  # noqa
from app.models.functional_relation import FunctionalRelation  # noqa 