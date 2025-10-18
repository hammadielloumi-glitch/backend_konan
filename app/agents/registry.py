
from .domains.constitution import ConstitutionAgent
from .domains.famille import FamilleAgent
from .domains.fiscalite import FiscaliteAgent
from .domains.travail import TravailAgent
from .domains.penal import PenalAgent
from .domains.commercial import CommercialAgent
from .domains.civil import CivilAgent
from .domains.administratif import AdministratifAgent
from .domains.immobilier import ImmobilierAgent
REGISTRY = {
    "constitution": ConstitutionAgent(),
    "famille": FamilleAgent(),
    "fiscalite": FiscaliteAgent(),
    "travail": TravailAgent(),
    "penal": PenalAgent(),
    "commercial": CommercialAgent(),
    "civil": CivilAgent(),
    "administratif": AdministratifAgent(),
    "immobilier": ImmobilierAgent(),
}
def get_agent(domain: str):
    return REGISTRY.get(domain, CivilAgent())
