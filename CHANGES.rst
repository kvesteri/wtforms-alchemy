Changelog
---------

Here you can see the full list of changes between each WTForms-Alchemy release.


0.7.13 (2013-08-27)
^^^^^^^^^^^^^^^^^^^

- Length validators only assigned to string typed columns


0.7.13 (2013-08-22)
^^^^^^^^^^^^^^^^^^^

- Model column_property methods now skipped in model generation process


0.7.12 (2013-08-18)
^^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-Utils dependency to 0.16.7
- Updated SQLAlchemy-i18n dependency to 0.6.3


0.7.11 (2013-08-05)
^^^^^^^^^^^^^^^^^^^

- Added configuration skip_unknown_types to silently skip columns with types WTForms-Alchemy does not understand


0.7.10 (2013-08-01)
^^^^^^^^^^^^^^^^^^^

- DecimalField with scales and choices now generate SelectField as expected


0.7.9 (2013-08-01)
^^^^^^^^^^^^^^^^^^

- TSVectorType columns excluded by default


0.7.8 (2013-07-31)
^^^^^^^^^^^^^^^^^^

- String typed columns now convert to WTForms-Components StringFields instead of WTForms TextFields


0.7.7 (2013-07-31)
^^^^^^^^^^^^^^^^^^

- HTML5 step widget param support added
- Updated WTForms-Components dependency to 0.6.6


0.7.6 (2013-07-24)
^^^^^^^^^^^^^^^^^^

- TypeDecorator support added


0.7.5 (2013-05-30)
^^^^^^^^^^^^^^^^^^

- Fixed _obj setting to better cope with wtforms_components unique validator


0.7.4 (2013-05-30)
^^^^^^^^^^^^^^^^^^

- Fixed min and max arg handling when using zero values


0.7.3 (2013-05-24)
^^^^^^^^^^^^^^^^^^

- Fixed ModelFieldList object population when using 'update' population strategy


0.7.2 (2013-05-24)
^^^^^^^^^^^^^^^^^^

- Updated WTForms-Components dependency to 0.6.3
- Made type conversion use WTForms-Components HTML5 fields


0.7.1 (2013-05-23)
^^^^^^^^^^^^^^^^^^

- DataRequired validator now added to not nullable booleans by default


0.7.0 (2013-05-14)
^^^^^^^^^^^^^^^^^^

- SQLAlchemy-i18n support added


0.6.0 (2013-05-07)
^^^^^^^^^^^^^^^^^^

- Updated WTForms dependency to 1.0.4
- Updated WTForms-Components dependency to 0.5.5
- EmailType now converts to HTML5 EmailField
- Integer now converts to HTML5 IntegerField
- Numeric now converts to HTML5 DecimalField
- Date now converts to HTML5 DateField
- DateTime now converts to HTML5 DateTimeField


0.5.7 (2013-05-03)
^^^^^^^^^^^^^^^^^^

- Fixed trim function for None values


0.5.6 (2013-05-02)
^^^^^^^^^^^^^^^^^^

- Column trim option added for fine-grained control of string field trimming


0.5.5 (2013-05-02)
^^^^^^^^^^^^^^^^^^

- Bug fix: strip_string_fields applied only for string fields


0.5.4 (2013-05-02)
^^^^^^^^^^^^^^^^^^

- Possibility to give default configuration for model_form_factory function
- strip_string_fields configuration option


0.5.3 (2013-04-30)
^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-Utils dependency to 0.10.0
- Updated WTForms-Components dependency to 0.5.4
- Added support for ColorType


0.5.2 (2013-04-25)
^^^^^^^^^^^^^^^^^^

- Added custom widget support
- Added custom filters support


0.5.1 (2013-04-16)
^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-Utils dependency to 0.9.1
- Updated WTForms-Components dependency to 0.5.2
- Fixed Email validator auto-assigning for EmailType
- Smarter type conversion for subclassed types
- Fixed ModelFormField update handling


0.5.0 (2013-04-12)
^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy dependency to 0.8
- Completely rewritten ModelFieldList implementation


0.4.5 (2013-03-27)
^^^^^^^^^^^^^^^^^^

- Updated WTForms-Components dependencies
- Updated docs


0.4.4 (2013-03-27)
^^^^^^^^^^^^^^^^^^

- Updated WTForms-Components and SQLAlchemy-Utils dependencies


0.4.3 (2013-03-26)
^^^^^^^^^^^^^^^^^^

- Disalbed length validation for PhoneNumberType


0.4.2 (2013-03-26)
^^^^^^^^^^^^^^^^^^

- Added conversion from NumberRangeType to NumberRangeField


0.4.1 (2013-03-21)
^^^^^^^^^^^^^^^^^^

- Added conversion from PhoneNumberType to PhoneNumberField


0.4 (2013-03-15)
^^^^^^^^^^^^^^^^

- Moved custome fields, validators and widgets to WTForms-Components package


0.3.3 (2013-03-14)
^^^^^^^^^^^^^^^^^^

- Added handling of form_field_class = None


0.3.2 (2013-03-14)
^^^^^^^^^^^^^^^^^^

- Added custom field class attribute


0.3.1 (2013-03-01)
^^^^^^^^^^^^^^^^^^

- Better exception messages


0.3.0 (2013-03-01)
^^^^^^^^^^^^^^^^^^

- New unique validator syntax


0.2.5 (2013-02-16)
^^^^^^^^^^^^^^^^^^

- API documentation


0.2.4 (2013-02-08)
^^^^^^^^^^^^^^^^^^

- Enhanced unique validator
- Documented new unique validator


0.2.3 (2012-11-26)
^^^^^^^^^^^^^^^^^^

- Another fix for empty choices handling


0.2.2 (2012-11-26)
^^^^^^^^^^^^^^^^^^

- Fixed empty choices handling for string fields


0.2.1 (2012-11-22)
^^^^^^^^^^^^^^^^^^

- If validator
- Chain validator


0.2 (2012-11-05)
^^^^^^^^^^^^^^^^^^

- DateRange validator
- SelectField with optgroup support


0.1.1
^^^^^

- Added smart one-to-one and one-to-many relationship population

0.1.0
^^^^^

- Initial public release
