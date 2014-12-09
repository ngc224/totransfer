#!/usr/bin/env python
# -*- coding:utf-8 -*-

from clint import textui
import sys, os, argparse, ConfigParser, requests, keyring, feedparser
import config as sys_config


class ToTranslator():
    def __init__(self):
        self._response = None

    def request(self, access_key, text, lang_from, lang_to):
        self._response = requests.post(
            sys_config.api_request_url,
            params={'Text': "'%s'" % text, 'To': "'%s'" % lang_to, 'From': "'%s'" % lang_from},
            auth=(access_key, access_key)
        )
        if not self.isStatusCode(self._response.status_code):
            raise
        return self

    def parse(self):
        for e in feedparser.parse(self._response.text)['entries']:
            return e['m_properties_detail']['value']

    @staticmethod
    def isStatusCode(code):
        return code == 200

    @staticmethod
    def isLang(lang):
        return lang in ToTranslator.getLangList()

    @staticmethod
    def getLangList():
        return ['ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'he', 'hi', 'ht', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'ms', 'mww', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'ur', 'vi', 'zh-CHS', 'zh-CHT']


class UserConfig():
    def __init__(self, filepath):
        self.filepath = filepath
        self.user_config = ConfigParser.SafeConfigParser()
        try:
            if not os.path.isfile(self.filepath):
                raise IOError(self.filepath)
        except:
            user_config = ConfigParser.RawConfigParser()
            user_config.add_section(sys_config.application_name)
            user_config.set(sys_config.application_name, 'From', '')
            user_config.set(sys_config.application_name, 'To', '')
            with open(self.filepath, 'wb') as configfile:
                user_config.write(configfile)
                os.chmod(self.filepath, 0644)
        self.user_config.read(self.filepath)

    def getUserOption(self, option):
        if self.user_config.has_option(sys_config.application_name, option):
            return self.user_config.get(sys_config.application_name, option)

    def setAccessKey(self):
        print(textui.colored.green('Get Evernote DeveloperToken URL --> '))
        while True:
            access_key = raw_input('Access key: ')
            if self.isAccessKey(access_key):
                keyring.set_password(sys_config.application_name, 'access_key', access_key)
                return self

    @staticmethod
    def getAccessKey():
        return keyring.get_password(sys_config.application_name, 'access_key')

    @staticmethod
    def isAccessKey(access_key):
        try:
            ToTranslator().request(access_key, 'test', 'en', 'ja')
        except:
            print(textui.colored.red('Token can not be used'))
            return False
        return True

    def setFromLang(self):
        print(textui.colored.green('Set totranslator default post tags / Not enter if you do not set'))
        self.user_config.set(sys_config.application_name, 'fromlang', raw_input('From lang: '))
        return self

    def setToLang(self):
        print(textui.colored.green('Set totranslator default post notebook / Not enter if you do not set'))
        self.user_config.set(sys_config.application_name, 'tolang', raw_input('To lang: '))
        return self

    def save(self):
        self.user_config.write(open(self.filepath, 'w'))


def main():
    parser = argparse.ArgumentParser(description=sys_config.application_name + ' version ' + sys_config.version)
    parser.add_argument('file', nargs='?', action='store', help='file to send to evernote')
    parser.add_argument('-f', '--fromlang', type=str, help='note attachment file name')
    parser.add_argument('-t', '--tolang', type=str, help='note title (omitted, the time is inputted automatically.)')
    parser.add_argument('-l', '--list', action='store_true', help='note attachment file name')
    parser.add_argument('--config', action='store_true', help='set user config')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + sys_config.version)

    args = parser.parse_args()

    if args.list:
        for lang in ToTranslator.getLangList():
            print lang
        return 0

    user_config = UserConfig(sys_config.filepath_user)

    if args.config:
        try:
            user_config.setAccessKey().setFromLang().setToLang().save()
        except:
            return 1
        return 0

    stdin_dafault = sys.stdin
    sys.stdin = open('/dev/tty', 'rt')
    if not user_config.isAccessKey(keyring.get_password(sys_config.application_name, 'access_key')):
        user_config.setAccessKey()
    sys.stdin = stdin_dafault

    totranslator = ToTranslator()

    if not args.fromlang and user_config.getUserOption('fromlang'):
        args.fromlang = user_config.getUserOption('fromlang')
    if not ToTranslator().isLang(args.fromlang):
        return "error set from lang"

    if not args.tolang and user_config.getUserOption('tolang'):
        args.tolang = user_config.getUserOption('tolang')
    if not ToTranslator().isLang(args.tolang):
        return "error set to lang"

    try:
        for line in iter(sys.stdin.readline, ''):
            print(textui.colored.green(
                totranslator.request(UserConfig.getAccessKey(), line, args.fromlang, args.tolang).parse()
            ))
    except:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
