from shop.models import Base
from config import ENGINE


Base.metadata.create_all(ENGINE)
