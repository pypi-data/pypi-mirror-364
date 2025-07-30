from portone_server_sdk import IdentityVerificationClient, PaymentClient
from portone_server_sdk.common import (
    CustomerInput,
    CustomerNameInput,
    PaymentAmountInput,
    PaymentProduct,
)

client = PaymentClient(
    secret="SO7zNSqMpnjbqf7cdbJf3MS5cIJG0EvfTCrGO4pNqYdFvebnStD9UTiWkaZyRCZdYysVz7XKoykugx8l",
)
iv_client = IdentityVerificationClient(
    secret="SO7zNSqMpnjbqf7cdbJf3MS5cIJG0EvfTCrGO4pNqYdFvebnStD9UTiWkaZyRCZdYysVz7XKoykugx8l"
)

try:
    print(
        client.pay_with_billing_key(
            payment_id="fj983hs",
            billing_key="billing-key-019830e4-3574-3bbd-f16b-ff39ffdd6d2e",
            order_name="Portone Test",
            customer=CustomerInput(
                name=CustomerNameInput(full="PortOne"), email="kiwiyou@portone.io"
            ),
            products=[
                PaymentProduct(
                    id="1", name="a", amount=100, quantity=1, link="https://example.com"
                ),
            ],
            amount=PaymentAmountInput(total=100),
            currency="USD",
            locale="EN_US",
        )
    )
except Exception as e:
    print(e)

payment_id = "fj983hs"
res = client.get_payment(payment_id=payment_id)
print(res)
