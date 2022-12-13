# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp
import re

class URL(Regexp):
    def __init__(self, require_tld=True, message=None):
        tld_part = (require_tld and r'\.[a-z]{2,10}' or '')
        regex = r'([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?$' % tld_part
        super(URL, self).__init__(regex, re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('유효하지 않은 도메인입니다. (ex: naver.com)')
        super(URL, self).__call__(form, field)

class LoginForm(FlaskForm):
    domain = StringField('Domain Name (ex: naver.com)', validators=[URL()])
    submit = SubmitField('예측')
    virustotal = SubmitField('VirusTotal Query')
    prediction = 'legit'
    whois = False
    ip = False
    whoisIP = False

