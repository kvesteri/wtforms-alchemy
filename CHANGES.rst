Changelog
=========

Here you can see the full list of changes between each WTForms-Alchemy release.

0.19.0 (2024-11-18)
^^^^^^^^^^^^^^^^^^^

- Dropped support for Python 3.8 and earlier. The minimum supported Python version is now 3.9.
- Dropped support for SQLAlchemy 1.3 and earlier. The minimum supported SQLAlchemy version is now 1.4.
- Added support for Python 3.10–3.13.
- Added support for SQLAlchemy 2.0.
- Added support for WTForms 3.2. The minimum supported WTForms version is now 3.1.

0.18.0 (2021-12-21)
^^^^^^^^^^^^^^^^^^^

- Dropped WTForms 1.0 support
- Added WTForms 3.0 and SA 1.4 support
- Dropped py35 support


0.17.0 (2020-06-02)
^^^^^^^^^^^^^^^^^^^

- Dropped py27, py33 and py34 support


0.16.9 (2019-03-06)
^^^^^^^^^^^^^^^^^^^

- Added support for JSON type in TypeMap (#142, pull request courtesy of fedExpress)


0.16.8 (2018-12-04)
^^^^^^^^^^^^^^^^^^^

- Fixed QuerySelectField.query allowing no results (#136, pull request courtesy of TrilceAC)


0.16.7 (2018-05-07)
^^^^^^^^^^^^^^^^^^^

- Fixed UnknownTypeException being thrown correctly for unsupported types (#131, pull request courtesy of tvuotila)


0.16.6 (2018-01-21)
^^^^^^^^^^^^^^^^^^^

- Added SQLAlchemy 1.2 support


0.16.5 (2017-07-29)
^^^^^^^^^^^^^^^^^^^

- Fixed GroupedQuerySelectMultipleField validator to support empty data (#123, pull request courtesy of superosku)


0.16.4 (2017-07-29)
^^^^^^^^^^^^^^^^^^^

- Fixed GroupedQuerySelectMultipleField validator (#121, pull request courtesy of superosku)


0.16.3 (2017-06-25)
^^^^^^^^^^^^^^^^^^^

- Fixed ChoiceType conversion for Enums (#112, pull request courtesy of fayazkhan)


0.16.2 (2017-02-28)
^^^^^^^^^^^^^^^^^^^

- Added GroupedQueryMultipleSelectField (#113, pull request courtesy of adarshk7)


0.16.1 (2016-05-11)
^^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-Utils requirement to 0.32.6
- Fixed PhoneNumberType conversion (#102)


0.16.0 (2016-04-20)
^^^^^^^^^^^^^^^^^^^

- Dropped python 2.6 support
- Made PhoneNumberField work correctly together with DataRequired (#101, pull request courtesy of jmagnusson)


0.15.0 (2016-01-27)
^^^^^^^^^^^^^^^^^^^

- Moved GroupedQuerySelectField from WTForms-Components package to WTForms-Alchemy
- Moved WeekdaysField from WTForms-Components package to WTForms-Alchemy
- Moved PhoneNumberField from WTForms-Components package to WTForms-Alchemy
- Moved Unique validator from WTForms-Components package to WTForms-Alchemy


0.14.0 (2016-01-23)
^^^^^^^^^^^^^^^^^^^

- Added QuerySelectField and QuerySelectMultipleField which were deprecated from
WTForms as of version 2.1


0.13.3 (2015-06-17)
^^^^^^^^^^^^^^^^^^^

- Removed ClassMap's inheritance sorting. This never really worked properly and resulted in weird undeterministic bugs on Python 3.


0.13.2 (2015-05-21)
^^^^^^^^^^^^^^^^^^^

- Added support for callables in type map argument


0.13.1 (2015-04-19)
^^^^^^^^^^^^^^^^^^^

- Added flake8 checks
- Added isort checks
- Fixed country import caused by SQLAlchemy-Utils 0.30.0
- Update SQLAlchemy-Utils dependency to 0.30.0


0.13.0 (2014-10-14)
^^^^^^^^^^^^^^^^^^^

- Made all default validators configurable in model_form_factory
- Added support for disabling default validators


0.12.9 (2014-08-30)
^^^^^^^^^^^^^^^^^^^

- Added support for composite primary keys in ModelFieldList


0.12.8 (2014-07-28)
^^^^^^^^^^^^^^^^^^^

- Added support for URLType of SQLAlchemy-Utils


0.12.7 (2014-07-21)
^^^^^^^^^^^^^^^^^^^

- Fix ModelFieldList handling of simultaneous deletes and updates


0.12.6 (2014-06-12)
^^^^^^^^^^^^^^^^^^^

- Fix various issues with new-style classes


0.12.5 (2014-05-29)
^^^^^^^^^^^^^^^^^^^

- Added CountryField
- Added CountryType to CountryField conversion
- Fixed various issues with column aliases


0.12.4 (2014-03-26)
^^^^^^^^^^^^^^^^^^^

- Added WeekDaysType to WeekDaysField conversion


0.12.3 (2014-03-24)
^^^^^^^^^^^^^^^^^^^

- Fixed ChoiceType coercion for SelectFields


0.12.2 (2014-02-20)
^^^^^^^^^^^^^^^^^^^

- New configuration option: attr_errors
- Min and max info attributes generate NumberRange validator for Numeric, Float, IntRangeType and NumericRangeType columns


0.12.1 (2014-02-13)
^^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-i18n optional dependency to 0.8.2


0.12.0 (2013-12-19)
^^^^^^^^^^^^^^^^^^^

- Added support for SQLAlchemy-Utils range types IntRange, NumericRange, DateRange and DateTimeRange
- Deprecated support for NumberRangeField
- Updated SQLAlchemy-Utils dependency to 0.23.1
- Updated WTForms-Components dependency to 0.9.0


0.11.0 (2013-12-19)
^^^^^^^^^^^^^^^^^^^

- Added configurable default validators
- Fixed ModelFieldList processing


0.10.0 (2013-12-16)
^^^^^^^^^^^^^^^^^^^

- Replaced assign_required configuration option with not_null_validator for more fine grained control of not null validation
- Replaced not_null_str_validator with not_null_validator_type_map


0.9.3 (2013-12-12)
^^^^^^^^^^^^^^^^^^

- Support for hybrid properties that return column properties
- Better exception messages for properties that are not of type ColumnProperty
- Support for class level type map customization


0.9.2 (2013-12-11)
^^^^^^^^^^^^^^^^^^

- Smarter object value inspection for ModelFieldList
- Changed ModelFieldList default population strategy to 'update' instead of 'replace'


0.9.1 (2013-12-03)
^^^^^^^^^^^^^^^^^^

- Fixed property alias handling (issue #46)


0.9.0 (2013-11-30)
^^^^^^^^^^^^^^^^^^

- Initial WTForms 2.0 support
- New configuration options: not_null_validator, not_null_str_validator


0.8.6 (2013-11-18)
^^^^^^^^^^^^^^^^^^

- Form fields now generated in class initialization time rather than on form object initialization


0.8.5 (2013-11-13)
^^^^^^^^^^^^^^^^^^

- Added Numeric type scale to DecimalField places conversion


0.8.4 (2013-11-11)
^^^^^^^^^^^^^^^^^^

- Declaration order of model fields now preserved in generated forms


0.8.3 (2013-10-28)
^^^^^^^^^^^^^^^^^^

- Added Python 2.6 support (supported versions now 2.6, 2.7 and 3.3)
- Enhanced coerce func generator


0.8.2 (2013-10-25)
^^^^^^^^^^^^^^^^^^

- TypeDecorator derived type support SelectField coerce callable generator


0.8.1 (2013-10-24)
^^^^^^^^^^^^^^^^^^

- Added support for SQLAlchemy-Utils ChoiceType
- Updated SQLAlchemy-Utils dependency to 0.18.0


0.8.0 (2013-10-11)
^^^^^^^^^^^^^^^^^^

- Fixed None value handling in string stripping when strip_string_fields option is enabled
- Python 3 support
- ModelFormMeta now configurable


0.7.15 (2013-09-06)
^^^^^^^^^^^^^^^^^^^

- Form generation now understands column aliases


0.7.14 (2013-08-27)
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
