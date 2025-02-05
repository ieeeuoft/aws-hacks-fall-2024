from dateutil.relativedelta import relativedelta
import re

from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django_registration import validators
from django.conf import settings

from hackathon_site.utils import is_registration_open, is_hackathon_happening
from registration.models import Application, Team, User
from registration.widgets import MaterialFileInput
from review.models import Review


class SignUpForm(UserCreationForm):
    """
    Form for registering a new user account.

    Similar to django_registration's ``RegistrationForm``, but doesn't
    require a username field. Instead, email is a required field, and
    username is automatically set to be the email. This is ultimately
    simpler than creating a custom user model to use email as username.
    """

    captcha = ReCaptchaField(label="")
    error_css_class = "invalid"

    class Meta(UserCreationForm.Meta):
        fields = [
            User.get_email_field_name(),
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
        labels = {
            User.get_email_field_name(): _("UofT Email"),
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "password1": _("Password"),
            "password2": _("Confirm Password"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email_field = User.get_email_field_name()
        self.fields[email_field].validators.extend(
            (
                validators.HTML5EmailValidator(),
                validators.validate_confusables_email,
                validators.CaseInsensitiveUnique(
                    User, email_field, "This email is unavailable"
                ),
            )
        )
        self.label_suffix = ""

        # This overrides the default labels set by UserCreationForm
        for field, label in self._meta.labels.items():
            self.fields[field].label = label

        for field in self._meta.fields:
            self.fields[field].required = True

    def clean_email(self):
        cleaned_email = self.cleaned_data["email"].lower()
        if not cleaned_email.endswith("@mail.utoronto.ca"):
            raise forms.ValidationError(
                _("You must use your UofT email address to register."),
                code="invalid_email",
            )
        return cleaned_email

    def clean_first_name(self):
        if not bool(re.search("^[a-zA-Z0-9\-]*$", self.cleaned_data["first_name"])):
            raise forms.ValidationError(
                _(
                    f"This doesn't seem like a name, please enter a valid name (no special characters)"
                ),
                code="invalid_first_name",
            )

        if len(self.cleaned_data["first_name"]) > 30:
            raise forms.ValidationError(
                _(f"This input seems too long to be a name, please enter a valid name"),
                code="first_name_too_long",
            )
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        if not bool(re.search("^[a-zA-Z0-9]*$", self.cleaned_data["last_name"])):
            raise forms.ValidationError(
                _(
                    f"This doesn't seem like a name, please enter a valid name (no special characters)"
                ),
                code="invalid_last_name",
            )

        if len(self.cleaned_data["last_name"]) > 30:
            raise forms.ValidationError(
                _(f"This input seems too long to be a name, please enter a valid name"),
                code="last_name_too_long",
            )
        return self.cleaned_data["last_name"]

    def save(self, commit=True):
        """
        Set the user's username to their email when saving

        This is much simpler than the alternative of creating a
        custom user model without a username field, but a caveat
        nonetheless.
        """

        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ApplicationForm(forms.ModelForm):
    error_css_class = "invalid"

    class Meta:
        model = Application
        fields = [
            "age",
            "gender",
            "pronouns",
            "ethnicity",
            "dietary_restrictions",
            "specific_dietary_requirement",
            "street_address",
            "apt_number",
            "country",
            "city",
            "region",
            "postal_code",
            "student_number",
            "phone_number",
            "study_level",
            "program",
            "graduation_year",
            "resume",
            "linkedin",
            "github",
            "devpost",
            "why_participate",
            "what_technical_experience",
            "discovery_method",
            "underrepresented_community",
            "sexual_orientation",
            "resume_sharing",
            "conduct_agree",
        ]
        widgets = {
            "student_number": forms.TextInput(attrs={"placeholder": "1234567890"}),
            "graduation_year": forms.NumberInput(attrs={"placeholder": 2024}),
            "resume": MaterialFileInput(attrs={"accept": ".pdf"}),
            "why_participate": forms.Textarea(
                attrs={
                    "class": "materialize-textarea",
                    "placeholder": "I want to participate in Hack The Student Life because...",
                    "data-length": 1000,
                }
            ),
            "what_technical_experience": forms.Textarea(
                attrs={
                    "class": "materialize-textarea",
                    "placeholder": "My technical experience includes...",
                    "data-length": 1000,
                }
            ),
            # Additional widgets can be defined here for other fields as needed.
            "phone_number": forms.TextInput(attrs={"placeholder": "+1 (123) 456-7890"}),
            "graduation_year": forms.NumberInput(attrs={"placeholder": 2024}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["conduct_agree"].required = True

    def clean(self):
        if not is_registration_open():
            raise forms.ValidationError(
                _("Registration has closed."), code="registration_closed"
            )

        cleaned_data = super().clean()
        if hasattr(self.user, "application"):
            raise forms.ValidationError(
                _("User has already submitted an application."), code="invalid"
            )
        return cleaned_data

    def clean_student_number(self):
        student_number = self.cleaned_data.get("student_number")
        if not student_number.isdigit() or len(student_number) != 10:
            raise forms.ValidationError("Student number must be exactly 10 digits.")
        return student_number

    # Include any other custom validation methods as necessary.
    def clean_age(self):
        user_age = self.cleaned_data["age"]
        # Check if the age is "22+"
        if user_age == "22+":
            return user_age
        if int(user_age) < settings.MINIMUM_AGE:
            raise forms.ValidationError(
                _(f"You must be {settings.MINIMUM_AGE} to participate."),
                code="user_is_too_young_to_participate",
            )
        return user_age

    def save(self, commit=True):
        self.instance = super().save(commit=False)
        team = Team.objects.create()

        self.instance.user = self.user
        self.instance.team = team
        self.instance.phone_number = re.sub("[^0-9]", "", self.instance.phone_number)

        if commit:
            self.instance.save()
            self.save_m2m()

        return self.instance


class JoinTeamForm(forms.Form):
    team_code = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.error_css_class = "invalid"

    def clean(self):
        if not is_registration_open():
            raise forms.ValidationError(
                _("You cannot change teams after registration has closed."),
                code="registration_closed",
            )

        return super().clean()

    def clean_team_code(self):
        team_code = self.cleaned_data["team_code"]

        try:
            team = Team.objects.get(team_code=team_code)
        except Team.DoesNotExist:
            raise forms.ValidationError(_(f"Team {team_code} does not exist."))

        if team.applications.count() >= Team.MAX_MEMBERS:
            raise forms.ValidationError(_(f"Team {team_code} is full."))

        return team_code


class SignInForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.error_css_class = "invalid"

    def clean(self):
        if not is_hackathon_happening():
            raise forms.ValidationError(
                _("You cannot sign in outside of the hackathon period."),
                code="invalid_sign_in_time",
            )

        return super().clean()

    def clean_email(self):
        email = self.cleaned_data["email"]

        try:
            user = User.objects.get(email__exact=email)
            application = Application.objects.get(user__exact=user)
            try:
                review = Review.objects.get(application__exact=application)
            except Review.DoesNotExist:
                raise forms.ValidationError(_(f"User {email} was not reviewed."))
            if review.status == "Accepted":
                if settings.RSVP and application.rsvp is None:
                    raise forms.ValidationError(
                        _(f"User {email} has not RSVP'd to the hackathon")
                    )
            else:
                raise forms.ValidationError(
                    _(
                        f"User {email} has not been Accepted to attend {settings.HACKATHON_NAME}"
                    )
                )
        except User.DoesNotExist:
            raise forms.ValidationError(_(f"User {email} does not exist."))
        except Application.DoesNotExist:
            raise forms.ValidationError(
                _(f"User {email} has not applied to {settings.HACKATHON_NAME}")
            )
        except Exception as e:
            raise e

        return email
