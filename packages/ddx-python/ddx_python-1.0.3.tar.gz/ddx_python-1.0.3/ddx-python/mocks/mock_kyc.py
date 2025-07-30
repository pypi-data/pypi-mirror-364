from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/api/v3/brokerage/payment_methods/<id>", methods=["GET"])
    def get_payment_method(id):
        # TODO: verify the jwt token in the header
        response = {
            "payment_method": {
                "id": id,
                "currency": "USD",
                "verified": True,
                "allow_buy": True,
                "allow_sell": True,
                "allow_deposit": True,
                "allow_withdraw": True,
            }
        }
        return jsonify(response)

    @app.route("/kyc/1.0/connect/beta_derivadex_b7fc6/recordId/<id>", methods=["GET"])
    # Use Alice's address for testing
    def get_kyc_status(id):
        # convert id as hex string into bytes
        id_bytes = bytes.fromhex(id)
        # convert bytes to int
        id_int = int.from_bytes(id_bytes, "big")
        # if id_int is even, return approved, otherwise return blocked
        if id_int % 2 == 0:
            status = "approved"
            response = {
                "data": {
                    "recordId": id,
                    "status": status,
                    "isArchived": False,
                    "identities": {
                        "crypto_address_eth": {
                            "type": "String",
                            "value": "0xA8dDa8d7F5310E4A9E24F8eBA77E091Ac264f872",
                        },
                        "email": {"type": "String", "value": "test@example.com"},
                    },
                }
            }
        else:
            status = "blocked"
            response = {
                "data": {
                    "recordId": id,
                    "status": status,
                    "isArchived": True,
                }
            }
        return jsonify(response)

    return app


if __name__ == "__main__":
    print("Running SSL-enabled mock KYC server")
    app = create_app()
    app.run(host="0.0.0.0", ssl_context=("test_kyc.crt", "test_kyc.key"))
else:
    print("Creating gunicorn app for mock KYC server")
    gunicorn_app = create_app()
