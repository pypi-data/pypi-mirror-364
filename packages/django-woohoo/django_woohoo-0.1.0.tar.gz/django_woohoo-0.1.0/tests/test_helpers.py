from django.test import TestCase
from django_woohoo.helpers import AmazonCouponClient
from django_woohoo.dataclasses import PaymentInitiateTransactionDataClass, PaymentBeneficiaryDetails
from django.contrib.auth import get_user_model

class WoohooHelperTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.helper = AmazonCouponClient(self.user)

    def test_process_amount(self):
        data = PaymentInitiateTransactionDataClass(
            transfer_amount=100,
            beneficiary_details=PaymentBeneficiaryDetails(
                beneficiary_name="Sarthak",
                beneficiary_email="sarthaksnh5@gmail.com",
                beneficiary_phone="+919056317518"
            )
        )
        status, response = self.helper.process_amount(data, "CLAIMCODE")
        self.assertEqual(status, 200)
