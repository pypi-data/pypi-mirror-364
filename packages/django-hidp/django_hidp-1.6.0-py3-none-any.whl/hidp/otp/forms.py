from django_otp.forms import (
    OTPAuthenticationFormMixin as DjangoOTPAuthenticationFormMixin,
)
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from django import forms
from django.utils.translation import gettext_lazy as _

from hidp.otp.devices import get_device_for_user


class OTPAuthenticationFormMixin(DjangoOTPAuthenticationFormMixin):
    # Override/copy the error messages to be able to translate them in HIdP
    otp_error_messages = DjangoOTPAuthenticationFormMixin.otp_error_messages | {
        "invalid_token": _(
            "Invalid token. Please make sure you have entered it correctly."
        ),
    }


class OTPVerifyFormBase(OTPAuthenticationFormMixin, forms.Form):
    template_name = "hidp/otp/forms/otp_verify_form.html"

    # The device class to use for verification, e.g. TOTPDevice or StaticDevice.
    device_class = None

    @staticmethod
    def create_otp_token_field(label):
        """
        Create a form field for the OTP token.

        Args:
            label: Field label

        Returns:
            Configured CharField
        """
        attrs = {
            "autocomplete": "one-time-code",
            "inputmode": "numeric",
            "pattern": "[0-9]*",
        }

        return forms.CharField(
            widget=forms.TextInput(attrs=attrs),
            label=label,
            max_length=6,
        )

    @staticmethod
    def create_recovery_code_field(label):
        """
        Create a form field for the recovery code.

        Args:
            label: Field label

        Returns:
            Configured CharField
        """
        attrs = {
            "autocomplete": "off",
        }

        return forms.CharField(
            widget=forms.TextInput(attrs=attrs),
            label=label,
            max_length=8,
        )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

    def _chosen_device(self, user):
        return self.get_device(user)

    def get_device(self, user):
        return get_device_for_user(user, self.device_class)

    def clean(self):
        super().clean()

        self.clean_otp(self.user)

        return self.cleaned_data


class VerifyTOTPForm(OTPVerifyFormBase):
    """
    A form used to verify a TOTP token from an Authenticator App.

    This form is used to verify a TOTP token entered by the user. It will verify the
    token against the user's confirmed TOTP device.
    """

    device_class = TOTPDevice
    otp_token = OTPVerifyFormBase.create_otp_token_field(
        label=_("Enter the code from the app"),
    )


class VerifyStaticTokenForm(OTPVerifyFormBase):
    """
    A form used to verify a static token from a list of recovery codes.

    This form is used to verify a static token entered by the user. It will verify
    the token against the user's confirmed Static device.
    """

    device_class = StaticDevice
    otp_token = OTPVerifyFormBase.create_recovery_code_field(
        label=_("Enter a recovery code"),
    )


class OTPSetupForm(OTPVerifyFormBase):
    otp_token = OTPVerifyFormBase.create_otp_token_field(
        label=_("Enter the code from the app"),
    )
    confirm_stored_backup_tokens = forms.BooleanField(
        required=True,
        label=_("I have stored my backup codes in a safe place"),
        help_text=_(
            "You can use these codes to log in if you lose access to your device"
        ),
    )

    def get_device(self, user):
        """Hard-wire the unconfirmed device to verify against."""
        return self.device

    def __init__(self, *args, user, device, backup_device, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.device = device
        self.backup_device = backup_device

    def save(self):
        # Mark the devices as confirmed
        self.device.confirmed = True
        self.device.save(update_fields=["confirmed"])
        self.backup_device.confirmed = True
        self.backup_device.save(update_fields=["confirmed"])
