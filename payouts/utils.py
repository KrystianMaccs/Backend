from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class TransferIdGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, artist_payout, timestamp):
        try:
            return (
                six.text_type(artist_payout.pk) + six.text_type(artist_payout.artist_id) +
                six.text_type(artist_payout.pay_due_id)
            )
        except:
            return (
                six.text_type(artist_payout.pk) + six.text_type(artist_payout.royalty_id) +
                six.text_type(artist_payout.pay_due_id)
            )


transfer_id_gen = TransferIdGenerator()

def get_trans_id(artist_payout):
    return f'gc_{transfer_id_gen.make_token(artist_payout)}'
