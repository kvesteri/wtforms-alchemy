import pytest
from wtforms import Form

from tests import MultiDict
from wtforms_alchemy import DataRequired, PhoneNumberField


class TestPhoneNumberField(object):
    def setup_method(self, method):
        self.valid_phone_numbers = [
            '040 1234567',
            '+358 401234567',
            '09 2501234',
            '+358 92501234',
            '0800 939393',
            '09 4243 0456',
            '0600 900 500'
        ]
        self.invalid_phone_numbers = [
            'abc',
            '+040 1234567',
            '0111234567',
            '358'
        ]

    def init_form(self, **kwargs):
        class TestForm(Form):
            phone_number = PhoneNumberField(**kwargs)
        return TestForm

    def test_valid_phone_numbers(self):
        form_class = self.init_form(region='FI')
        for phone_number in self.valid_phone_numbers:
            form = form_class(MultiDict(phone_number=phone_number))
            form.validate()
            assert len(form.errors) == 0

    def test_invalid_phone_numbers(self):
        form_class = self.init_form(region='FI')
        for phone_number in self.invalid_phone_numbers:
            form = form_class(MultiDict(phone_number=phone_number))
            form.validate()
            assert len(form.errors['phone_number']) == 1

    def test_render_empty_phone_number_value(self):
        form_class = self.init_form(region='FI')
        form = form_class(MultiDict(phone_number=''))
        assert 'value=""' in form.phone_number()

    def test_empty_phone_number_value_passed_as_none(self):
        form_class = self.init_form(region='FI')
        form = form_class(MultiDict(phone_number=''))
        form.validate()
        assert len(form.errors) == 0
        assert form.data['phone_number'] is None

    def test_default_display_format(self):
        form_class = self.init_form(region='FI')
        form = form_class(MultiDict(phone_number='+358401234567'))
        assert 'value="040 1234567"' in form.phone_number()

    def test_international_display_format(self):
        form_class = self.init_form(
            region='FI',
            display_format='international'
        )
        form = form_class(MultiDict(phone_number='0401234567'))
        assert 'value="+358 40 1234567"' in form.phone_number()

    def test_e164_display_format(self):
        form_class = self.init_form(
            region='FI',
            display_format='e164'
        )
        form = form_class(MultiDict(phone_number='0401234567'))
        assert 'value="+358401234567"' in form.phone_number()

    def test_field_rendering_when_invalid_phone_number(self):
        form_class = self.init_form()
        form = form_class(MultiDict(phone_number='invalid'))
        form.validate()
        assert 'value="invalid"' in form.phone_number()

    @pytest.mark.parametrize(
        'number,error_msg,check_value',
        (
            (
                '',
                'This field is required.',
                lambda v, orig: v is None
            ),
            (
                '1',
                'Not a valid phone number value',
                lambda v, orig: v is not None
            ),
            (
                '123',
                'Not a valid phone number value',
                lambda v, orig: v is not None
            ),
            (
                '+46123456789',
                None,
                lambda v, orig: v.e164 == orig
            ),
        )
    )
    def test_required_phone_number_form(self, number, error_msg, check_value):
        class PhoneNumberForm(Form):
            phone = PhoneNumberField(
                'Phone number',
                validators=[DataRequired()]
            )

        form = PhoneNumberForm(MultiDict(
            phone=number
        ))
        form.validate()
        if error_msg:
            assert len(form.errors) == 1
            assert form.errors['phone'][0] == error_msg
        else:
            assert len(form.errors) == 0
        assert check_value(form.phone.data, number) is True
