from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PaymentBeneficiaryDetails:
    beneficiary_name: str
    beneficiary_email: str
    beneficiary_phone: str
    beneficiary_country: str = "IN"
    beneficiary_postcode: str = "560076"


@dataclass_json
@dataclass
class PaymentInitiateTransactionDataClass:
    transfer_amount: float
    beneficiary_details: PaymentBeneficiaryDetails